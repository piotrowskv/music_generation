import copy

import pytest

from midi.music_21 import *

# one-time setup
file1_path = 'files/test_all_notes.mid'
file2_path = 'files/test_tempos_velocities_and_polyphony.mid'

output_1m_path = 'files/music21_output_1m.npy'
output_1t_path = 'files/music21_output_1t.npy'
output_2m_path = 'files/music21_output_2m.npy'
output_2t_path = 'files/music21_output_2t.npy'

input_list = [[(8, [80]), (8, [79]), (8, [77]), (8, [76]), (8, [77]), (8, [76]), (8, [74]), (8, [72]), (8, [74]),
               (8, [72]), (80, []), (8, [72]), (8, [73]), (8, [76]), (8, [78]), (0, [])],
              [(8, []), (8, [70]), (8, [69]), (8, [66]), (32, [67]), (48, []), (16, [67]), (16, []), (16, [67]),
               (32, [66]), (0, [])],
              [(40, []), (8, [63]), (8, [62]), (8, [60]), (16, [59]), (32, [60]), (16, [59]), (16, [60]), (16, [64]),
               (32, [59, 61]), (0, [])],
              [(104, []), (16, [49]), (16, [51]), (16, [54]), (4, [52]), (4, [53]), (28, [55]), (0, [])]]

expected_events = [[[80], [79], [77], [76], [77], [76], [74], [72], [74], [72], [], [], [], [], [], [], [], [], [],
                    [72], [73], [76], [78], [78]],
                   [[], [70], [69], [66], [67], [67], [67], [67], [], [], [], [], [67], [67], [], [], [67], [67],
                    [67], [66], [66], [66], [66], [66]],
                   [[], [], [], [], [], [63], [62], [60], [59], [59], [60], [60], [59], [59], [60], [60], [64],
                    [64], [64], [59, 61], [59, 61], [59, 61], [59, 61], [59, 61]],
                   [[], [], [], [], [], [], [], [], [], [], [], [49], [49], [51], [51], [54], [54], [52], [53],
                    [55], [55], [55], [55], []],
                   [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 24, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 8, 4, 4]]

partial_events = [[], [], [], [], [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 24, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 8, 4, 4]]

expected_tempos = [500000] * 80
expected_tempos.extend([555555] * 64)
expected_tempos.extend([500000] * 49)

expected_midi = [[0.6328125, 0.625, 0.609375, 0.6015625, 0.609375, 0.6015625, 0.5859375, 0.5703125, 0.5859375,
                  0.5703125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5703125, 0.578125, 0.6015625, 0.6171875,
                  0.6171875],
                 [0.0, 0.5546875, 0.546875, 0.5234375, 0.53125, 0.53125, 0.53125, 0.53125, 0.0, 0.0, 0.0, 0.0,
                  0.53125, 0.53125, 0.0, 0.0, 0.53125, 0.53125, 0.53125, 0.5234375, 0.5234375, 0.5234375, 0.5234375,
                  0.5234375],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.4921875, 0.4765625, 0.46875, 0.46875, 0.4765625, 0.4765625,
                  0.46875, 0.46875, 0.4765625, 0.4765625, 0.5078125, 0.5078125, 0.5078125, 0.484375, 0.484375,
                  0.484375, 0.484375, 0.484375],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.390625, 0.390625, 0.40625, 0.40625,
                  0.4296875, 0.4296875, 0.4140625, 0.421875, 0.4375, 0.4375, 0.4375, 0.4375, 0.0],
                 [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.041666666666666664, 0.125,
                  0.125, 0.125, 0.125, 0.125, 0.125, 0.25, 0.25, 0.125, 0.125, 0.125, 0.25, 0.25],
                 [0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.0018000018000018,
                  0.0018000018000018, 0.0018000018000018, 0.0018000018000018, 0.0018000018000018,
                  0.0018000018000018, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002]]

partial_midi = [[0.6328125, 0.625, 0.609375, 0.6015625, 0.609375, 0.6015625, 0.5859375, 0.5703125, 0.5859375,
                 0.5703125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5703125, 0.578125, 0.6015625, 0.6171875,
                 0.6171875],
                [0.0, 0.5546875, 0.546875, 0.5234375, 0.53125, 0.53125, 0.53125, 0.53125, 0.0, 0.0, 0.0, 0.0,
                 0.53125, 0.53125, 0.0, 0.0, 0.53125, 0.53125, 0.53125, 0.5234375, 0.5234375, 0.5234375, 0.5234375,
                 0.5234375],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.4921875, 0.4765625, 0.46875, 0.46875, 0.4765625, 0.4765625,
                 0.46875, 0.46875, 0.4765625, 0.4765625, 0.5078125, 0.5078125, 0.5078125, 0.484375, 0.484375,
                 0.484375, 0.484375, 0.484375],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.390625, 0.390625, 0.40625, 0.40625,
                 0.4296875, 0.4296875, 0.4140625, 0.421875, 0.4375, 0.4375, 0.4375, 0.4375, 0.0],
                [],
                []]

