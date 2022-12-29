# import pytest

from midi.encode import *

# one-time setup
input_array_path = 'test_files/test_polyphony/ABF.npy'

input_tempos = [500000] * 80
input_tempos.extend([555555] * 64)
input_tempos.extend([500000] * 48)

expected_meta = MidiTrack([
    MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                notated_32nd_notes_per_beat=8, time=0),
    MetaMessage('set_tempo', tempo=500000, time=0),
    MetaMessage('set_tempo', tempo=555555, time=1200),
    MetaMessage('set_tempo', tempo=500000, time=960),
    MetaMessage('end_of_track', time=720)
])

expected_track = MidiTrack([
    Message('note_on', channel=0, note=80, velocity=64, time=0),
    Message('note_off', channel=0, note=80, velocity=64, time=120),
    Message('note_on', channel=0, note=70, velocity=64, time=0),
    Message('note_on', channel=0, note=79, velocity=64, time=0),
    Message('note_off', channel=0, note=70, velocity=64, time=120),
    Message('note_off', channel=0, note=79, velocity=64, time=0),
    Message('note_on', channel=0, note=69, velocity=64, time=0),
    Message('note_on', channel=0, note=77, velocity=64, time=0),
    Message('note_off', channel=0, note=69, velocity=64, time=120),
    Message('note_off', channel=0, note=77, velocity=64, time=0),
    Message('note_on', channel=0, note=66, velocity=64, time=0),
    Message('note_on', channel=0, note=76, velocity=64, time=0),
    Message('note_off', channel=0, note=66, velocity=64, time=120),
    Message('note_off', channel=0, note=76, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_on', channel=0, note=77, velocity=64, time=0),
    Message('note_off', channel=0, note=77, velocity=64, time=120),
    Message('note_on', channel=0, note=63, velocity=64, time=0),
    Message('note_on', channel=0, note=76, velocity=64, time=0),
    Message('note_off', channel=0, note=63, velocity=64, time=120),
    Message('note_off', channel=0, note=76, velocity=64, time=0),
    Message('note_on', channel=0, note=62, velocity=64, time=0),
    Message('note_on', channel=0, note=74, velocity=64, time=0),
    Message('note_off', channel=0, note=62, velocity=64, time=120),
    Message('note_off', channel=0, note=74, velocity=64, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_on', channel=0, note=72, velocity=64, time=0),
    Message('note_off', channel=0, note=60, velocity=64, time=120),
    Message('note_off', channel=0, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=72, velocity=64, time=0),
    Message('note_on', channel=0, note=59, velocity=64, time=0),
    Message('note_on', channel=0, note=74, velocity=64, time=0),
    Message('note_off', channel=0, note=74, velocity=64, time=120),
    Message('note_on', channel=0, note=72, velocity=64, time=0),
    Message('note_off', channel=0, note=59, velocity=64, time=120),
    Message('note_off', channel=0, note=72, velocity=64, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_on', channel=0, note=49, velocity=64, time=360),
    Message('note_off', channel=0, note=60, velocity=64, time=120),
    Message('note_on', channel=0, note=59, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=49, velocity=64, time=120),
    Message('note_on', channel=0, note=51, velocity=64, time=0),
    Message('note_off', channel=0, note=59, velocity=64, time=120),
    Message('note_off', channel=0, note=67, velocity=64, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_off', channel=0, note=51, velocity=64, time=120),
    Message('note_on', channel=0, note=54, velocity=64, time=0),
    Message('note_off', channel=0, note=60, velocity=64, time=120),
    Message('note_on', channel=0, note=64, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=54, velocity=64, time=120),
    Message('note_on', channel=0, note=52, velocity=64, time=0),
    Message('note_off', channel=0, note=52, velocity=64, time=60),
    Message('note_on', channel=0, note=53, velocity=64, time=0),
    Message('note_off', channel=0, note=53, velocity=64, time=60),
    Message('note_off', channel=0, note=64, velocity=64, time=0),
    Message('note_off', channel=0, note=67, velocity=64, time=0),
    Message('note_on', channel=0, note=55, velocity=64, time=0),
    Message('note_on', channel=0, note=59, velocity=64, time=0),
    Message('note_on', channel=0, note=61, velocity=64, time=0),
    Message('note_on', channel=0, note=66, velocity=64, time=0),
    Message('note_on', channel=0, note=72, velocity=64, time=0),
    Message('note_off', channel=0, note=72, velocity=64, time=120),
    Message('note_on', channel=0, note=73, velocity=64, time=0),
    Message('note_off', channel=0, note=73, velocity=64, time=120),
    Message('note_on', channel=0, note=76, velocity=64, time=0),
    Message('note_off', channel=0, note=76, velocity=64, time=120),
    Message('note_on', channel=0, note=78, velocity=64, time=0),
    Message('note_off', channel=0, note=55, velocity=64, time=60),
    Message('note_off', channel=0, note=59, velocity=64, time=60),
    Message('note_off', channel=0, note=61, velocity=64, time=0),
    Message('note_off', channel=0, note=66, velocity=64, time=0),
    Message('note_off', channel=0, note=78, velocity=64, time=0),
    MetaMessage('end_of_track', time=0)
])


def test_get_tempo_meta_messages():
    meta_track = get_tempo_meta_messages(input_tempos, float(15))

    assert isinstance(meta_track, MidiTrack)
    assert meta_track == expected_meta

# TODO: tests to write
# def test_get_tempo_array_from_tempo_sequences():
# def test_get_sequences_from_array():
# def test_get_tuples_from_sequences_boolean_mode():
# def test_get_tuples_from_sequences_velocities_mode():
# def test_get_messages_from_tuples_separate_notes():
# def test_get_messages_from_tuples_join_notes():
# def test_get_messages_from_tuples_with_default_velocities():
# def test_prepare_meta_file_with_event_lengths():
# def test_prepare_meta_file_without_event_lengths():
# def test_prepare_meta_file_with_custom_ticks_per_beat():
# def test_get_messages_from_standard_2d_input_with_sequences():
# def test_get_messages_from_standard_2d_input_without_sequences():
# def test_get_file_from_standard_features_with_constant_tempo():
# def test_get_file_from_standard_features_with_list_of_tempos():
# def test_get_file_from_standard_features_with_sequences():
# def test_get_file_from_standard_features_with_custom_grid_accuracy():
# def test_get_file_from_standard_features_2d_input():
# def test_get_file_from_standard_features_3d_input():
# def test_get_file_from_music21_features_midi_mode():
# def test_get_file_from_music21_features_tonal_mode():
