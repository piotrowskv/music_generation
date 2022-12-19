import os

from music21 import *

from midi.decode import (Mode, export_output, export_tempo_array, get_filename,
                         get_sequence_of_notes)

NO_TRACKS = 3


def get_event_lists(f):
    events = [[] for _ in range(len(f) + 1)]
    tuples = [None] * len(f)

    active_tracks = range(len(f))
    active_tracks = list(active_tracks)
    to_remove = []
    removed_tracks = []

    for track in active_tracks:
        if len(f[track]) > 0:
            tuples[track] = f[track].pop(0)
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
        events[len(f)].append(diff)

        for track in active_tracks:
            events[track].append(tuples[track][1])
            tuples[track] = (tuples[track][0] - diff, tuples[track][1])

            while tuples[track][0] == 0:
                if len(f[track]) == 0:
                    to_remove.append(track)
                    break
                else:
                    tuples[track] = f[track].pop(0)

        for track in removed_tracks:
            events[track].append([])

        for track in to_remove:
            active_tracks.remove(track)
            removed_tracks.append(track)
        to_remove.clear()

    return events


def insert_meta_features(partial_features, events, tempos):
    offset = 0
    while len(events[-1]) > 0:
        state = events[-1].pop(0)
        partial_features[-2].append(1 / state)  # lengths mapping 1/x
        partial_features[-1].append(min(1.0, 1000 / tempos[offset]))  # tempos mapping 1000/x
        offset += state

    return partial_features


# VERSION WITH OCTAVE/TONE
def get_tonal_midi_features(events, tempos):
    features = [[] for _ in range(2 * len(events))]
    for track in range(len(events) - 1):
        while len(events[track]) > 0:
            state = events[track].pop(0)

            if len(state) == 0:
                features[2 * track + 0].append(0.0)
                features[2 * track + 1].append(0.0)
            elif len(state) == 1:
                features[2 * track + 0].append(max(0.0, min(1.0, (state[0] // 12 - 1) / 8)))  # octaves mapping x/8
                features[2 * track + 1].append((state[0] % 12 + 1) / 12)  # tones mapping x/12
            else:
                ch = chord.Chord(state)
                ch = ch.root().midi
                features[2 * track + 0].append(max(0.0, min(1.0, (ch // 12 - 1) / 8)))
                features[2 * track + 1].append((ch % 12 + 1) / 12)

    features = insert_meta_features(features, events, tempos)
    return features


# VERSION WITH MIDI NOTE
def get_raw_midi_features(events, tempos):
    features = [[] for _ in range(len(events) + 1)]
    for track in range(len(events) - 1):
        while len(events[track]) > 0:
            state = events[track].pop(0)

            if len(state) == 0:
                features[track].append(0.0)
            elif len(state) == 1:
                features[track].append(state[0] / 128)  # notes mapping x/128
            else:
                ch = chord.Chord(state)
                ch = ch.root().midi
                features[track].append(ch / 128)

    features = insert_meta_features(features, events, tempos)
    return features


def check_number_of_tracks(f, filename):
    if len(f) != NO_TRACKS:
        raise ValueError('number of tracks ({}) in {} not matching the expected value ({})'
                         .format(len(f), filename, NO_TRACKS))


def get_features(filepath, filename):  # TODO: add a mode switcher
    # file_input = np.load(filepath, allow_pickle=True)
    # file_input = file_input.tolist()
    file_input = get_sequence_of_notes(filepath, Mode.BOOLEANS, False, True)

    check_number_of_tracks(file_input, filename)
    tempo_array = export_tempo_array(filepath)
    event_lists = get_event_lists(file_input)

    # feature_list = get_tonal_midi_features(event_lists, tempo_array)
    feature_list = get_raw_midi_features(event_lists, tempo_array)

    return feature_list


if __name__ == '__main__':
    for name in os.listdir('../data'):
        path = os.path.join('../data', name)

        try:
            features = get_features(path, name)
            export_output('../sequences', get_filename(path), features)

        except Exception as ex:
            print(ex)