expected_tonal = [[0.6363636363636364, 0.6363636363636364, 0.6363636363636364, 0.6363636363636364, 0.6363636363636364,
                   0.6363636363636364, 0.6363636363636364, 0.6363636363636364, 0.6363636363636364, 0.6363636363636364,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6363636363636364, 0.6363636363636364,
                   0.6363636363636364, 0.6363636363636364, 0.6363636363636364],
                  [0.75, 0.6666666666666666, 0.5, 0.4166666666666667, 0.5, 0.4166666666666667, 0.25,
                   0.08333333333333333, 0.25, 0.08333333333333333, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.08333333333333333, 0.16666666666666666, 0.4166666666666667, 0.5833333333333334,
                   0.5833333333333334],
                  [0.0, 0.5454545454545454, 0.5454545454545454, 0.5454545454545454, 0.5454545454545454,
                   0.5454545454545454, 0.5454545454545454, 0.5454545454545454, 0.0, 0.0, 0.0, 0.0, 0.5454545454545454,
                   0.5454545454545454, 0.0, 0.0, 0.5454545454545454, 0.5454545454545454, 0.5454545454545454,
                   0.5454545454545454, 0.5454545454545454, 0.5454545454545454, 0.5454545454545454, 0.5454545454545454],
                  [0.0, 0.9166666666666666, 0.8333333333333334, 0.5833333333333334, 0.6666666666666666,
                   0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.0, 0.0, 0.0, 0.0, 0.6666666666666666,
                   0.6666666666666666, 0.0, 0.0, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666,
                   0.5833333333333334, 0.5833333333333334, 0.5833333333333334, 0.5833333333333334, 0.5833333333333334],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.5454545454545454, 0.5454545454545454, 0.5454545454545454,
                   0.45454545454545453, 0.45454545454545453, 0.5454545454545454, 0.5454545454545454,
                   0.45454545454545453, 0.45454545454545453, 0.5454545454545454, 0.5454545454545454, 0.5454545454545454,
                   0.5454545454545454, 0.5454545454545454, 0.5454545454545454, 0.5454545454545454, 0.5454545454545454,
                   0.5454545454545454, 0.5454545454545454],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.3333333333333333, 0.25, 0.08333333333333333, 1.0, 1.0,
                   0.08333333333333333, 0.08333333333333333, 1.0, 1.0, 0.08333333333333333, 0.08333333333333333,
                   0.4166666666666667, 0.4166666666666667, 0.4166666666666667, 0.16666666666666666, 0.16666666666666666,
                   0.16666666666666666, 0.16666666666666666, 0.16666666666666666],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.45454545454545453, 0.45454545454545453,
                   0.45454545454545453, 0.45454545454545453, 0.45454545454545453, 0.45454545454545453,
                   0.45454545454545453, 0.45454545454545453, 0.45454545454545453, 0.45454545454545453,
                   0.45454545454545453, 0.45454545454545453, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.16666666666666666, 0.16666666666666666,
                   0.3333333333333333, 0.3333333333333333, 0.5833333333333334, 0.5833333333333334, 0.4166666666666667,
                   0.5, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.0],
                  [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.041666666666666664, 0.125,
                   0.125, 0.125, 0.125, 0.125, 0.125, 0.25, 0.25, 0.125, 0.125, 0.125, 0.25, 0.25],
                  [0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.0018000018000018,
                   0.0018000018000018, 0.0018000018000018, 0.0018000018000018, 0.0018000018000018, 0.0018000018000018,
                   0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002]]


def test_check_number_of_tracks_correct():
    check_number_of_tracks([1, 2, 3, 4, 5, 6], 'filename', 6)


def test_check_number_of_tracks_incorrect():
    with pytest.raises(ValueError):
        check_number_of_tracks([1, 2, 3], 'filename', 4)


def test_get_event_lists():
    events = get_event_lists(copy.deepcopy(input_list))

    assert isinstance(events, list)
    assert events == expected_events


def test_preprocess_features_check_correct():
    events, tempos = preprocess_features(file2_path, 'test_tempos_velocities_and_polyphony', True, 4)

    assert isinstance(events, list)
    assert isinstance(tempos, list)
    assert events == expected_events
    assert tempos == expected_tempos


def test_preprocess_features_check_incorrect():
    with pytest.raises(ValueError):
        _, _ = preprocess_features(file2_path, 'test_tempos_velocities_and_polyphony', True, 2)


def test_insert_meta_features():
    meta_features = insert_meta_features(copy.deepcopy(partial_midi), copy.deepcopy(partial_events),
                                         copy.deepcopy(expected_tempos))

    assert isinstance(meta_features, list)
    assert meta_features == expected_midi


def test_get_list_of_midi_features():
    midi_features = get_list_of_midi_features(copy.deepcopy(expected_events), copy.deepcopy(expected_tempos))

    assert isinstance(midi_features, list)
    assert midi_features == expected_midi


def test_get_list_of_tonal_features():
    tonal_features = get_list_of_tonal_features(copy.deepcopy(expected_events), copy.deepcopy(expected_tempos))

    assert isinstance(tonal_features, list)
    assert tonal_features == expected_tonal


def test_get_midi_features_file_1():
    out_array = get_midi_features(file1_path, 'test_all_notes')
    midi_array = np.load(output_1m_path, allow_pickle=True)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(out_array, midi_array)


def test_get_midi_features_file_2():
    out_array = get_midi_features(file2_path, 'test_tempos_velocities_and_polyphony')
    midi_array = np.load(output_2m_path, allow_pickle=True)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(out_array, midi_array)


def test_get_tonal_features_file_1():
    out_array = get_tonal_features(file1_path, 'test_all_notes')
    tonal_array = np.load(output_1t_path, allow_pickle=True)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(out_array, tonal_array)


def test_get_tonal_features_file_2():
    out_array = get_tonal_features(file2_path, 'test_tempos_velocities_and_polyphony')
    tonal_array = np.load(output_2t_path, allow_pickle=True)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(out_array, tonal_array)
