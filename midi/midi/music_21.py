import numpy as np

from music21 import *
try:
    from decode import get_sequence_of_notes, export_tempo_array
except ImportError:
    from .decode import get_sequence_of_notes, export_tempo_array


def check_number_of_tracks(array, filename, number):
    """
    checks if number of tracks equals an expected value: if not, raises a ValueError

    :param array:
    :param filename:
    :param number:
    :return:
    """
    if len(array) != number:
        raise ValueError('number of tracks ({}) in {} not matching the expected value ({})'
                         .format(len(array), filename, number))


def get_event_lists(array):
    """
    translates a multi-track array representing notes into a list of events with active notes
    
    :param array: 
    :return: 
    """
    events = [[] for _ in range(len(array) + 1)]
    tuples = [None] * len(array)

    active_tracks = range(len(array))
    active_tracks = list(active_tracks)
    to_remove = []
    removed_tracks = []

    for track in active_tracks:
        if len(array[track]) > 0:
            tuples[track] = array[track].pop(0)
        else:
            to_remove.append(track)
            # active_tracks.remove(track)

    for track in to_remove:
        active_tracks.remove(track)
        removed_tracks.append(track)
    to_remove.clear()

    while len(active_tracks) > 0:
        d = [tuples[i][0] for i in active_tracks]
        diff = min(d)
        events[len(array)].append(diff)

        for track in active_tracks:
            events[track].append(tuples[track][1])
            tuples[track] = (tuples[track][0] - diff, tuples[track][1])

            while tuples[track][0] == 0:
                if len(array[track]) == 0:
                    to_remove.append(track)
                    break
                else:
                    tuples[track] = array[track].pop(0)

        for track in removed_tracks:
            events[track].append([])

        for track in to_remove:
            active_tracks.remove(track)
            removed_tracks.append(track)
        to_remove.clear()

    return events


def insert_meta_features(partial_features, event_lengths, tempos):
    """
    processes arrays of tempos and events' lengths,
    then adds two rows of respective features to already existing list of features
    
    :param partial_features: 
    :param event_lengths: 
    :param tempos: 
    :return: 
    """
    offset = 0
    while len(event_lengths[-1]) > 0:
        state = event_lengths[-1].pop(0)
        partial_features[-2].append(1 / state)  # lengths 1/x
        partial_features[-1].append(min(1.0, 1000 / tempos[offset]))  # tempos 1000/x
        offset += state

    return partial_features


def preprocess_features(filepath, filename, check_tracks=False, number_of_tracks=0):
    """
    gets a tempo array and a list of events from a MIDI file,
    optionally checks if number of tracks matches an expected value

    :param filepath:
    :param filename:
    :param check_tracks:
    :param number_of_tracks:
    :return:
    """
    # file_input = np.load(filepath, allow_pickle=True)  # TODO: choose input method
    # file_input = file_input.tolist()
    file_input = get_sequence_of_notes(filepath, False, False, True)

    if check_tracks:
        check_number_of_tracks(file_input, filename, number_of_tracks)
    tempo_array = export_tempo_array(filepath, True)
    event_lists = get_event_lists(file_input)

    return event_lists, tempo_array


def get_list_of_tonal_features(events, tempos):
    """
    calculates the most significant note in each track for every event,
    translates a list of events and tempos into an array of normalised tonal features of notes (octave and tone)

    :param events:
    :param tempos:
    :return:
    """
    features_list = [[] for _ in range(2 * len(events))]
    for track in range(len(events) - 1):
        while len(events[track]) > 0:
            state = events[track].pop(0)

            if len(state) == 0:
                features_list[2 * track + 0].append(0.0)
                features_list[2 * track + 1].append(0.0)
            elif len(state) == 1:
                # features' octave numeration does not match EventNote (actual) octaves to avoid non-positive values
                features_list[2 * track + 0].append((state[0] // 12 + 1) / 11)  # octaves /11
                features_list[2 * track + 1].append((state[0] % 12 + 1) / 12)  # tones /12
            else:
                ch = chord.Chord(state)
                ch = ch.root().midi
                features_list[2 * track + 0].append((ch // 12 + 1) / 11)  # octaves /11
                features_list[2 * track + 1].append((ch % 12 + 1) / 12)  # tones /12

    features_list = insert_meta_features(features_list, events, tempos)
    return features_list


def get_list_of_midi_features(events, tempos):
    """
    calculates the most significant note in each track for every event,
    translates a list of events and tempos into an array of normalised MIDI notes' features

    :param events:
    :param tempos:
    :return:
    """
    features_list = [[] for _ in range(len(events) + 1)]
    for track in range(len(events) - 1):
        while len(events[track]) > 0:
            state = events[track].pop(0)

            if len(state) == 0:
                features_list[track].append(0.0)
            elif len(state) == 1:
                # features' notes numeration does not match MIDI (actual) notes to avoid non-positive (0) value
                features_list[track].append((state[0] + 1) / 128)  # notes /128
            else:
                ch = chord.Chord(state)
                ch = ch.root().midi
                features_list[track].append((ch + 1) / 128)  # notes /128

    features_list = insert_meta_features(features_list, events, tempos)
    return features_list


def get_midi_features(filepath, filename, check_tracks=False, number_of_tracks=0):
    """
    gets an array of MIDI notes' features from a MIDI file

    :param filepath:
    :param filename:
    :param check_tracks:
    :param number_of_tracks:
    :return:
    """
    event_lists, tempo_array = preprocess_features(filepath, filename, check_tracks, number_of_tracks)
    feature_list = get_list_of_midi_features(event_lists, tempo_array)
    feature_list = np.asarray(feature_list)
    feature_list = np.transpose(feature_list)

    return feature_list


def get_tonal_features(filepath, filename, check_tracks=False, number_of_tracks=0):
    """
    gets an array of tonal features of notes (octave and tone) from a MIDI file

    :param filepath:
    :param filename:
    :param check_tracks:
    :param number_of_tracks:
    :return:
    """
    event_lists, tempo_array = preprocess_features(filepath, filename, check_tracks, number_of_tracks)
    feature_list = get_list_of_tonal_features(event_lists, tempo_array)
    feature_list = np.asarray(feature_list)
    feature_list = np.transpose(feature_list)

    return feature_list


if __name__ == '__main__':
    import os
    from decode import get_filename, export_output

    for name in os.listdir('../../data'):
        path = os.path.join('../../data', name)

        try:
            features_array = get_midi_features(path, name)
            # features_array = get_tonal_features(path, name)

            export_output('../../sequences', get_filename(path), features_array)

        except Exception as ex:
            print(ex)
