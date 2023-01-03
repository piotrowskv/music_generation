import copy
import numpy as np

from typing import *
from music21 import *
try:
    from decode import get_sequence_of_notes, export_tempo_array
except ImportError:
    from .decode import get_sequence_of_notes, export_tempo_array


def check_number_of_tracks(array: list[list[Tuple[int, list[int]]]],
                           number: int) -> None:
    """
    checks if number of tracks equals an expected value: if not, raises a ValueError

    :param array:
    :param number:
    :return:
    """
    if len(array) != number:
        raise Warning('number of tracks ({}) not matching the expected value ({})'
                      .format(len(array), number))


def get_event_lists(array: list[list[Tuple[int, list[int]]]]) -> Tuple[list[list[list[int]]], list[int]]:
    """
    translates a multi-track array representing notes into a list of events with active notes
    
    :param array: 
    :return: 
    """
    array = copy.deepcopy(array)
    events: list[list[list[int]]] = [[] for _ in range(len(array))]
    tuples = dict[int, Tuple[int, list[int]]]()
    # tuples: list[Tuple[int, list[int]]] = [] * len(array)
    lengths = list[int]()

    active_range = range(len(array))
    active_tracks: list[int] = list(active_range)
    to_remove: list[int] = []
    removed_tracks: list[int] = []

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
        d: list[int] = [tuples[i][0] for i in active_tracks]
        diff = min(d)
        lengths.append(diff)
        # events[len(array)].append(diff)

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

    return events, lengths


def insert_meta_features(partial_features: list[list[float]],
                         event_lengths: list[int],
                         tempos: list[int]) -> list[list[float]]:
    """
    processes arrays of tempos and events' lengths,
    then adds two rows of respective features to already existing list of features
    
    :param partial_features:
    :param event_lengths: 
    :param tempos: 
    :return: 
    """
    partial_features = copy.deepcopy(partial_features)
    partial_features.append(list[float]())
    partial_features.append(list[float]())

    event_lengths = copy.deepcopy(event_lengths)
    offset = 0
    while len(event_lengths) > 0:
        state = event_lengths.pop(0)
        partial_features[-2].append(1 / state)  # lengths 1/x
        partial_features[-1].append(min(1.0, 1000 / tempos[offset]))  # tempos 1000/x
        offset += state

    return partial_features


def preprocess_features(filepath: str,
                        check_tracks: bool = False,
                        number_of_tracks: int = 0) -> Tuple[list[list[list[int]]], list[int], list[int]]:
    """
    gets a tempo array and a list of events from a MIDI file,
    optionally checks if number of tracks matches an expected value

    :param filepath:
    :param check_tracks:
    :param number_of_tracks:
    :return:
    """
    file_input = get_sequence_of_notes(filepath, False, False, True)

    if check_tracks:
        check_number_of_tracks(file_input, number_of_tracks)
    tempo_array = export_tempo_array(filepath, True)
    event_lists, event_lengths = get_event_lists(file_input)

    return event_lists, event_lengths, tempo_array


def get_list_of_tonal_features(events: list[list[list[int]]],
                               lengths: list[int],
                               tempos: list[int]) -> list[list[float]]:

    """
    calculates the most significant note in each track for every event,
    translates a list of events and tempos into an array of normalised tonal features of notes (octave and tone)

    :param events:
    :param lengths:
    :param tempos:
    :return:
    """
    events = copy.deepcopy(events)
    features_list: list[list[float]]
    features_list = [[] for _ in range(2 * len(events))]
    for track in range(len(events)):
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
                ch_root = ch.root().midi
                features_list[2 * track + 0].append((ch_root // 12 + 1) / 11)  # octaves /11
                features_list[2 * track + 1].append((ch_root % 12 + 1) / 12)  # tones /12

    output_features = insert_meta_features(features_list, lengths, tempos)
    return output_features


def get_list_of_midi_features(events: list[list[list[int]]],
                              lengths: list[int],
                              tempos: list[int]) -> list[list[float]]:
    """
    calculates the most significant note in each track for every event,
    translates a list of events and tempos into an array of normalised MIDI notes' features

    :param events:
    :param lengths:
    :param tempos:
    :return:
    """
    events = copy.deepcopy(events)
    features_list: list[list[float]]
    features_list = [[] for _ in range(len(events))]
    for track in range(len(events)):
        while len(events[track]) > 0:
            state = events[track].pop(0)

            if len(state) == 0:
                features_list[track].append(0.0)
            elif len(state) == 1:
                # features' notes numeration does not match MIDI (actual) notes to avoid non-positive (0) value
                features_list[track].append((state[0] + 1) / 128)  # notes /128
            else:
                ch = chord.Chord(state)
                ch_root = ch.root().midi
                features_list[track].append((ch_root + 1) / 128)  # notes /128

    output_features = insert_meta_features(features_list, lengths, tempos)
    return output_features


def get_midi_features(filepath: str,
                      check_tracks: bool = False,
                      number_of_tracks: int = 0) -> np.ndarray:
    """
    gets an array of MIDI notes' features from a MIDI file

    :param filepath:
    :param check_tracks:
    :param number_of_tracks:
    :return:
    """
    event_lists, event_lengths, tempo_array = preprocess_features(filepath, check_tracks, number_of_tracks)
    feature_list = get_list_of_midi_features(event_lists, event_lengths, tempo_array)
    feature_array = np.asarray(feature_list)
    feature_array = np.transpose(feature_array)

    return feature_array


def get_tonal_features(filepath: str,
                       check_tracks: bool = False,
                       number_of_tracks: int = 0) -> np.ndarray:
    """
    gets an array of tonal features of notes (octave and tone) from a MIDI file

    :param filepath:
    :param check_tracks:
    :param number_of_tracks:
    :return:
    """
    event_lists, event_lengths, tempo_array = preprocess_features(filepath, check_tracks, number_of_tracks)
    feature_list = get_list_of_tonal_features(event_lists, event_lengths, tempo_array)
    feature_array = np.asarray(feature_list)
    feature_array = np.transpose(feature_array)

    return feature_array


if __name__ == '__main__':
    from decode import get_filename, export_output

    # for name in os.listdir('../../data'):
    #     path = os.path.join('../../data', name)

    try:
        # features_array = \
        #     get_midi_features('../tests/test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid')
        features_array = \
            get_tonal_features('../tests/test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid')

        export_output('', get_filename('../tests/test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid'),
                      features_array)

    except Exception as ex:
        print(ex)
