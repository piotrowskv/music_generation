import filecmp
import numpy as np
import os
import pytest

from midi.encode import *

# one-time setup
encode_file_folder = 'test_files/test_outputs'
encode_file_name = 'test_encode.mid'
encode_file_path = os.path.join(encode_file_folder, encode_file_name)

test_file_path = 'test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid'

input_array_ABF_path = 'test_files/test_polyphony/ABF.npy'
input_array_ABT_path = 'test_files/test_polyphony/ABT.npy'
input_array_SVTF_path = 'test_files/test_polyphony/SVTF_array.npy'
input_array_midi_path = 'test_files/test_polyphony/music21_midi.npy'
input_array_tonal_path = 'test_files/test_polyphony/music21_tonal.npy'

input_array_tempos = [500000] * 80
input_array_tempos.extend([555555] * 64)
input_array_tempos.extend([500000] * 48)

input_sequence_tempos = [500000] * 10
input_sequence_tempos.extend([555555] * 6)
input_sequence_tempos.extend([500000] * 9)

expected_array = []
for i in range(24):
    expected_array.append([False] * 128)
expected_array[0][80] = True
expected_array[1][70] = True
expected_array[1][79] = True
expected_array[2][69] = True
expected_array[2][77] = True
expected_array[3][66] = True
expected_array[3][76] = True
expected_array[4][67] = True
expected_array[4][77] = True
expected_array[5][63] = True
expected_array[5][67] = True
expected_array[5][76] = True
expected_array[6][62] = True
expected_array[6][67] = True
expected_array[6][74] = True
expected_array[7][60] = True
expected_array[7][67] = True
expected_array[7][72] = True
expected_array[8][59] = True
expected_array[8][74] = True
expected_array[9][59] = True
expected_array[9][72] = True
expected_array[10][60] = True
expected_array[11][49] = True
expected_array[11][60] = True
expected_array[12][49] = True
expected_array[12][59] = True
expected_array[12][67] = True
expected_array[13][51] = True
expected_array[13][59] = True
expected_array[13][67] = True
expected_array[14][51] = True
expected_array[14][60] = True
expected_array[15][54] = True
expected_array[15][60] = True
expected_array[16][54] = True
expected_array[16][64] = True
expected_array[16][67] = True
expected_array[17][52] = True
expected_array[17][64] = True
expected_array[17][67] = True
expected_array[18][53] = True
expected_array[18][64] = True
expected_array[18][67] = True
expected_array[19][55] = True
expected_array[19][59] = True
expected_array[19][61] = True
expected_array[19][66] = True
expected_array[19][72] = True
expected_array[20][55] = True
expected_array[20][59] = True
expected_array[20][61] = True
expected_array[20][66] = True
expected_array[20][73] = True
expected_array[21][55] = True
expected_array[21][59] = True
expected_array[21][61] = True
expected_array[21][66] = True
expected_array[21][76] = True
expected_array[22][55] = True
expected_array[22][59] = True
expected_array[22][61] = True
expected_array[22][66] = True
expected_array[22][78] = True
expected_array[23][59] = True
expected_array[23][61] = True
expected_array[23][66] = True
expected_array[23][78] = True

expected_sequences = []
for i in range(25):
    expected_sequences.append([0.0] * 128)
expected_sequences[0][80] = 0.5
expected_sequences[1][70] = 0.5
expected_sequences[1][79] = 0.5
expected_sequences[2][69] = 0.5
expected_sequences[2][77] = 0.5
expected_sequences[3][66] = 0.5
expected_sequences[3][76] = 0.5
expected_sequences[4][67] = 0.5
expected_sequences[4][77] = 0.5
expected_sequences[5][63] = 0.5
expected_sequences[5][67] = 0.5
expected_sequences[5][76] = 0.5
expected_sequences[6][62] = 0.5
expected_sequences[6][67] = 0.5
expected_sequences[6][74] = 0.5
expected_sequences[7][60] = 0.5
expected_sequences[7][67] = 0.5
expected_sequences[7][72] = 0.5
expected_sequences[8][59] = 0.5
expected_sequences[8][74] = 0.5
expected_sequences[9][59] = 0.5
expected_sequences[9][72] = 0.5
expected_sequences[10][60] = 0.5
expected_sequences[11][49] = 0.375
expected_sequences[11][60] = 0.5
expected_sequences[12][49] = 0.375
expected_sequences[12][59] = 0.5
expected_sequences[12][67] = 0.5
expected_sequences[13][51] = 0.375
expected_sequences[13][59] = 0.5
expected_sequences[13][67] = 0.5
expected_sequences[14][51] = 0.375
expected_sequences[14][60] = 0.5
expected_sequences[15][54] = 0.375
expected_sequences[15][60] = 0.5
expected_sequences[16][54] = 0.375
expected_sequences[16][64] = 0.5
expected_sequences[16][67] = 0.5
expected_sequences[17][52] = 0.25
expected_sequences[17][64] = 0.5
expected_sequences[17][67] = 0.5
expected_sequences[18][53] = 0.25
expected_sequences[18][64] = 0.5
expected_sequences[18][67] = 0.5
expected_sequences[19][55] = 0.25
expected_sequences[19][59] = 0.75
expected_sequences[19][61] = 0.75
expected_sequences[19][66] = 0.75
expected_sequences[19][72] = 0.25
expected_sequences[20][55] = 0.25
expected_sequences[20][59] = 0.75
expected_sequences[20][61] = 0.75
expected_sequences[20][66] = 0.75
expected_sequences[20][73] = 0.25
expected_sequences[21][55] = 0.25
expected_sequences[21][59] = 0.75
expected_sequences[21][61] = 0.75
expected_sequences[21][66] = 0.75
expected_sequences[21][76] = 0.25
expected_sequences[22][55] = 0.25
expected_sequences[22][59] = 0.75
expected_sequences[22][61] = 0.75
expected_sequences[22][66] = 0.75
expected_sequences[22][78] = 0.25
expected_sequences[23][59] = 0.75
expected_sequences[23][61] = 0.75
expected_sequences[23][66] = 0.75
expected_sequences[23][78] = 0.25
expected_sequences = np.asarray(expected_sequences)

expected_array_lengths = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 24, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 8, 4, 4]

expected_sequence_lengths = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 24, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 8, 4, 4, 0]

expected_array_tuples = [[(80, 127)],
                         [(70, 127), (79, 127)],
                         [(69, 127), (77, 127)],
                         [(66, 127), (76, 127)],
                         [(67, 127), (77, 127)],
                         [(63, 127), (67, 127), (76, 127)],
                         [(62, 127), (67, 127), (74, 127)],
                         [(60, 127), (67, 127), (72, 127)],
                         [(59, 127), (74, 127)],
                         [(59, 127), (72, 127)],
                         [(60, 127)],
                         [(49, 127), (60, 127)],
                         [(49, 127), (59, 127), (67, 127)],
                         [(51, 127), (59, 127), (67, 127)],
                         [(51, 127), (60, 127)],
                         [(54, 127), (60, 127)],
                         [(54, 127), (64, 127), (67, 127)],
                         [(52, 127), (64, 127), (67, 127)],
                         [(53, 127), (64, 127), (67, 127)],
                         [(55, 127), (59, 127), (61, 127), (66, 127), (72, 127)],
                         [(55, 127), (59, 127), (61, 127), (66, 127), (73, 127)],
                         [(55, 127), (59, 127), (61, 127), (66, 127), (76, 127)],
                         [(55, 127), (59, 127), (61, 127), (66, 127), (78, 127)],
                         [(59, 127), (61, 127), (66, 127), (78, 127)]]

expected_sequence_tuples = [[(80, 64)],
                            [(70, 64), (79, 64)],
                            [(69, 64), (77, 64)],
                            [(66, 64), (76, 64)],
                            [(67, 64), (77, 64)],
                            [(63, 64), (67, 64), (76, 64)],
                            [(62, 64), (67, 64), (74, 64)],
                            [(60, 64), (67, 64), (72, 64)],
                            [(59, 64), (74, 64)],
                            [(59, 64), (72, 64)],
                            [(60, 64)],
                            [(49, 48), (60, 64)],
                            [(49, 48), (59, 64), (67, 64)],
                            [(51, 48), (59, 64), (67, 64)],
                            [(51, 48), (60, 64)],
                            [(54, 48), (60, 64)],
                            [(54, 48), (64, 64), (67, 64)],
                            [(52, 32), (64, 64), (67, 64)],
                            [(53, 32), (64, 64), (67, 64)],
                            [(55, 32), (59, 96), (61, 96), (66, 96), (72, 32)],
                            [(55, 32), (59, 96), (61, 96), (66, 96), (73, 32)],
                            [(55, 32), (59, 96), (61, 96), (66, 96), (76, 32)],
                            [(55, 32), (59, 96), (61, 96), (66, 96), (78, 32)],
                            [(59, 96), (61, 96), (66, 96), (78, 32)],
                            []]

expected_constant_meta_track = MidiTrack([
    MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                notated_32nd_notes_per_beat=8, time=0),
    MetaMessage('set_tempo', tempo=500000, time=0),
    MetaMessage('end_of_track', time=2880)])

expected_meta_track = MidiTrack([
    MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                notated_32nd_notes_per_beat=8, time=0),
    MetaMessage('set_tempo', tempo=500000, time=0),
    MetaMessage('set_tempo', tempo=555555, time=1200),
    MetaMessage('set_tempo', tempo=500000, time=960),
    MetaMessage('end_of_track', time=720)])

expected_array_track = MidiTrack([
    Message('note_on', channel=0, note=80, velocity=64, time=0),
    Message('note_off', channel=0, note=80, velocity=0, time=120),
    Message('note_on', channel=0, note=70, velocity=64, time=0),
    Message('note_on', channel=0, note=79, velocity=64, time=0),
    Message('note_off', channel=0, note=70, velocity=0, time=120),
    Message('note_off', channel=0, note=79, velocity=0, time=0),
    Message('note_on', channel=0, note=69, velocity=64, time=0),
    Message('note_on', channel=0, note=77, velocity=64, time=0),
    Message('note_off', channel=0, note=69, velocity=0, time=120),
    Message('note_off', channel=0, note=77, velocity=0, time=0),
    Message('note_on', channel=0, note=66, velocity=64, time=0),
    Message('note_on', channel=0, note=76, velocity=64, time=0),
    Message('note_off', channel=0, note=66, velocity=0, time=120),
    Message('note_off', channel=0, note=76, velocity=0, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_on', channel=0, note=77, velocity=64, time=0),
    Message('note_off', channel=0, note=77, velocity=0, time=120),
    Message('note_on', channel=0, note=63, velocity=64, time=0),
    Message('note_on', channel=0, note=76, velocity=64, time=0),
    Message('note_off', channel=0, note=63, velocity=0, time=120),
    Message('note_off', channel=0, note=76, velocity=0, time=0),
    Message('note_on', channel=0, note=62, velocity=64, time=0),
    Message('note_on', channel=0, note=74, velocity=64, time=0),
    Message('note_off', channel=0, note=62, velocity=0, time=120),
    Message('note_off', channel=0, note=74, velocity=0, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_on', channel=0, note=72, velocity=64, time=0),
    Message('note_off', channel=0, note=60, velocity=0, time=120),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_off', channel=0, note=72, velocity=0, time=0),
    Message('note_on', channel=0, note=59, velocity=64, time=0),
    Message('note_on', channel=0, note=74, velocity=64, time=0),
    Message('note_off', channel=0, note=74, velocity=0, time=120),
    Message('note_on', channel=0, note=72, velocity=64, time=0),
    Message('note_off', channel=0, note=59, velocity=0, time=120),
    Message('note_off', channel=0, note=72, velocity=0, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_on', channel=0, note=49, velocity=64, time=360),
    Message('note_off', channel=0, note=60, velocity=0, time=120),
    Message('note_on', channel=0, note=59, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=49, velocity=0, time=120),
    Message('note_on', channel=0, note=51, velocity=64, time=0),
    Message('note_off', channel=0, note=59, velocity=0, time=120),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_off', channel=0, note=51, velocity=0, time=120),
    Message('note_on', channel=0, note=54, velocity=64, time=0),
    Message('note_off', channel=0, note=60, velocity=0, time=120),
    Message('note_on', channel=0, note=64, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=54, velocity=0, time=120),
    Message('note_on', channel=0, note=52, velocity=64, time=0),
    Message('note_off', channel=0, note=52, velocity=0, time=60),
    Message('note_on', channel=0, note=53, velocity=64, time=0),
    Message('note_off', channel=0, note=53, velocity=0, time=60),
    Message('note_off', channel=0, note=64, velocity=0, time=0),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_on', channel=0, note=55, velocity=64, time=0),
    Message('note_on', channel=0, note=59, velocity=64, time=0),
    Message('note_on', channel=0, note=61, velocity=64, time=0),
    Message('note_on', channel=0, note=66, velocity=64, time=0),
    Message('note_on', channel=0, note=72, velocity=64, time=0),
    Message('note_off', channel=0, note=72, velocity=0, time=120),
    Message('note_on', channel=0, note=73, velocity=64, time=0),
    Message('note_off', channel=0, note=73, velocity=0, time=120),
    Message('note_on', channel=0, note=76, velocity=64, time=0),
    Message('note_off', channel=0, note=76, velocity=0, time=120),
    Message('note_on', channel=0, note=78, velocity=64, time=0),
    Message('note_off', channel=0, note=55, velocity=0, time=60),
    Message('note_off', channel=0, note=59, velocity=0, time=60),
    Message('note_off', channel=0, note=61, velocity=0, time=0),
    Message('note_off', channel=0, note=66, velocity=0, time=0),
    Message('note_off', channel=0, note=78, velocity=0, time=0),
    MetaMessage('end_of_track', time=0)])

expected_custom_array_track = MidiTrack([
    Message('note_on', channel=0, note=80, velocity=32, time=0),
    Message('note_off', channel=0, note=80, velocity=0, time=120),
    Message('note_on', channel=0, note=70, velocity=32, time=0),
    Message('note_on', channel=0, note=79, velocity=32, time=0),
    Message('note_off', channel=0, note=70, velocity=0, time=120),
    Message('note_off', channel=0, note=79, velocity=0, time=0),
    Message('note_on', channel=0, note=69, velocity=32, time=0),
    Message('note_on', channel=0, note=77, velocity=32, time=0),
    Message('note_off', channel=0, note=69, velocity=0, time=120),
    Message('note_off', channel=0, note=77, velocity=0, time=0),
    Message('note_on', channel=0, note=66, velocity=32, time=0),
    Message('note_on', channel=0, note=76, velocity=32, time=0),
    Message('note_off', channel=0, note=66, velocity=0, time=120),
    Message('note_off', channel=0, note=76, velocity=0, time=0),
    Message('note_on', channel=0, note=67, velocity=32, time=0),
    Message('note_on', channel=0, note=77, velocity=32, time=0),
    Message('note_off', channel=0, note=77, velocity=0, time=120),
    Message('note_on', channel=0, note=63, velocity=32, time=0),
    Message('note_on', channel=0, note=76, velocity=32, time=0),
    Message('note_off', channel=0, note=63, velocity=0, time=120),
    Message('note_off', channel=0, note=76, velocity=0, time=0),
    Message('note_on', channel=0, note=62, velocity=32, time=0),
    Message('note_on', channel=0, note=74, velocity=32, time=0),
    Message('note_off', channel=0, note=62, velocity=0, time=120),
    Message('note_off', channel=0, note=74, velocity=0, time=0),
    Message('note_on', channel=0, note=60, velocity=32, time=0),
    Message('note_on', channel=0, note=72, velocity=32, time=0),
    Message('note_off', channel=0, note=60, velocity=0, time=120),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_off', channel=0, note=72, velocity=0, time=0),
    Message('note_on', channel=0, note=59, velocity=32, time=0),
    Message('note_on', channel=0, note=74, velocity=32, time=0),
    Message('note_off', channel=0, note=74, velocity=0, time=120),
    Message('note_on', channel=0, note=72, velocity=32, time=0),
    Message('note_off', channel=0, note=59, velocity=0, time=120),
    Message('note_off', channel=0, note=72, velocity=0, time=0),
    Message('note_on', channel=0, note=60, velocity=32, time=0),
    Message('note_on', channel=0, note=49, velocity=32, time=360),
    Message('note_off', channel=0, note=60, velocity=0, time=120),
    Message('note_on', channel=0, note=59, velocity=32, time=0),
    Message('note_on', channel=0, note=67, velocity=32, time=0),
    Message('note_off', channel=0, note=49, velocity=0, time=120),
    Message('note_on', channel=0, note=51, velocity=32, time=0),
    Message('note_off', channel=0, note=59, velocity=0, time=120),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_on', channel=0, note=60, velocity=32, time=0),
    Message('note_off', channel=0, note=51, velocity=0, time=120),
    Message('note_on', channel=0, note=54, velocity=32, time=0),
    Message('note_off', channel=0, note=60, velocity=0, time=120),
    Message('note_on', channel=0, note=64, velocity=32, time=0),
    Message('note_on', channel=0, note=67, velocity=32, time=0),
    Message('note_off', channel=0, note=54, velocity=0, time=120),
    Message('note_on', channel=0, note=52, velocity=32, time=0),
    Message('note_off', channel=0, note=52, velocity=0, time=60),
    Message('note_on', channel=0, note=53, velocity=32, time=0),
    Message('note_off', channel=0, note=53, velocity=0, time=60),
    Message('note_off', channel=0, note=64, velocity=0, time=0),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_on', channel=0, note=55, velocity=32, time=0),
    Message('note_on', channel=0, note=59, velocity=32, time=0),
    Message('note_on', channel=0, note=61, velocity=32, time=0),
    Message('note_on', channel=0, note=66, velocity=32, time=0),
    Message('note_on', channel=0, note=72, velocity=32, time=0),
    Message('note_off', channel=0, note=72, velocity=0, time=120),
    Message('note_on', channel=0, note=73, velocity=32, time=0),
    Message('note_off', channel=0, note=73, velocity=0, time=120),
    Message('note_on', channel=0, note=76, velocity=32, time=0),
    Message('note_off', channel=0, note=76, velocity=0, time=120),
    Message('note_on', channel=0, note=78, velocity=32, time=0),
    Message('note_off', channel=0, note=55, velocity=0, time=60),
    Message('note_off', channel=0, note=59, velocity=0, time=60),
    Message('note_off', channel=0, note=61, velocity=0, time=0),
    Message('note_off', channel=0, note=66, velocity=0, time=0),
    Message('note_off', channel=0, note=78, velocity=0, time=0),
    MetaMessage('end_of_track', time=0)])

expected_sequence_track = MidiTrack([
    Message('note_on', channel=0, note=80, velocity=64, time=0),
    Message('note_off', channel=0, note=80, velocity=0, time=120),
    Message('note_on', channel=0, note=70, velocity=64, time=0),
    Message('note_on', channel=0, note=79, velocity=64, time=0),
    Message('note_off', channel=0, note=70, velocity=0, time=120),
    Message('note_off', channel=0, note=79, velocity=0, time=0),
    Message('note_on', channel=0, note=69, velocity=64, time=0),
    Message('note_on', channel=0, note=77, velocity=64, time=0),
    Message('note_off', channel=0, note=69, velocity=0, time=120),
    Message('note_off', channel=0, note=77, velocity=0, time=0),
    Message('note_on', channel=0, note=66, velocity=64, time=0),
    Message('note_on', channel=0, note=76, velocity=64, time=0),
    Message('note_off', channel=0, note=66, velocity=0, time=120),
    Message('note_off', channel=0, note=76, velocity=0, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_on', channel=0, note=77, velocity=64, time=0),
    Message('note_off', channel=0, note=67, velocity=0, time=120),
    Message('note_off', channel=0, note=77, velocity=0, time=0),
    Message('note_on', channel=0, note=63, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_on', channel=0, note=76, velocity=64, time=0),
    Message('note_off', channel=0, note=63, velocity=0, time=120),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_off', channel=0, note=76, velocity=0, time=0),
    Message('note_on', channel=0, note=62, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_on', channel=0, note=74, velocity=64, time=0),
    Message('note_off', channel=0, note=62, velocity=0, time=120),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_off', channel=0, note=74, velocity=0, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_on', channel=0, note=72, velocity=64, time=0),
    Message('note_off', channel=0, note=60, velocity=0, time=120),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_off', channel=0, note=72, velocity=0, time=0),
    Message('note_on', channel=0, note=59, velocity=64, time=0),
    Message('note_on', channel=0, note=74, velocity=64, time=0),
    Message('note_off', channel=0, note=59, velocity=0, time=120),
    Message('note_off', channel=0, note=74, velocity=0, time=0),
    Message('note_on', channel=0, note=59, velocity=64, time=0),
    Message('note_on', channel=0, note=72, velocity=64, time=0),
    Message('note_off', channel=0, note=59, velocity=0, time=120),
    Message('note_off', channel=0, note=72, velocity=0, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_off', channel=0, note=60, velocity=0, time=360),
    Message('note_on', channel=0, note=49, velocity=48, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_off', channel=0, note=49, velocity=0, time=120),
    Message('note_off', channel=0, note=60, velocity=0, time=0),
    Message('note_on', channel=0, note=49, velocity=48, time=0),
    Message('note_on', channel=0, note=59, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=49, velocity=0, time=120),
    Message('note_off', channel=0, note=59, velocity=0, time=0),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_on', channel=0, note=51, velocity=48, time=0),
    Message('note_on', channel=0, note=59, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=51, velocity=0, time=120),
    Message('note_off', channel=0, note=59, velocity=0, time=0),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_on', channel=0, note=51, velocity=48, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_off', channel=0, note=51, velocity=0, time=120),
    Message('note_off', channel=0, note=60, velocity=0, time=0),
    Message('note_on', channel=0, note=54, velocity=48, time=0),
    Message('note_on', channel=0, note=60, velocity=64, time=0),
    Message('note_off', channel=0, note=54, velocity=0, time=120),
    Message('note_off', channel=0, note=60, velocity=0, time=0),
    Message('note_on', channel=0, note=54, velocity=48, time=0),
    Message('note_on', channel=0, note=64, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=54, velocity=0, time=120),
    Message('note_off', channel=0, note=64, velocity=0, time=0),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_on', channel=0, note=52, velocity=32, time=0),
    Message('note_on', channel=0, note=64, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=52, velocity=0, time=60),
    Message('note_off', channel=0, note=64, velocity=0, time=0),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_on', channel=0, note=53, velocity=32, time=0),
    Message('note_on', channel=0, note=64, velocity=64, time=0),
    Message('note_on', channel=0, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=53, velocity=0, time=60),
    Message('note_off', channel=0, note=64, velocity=0, time=0),
    Message('note_off', channel=0, note=67, velocity=0, time=0),
    Message('note_on', channel=0, note=55, velocity=32, time=0),
    Message('note_on', channel=0, note=59, velocity=96, time=0),
    Message('note_on', channel=0, note=61, velocity=96, time=0),
    Message('note_on', channel=0, note=66, velocity=96, time=0),
    Message('note_on', channel=0, note=72, velocity=32, time=0),
    Message('note_off', channel=0, note=55, velocity=0, time=120),
    Message('note_off', channel=0, note=59, velocity=0, time=0),
    Message('note_off', channel=0, note=61, velocity=0, time=0),
    Message('note_off', channel=0, note=66, velocity=0, time=0),
    Message('note_off', channel=0, note=72, velocity=0, time=0),
    Message('note_on', channel=0, note=55, velocity=32, time=0),
    Message('note_on', channel=0, note=59, velocity=96, time=0),
    Message('note_on', channel=0, note=61, velocity=96, time=0),
    Message('note_on', channel=0, note=66, velocity=96, time=0),
    Message('note_on', channel=0, note=73, velocity=32, time=0),
    Message('note_off', channel=0, note=55, velocity=0, time=120),
    Message('note_off', channel=0, note=59, velocity=0, time=0),
    Message('note_off', channel=0, note=61, velocity=0, time=0),
    Message('note_off', channel=0, note=66, velocity=0, time=0),
    Message('note_off', channel=0, note=73, velocity=0, time=0),
    Message('note_on', channel=0, note=55, velocity=32, time=0),
    Message('note_on', channel=0, note=59, velocity=96, time=0),
    Message('note_on', channel=0, note=61, velocity=96, time=0),
    Message('note_on', channel=0, note=66, velocity=96, time=0),
    Message('note_on', channel=0, note=76, velocity=32, time=0),
    Message('note_off', channel=0, note=55, velocity=0, time=120),
    Message('note_off', channel=0, note=59, velocity=0, time=0),
    Message('note_off', channel=0, note=61, velocity=0, time=0),
    Message('note_off', channel=0, note=66, velocity=0, time=0),
    Message('note_off', channel=0, note=76, velocity=0, time=0),
    Message('note_on', channel=0, note=55, velocity=32, time=0),
    Message('note_on', channel=0, note=59, velocity=96, time=0),
    Message('note_on', channel=0, note=61, velocity=96, time=0),
    Message('note_on', channel=0, note=66, velocity=96, time=0),
    Message('note_on', channel=0, note=78, velocity=32, time=0),
    Message('note_off', channel=0, note=55, velocity=0, time=60),
    Message('note_off', channel=0, note=59, velocity=0, time=0),
    Message('note_off', channel=0, note=61, velocity=0, time=0),
    Message('note_off', channel=0, note=66, velocity=0, time=0),
    Message('note_off', channel=0, note=78, velocity=0, time=0),
    Message('note_on', channel=0, note=59, velocity=96, time=0),
    Message('note_on', channel=0, note=61, velocity=96, time=0),
    Message('note_on', channel=0, note=66, velocity=96, time=0),
    Message('note_on', channel=0, note=78, velocity=32, time=0),
    Message('note_off', channel=0, note=59, velocity=0, time=60),
    Message('note_off', channel=0, note=61, velocity=0, time=0),
    Message('note_off', channel=0, note=66, velocity=0, time=0),
    Message('note_off', channel=0, note=78, velocity=0, time=0),
    MetaMessage('end_of_track', time=0)])

expected_custom_meta_file = MidiFile(type=1, ticks_per_beat=480, tracks=[
    MidiTrack([
        MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                    notated_32nd_notes_per_beat=8, time=0),
        MetaMessage('set_tempo', tempo=500000, time=0),
        MetaMessage('set_tempo', tempo=555555, time=2400),
        MetaMessage('set_tempo', tempo=500000, time=1920),
        MetaMessage('end_of_track', time=1440)])
])

expected_meta_file = MidiFile(type=1, ticks_per_beat=240, tracks=[
    MidiTrack([
        MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                    notated_32nd_notes_per_beat=8, time=0),
        MetaMessage('set_tempo', tempo=500000, time=0),
        MetaMessage('set_tempo', tempo=555555, time=1200),
        MetaMessage('set_tempo', tempo=500000, time=960),
        MetaMessage('end_of_track', time=720)])
])


def test_get_tempo_meta_messages():
    meta_track = get_tempo_meta_messages(input_array_tempos, float(15))

    assert isinstance(meta_track, MidiTrack)
    assert meta_track == expected_meta_track


def test_get_tempo_array_from_tempo_sequences():
    tempos = get_tempo_array_from_tempo_sequences(input_sequence_tempos, expected_sequence_lengths)

    assert isinstance(tempos, list)
    assert tempos == input_array_tempos


def test_get_sequences_from_array():
    input_array = np.load(input_array_ABT_path, allow_pickle=True)
    events, event_lengths = get_sequences_from_array(input_array)

    assert isinstance(events, list)
    assert isinstance(event_lengths, list)
    assert events == expected_array
    assert event_lengths == expected_array_lengths


def test_get_tuples_from_sequences_boolean_mode():
    tuples = get_tuples_from_sequences(expected_array)

    assert isinstance(tuples, list)
    assert tuples == expected_array_tuples


def test_get_tuples_from_sequences_velocities_mode():
    sequences = expected_sequences.tolist()
    tuples = get_tuples_from_sequences(sequences)

    assert isinstance(tuples, list)
    assert tuples == expected_sequence_tuples


def test_get_messages_from_tuples_separate_notes():
    track = get_messages_from_tuples(expected_sequence_tuples, 0, expected_sequence_lengths,
                                     float(15), False, False)

    assert isinstance(track, MidiTrack)
    assert track == expected_sequence_track


def test_get_messages_from_tuples_join_notes():
    track = get_messages_from_tuples(expected_array_tuples, 0, expected_array_lengths,
                                     float(15), True, True)

    assert isinstance(track, MidiTrack)
    assert track == expected_array_track


def test_get_messages_from_tuples_with_default_velocities():
    track = get_messages_from_tuples(expected_array_tuples, 0, expected_array_lengths,
                                     float(15), True, True, 32)

    assert isinstance(track, MidiTrack)
    assert track == expected_custom_array_track


def test_prepare_meta_file_with_event_lengths():
    tempos, accuracy, midi_file = prepare_meta_file(input_sequence_tempos, 64,
                                                    expected_sequence_lengths, 240)

    assert isinstance(tempos, list)
    assert isinstance(accuracy, float)
    assert isinstance(midi_file, MidiFile)

    assert tempos == input_array_tempos
    assert accuracy == float(15)
    assert repr(midi_file) == repr(expected_meta_file)


def test_prepare_meta_file_without_event_lengths():
    tempos, accuracy, midi_file = prepare_meta_file(input_array_tempos, 64, None, 240)

    assert isinstance(tempos, list)
    assert isinstance(accuracy, float)
    assert isinstance(midi_file, MidiFile)

    assert tempos == input_array_tempos
    assert accuracy == float(15)
    assert repr(midi_file) == repr(expected_meta_file)


def test_prepare_meta_file_with_custom_ticks_per_beat():
    tempos, accuracy, midi_file = prepare_meta_file(input_array_tempos, 64, None, 480)

    assert isinstance(tempos, list)
    assert isinstance(accuracy, float)
    assert isinstance(midi_file, MidiFile)

    assert tempos == input_array_tempos
    assert accuracy == float(30)
    assert repr(midi_file) == repr(expected_custom_meta_file)


def test_get_messages_from_standard_2d_input_with_sequences():
    track = get_messages_from_standard_2d_input(expected_sequences, 0, float(15), False, True, True,
                                                expected_sequence_lengths)

    assert isinstance(track, MidiTrack)
    assert track == expected_sequence_track


def test_get_messages_from_standard_2d_input_without_sequences():
    input_array = np.load(input_array_ABT_path, allow_pickle=True)
    track = get_messages_from_standard_2d_input(input_array, 0, float(15), True, False, False)

    assert isinstance(track, MidiTrack)
    assert track == expected_array_track


def test_get_file_from_standard_features_with_constant_tempo():
    input_array = np.load(input_array_ABT_path, allow_pickle=True)
    get_file_from_standard_features(input_array, 500000, encode_file_path,
                                    True, False, False)

    assert os.path.exists(encode_file_path)
    file = MidiFile(encode_file_path)

    assert hasattr(file, 'tracks')
    assert len(file.tracks) == 2
    assert file.tracks[0] == expected_constant_meta_track

    os.remove(encode_file_path)
    os.rmdir(encode_file_folder)


# TODO: check content?
def test_get_file_from_standard_features_with_sequences():
    input_array = np.load(input_array_SVTF_path, allow_pickle=True)
    get_file_from_standard_features(input_array, input_sequence_tempos,
                                    encode_file_path, False, True, False,
                                    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 24, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 8, 4, 4, 0])

    assert os.path.exists(encode_file_path)
    assert filecmp.cmp(encode_file_path, 'test_files/test_encoder/test_sequences.mid')

    os.remove(encode_file_path)
    os.rmdir(encode_file_folder)


def test_get_file_from_standard_features_with_custom_grid_accuracy():
    input_array = np.load(input_array_ABT_path, allow_pickle=True)
    get_file_from_standard_features(input_array, input_array_tempos, encode_file_path,
                                    True, False, False, None, 32)

    assert os.path.exists(encode_file_path)
    assert filecmp.cmp(encode_file_path, 'test_files/test_encoder/test_custom_grid.mid')

    os.remove(encode_file_path)
    os.rmdir(encode_file_folder)


def test_get_file_from_standard_features_2d_input():
    input_array = np.load(input_array_ABT_path, allow_pickle=True)
    get_file_from_standard_features(input_array, input_array_tempos, encode_file_path,
                                    True, False, False)

    assert os.path.exists(encode_file_path)
    assert filecmp.cmp(encode_file_path, 'test_files/test_encoder/test_2d_array.mid')

    os.remove(encode_file_path)
    os.rmdir(encode_file_folder)


def test_get_file_from_standard_features_3d_input():
    input_array = np.load(input_array_ABF_path, allow_pickle=True)
    get_file_from_standard_features(input_array, input_array_tempos, encode_file_path,
                                    True, False, False)

    assert os.path.exists(encode_file_path)
    assert filecmp.cmp(encode_file_path, 'test_files/test_encoder/test_3d_array.mid')

    os.remove(encode_file_path)
    os.rmdir(encode_file_folder)


def test_get_file_from_music21_features_midi_mode():
    input_array = np.load(input_array_midi_path, allow_pickle=True)
    get_file_from_music21_features(input_array, encode_file_path, False, True)

    assert os.path.exists(encode_file_path)
    assert filecmp.cmp(encode_file_path, 'test_files/test_encoder/test_music21_midi.mid')

    os.remove(encode_file_path)
    os.rmdir(encode_file_folder)


def test_get_file_from_music21_features_tonal_mode():
    input_array = np.load(input_array_tonal_path, allow_pickle=True)
    get_file_from_music21_features(input_array, encode_file_path, True, True)

    assert os.path.exists(encode_file_path)
    assert filecmp.cmp(encode_file_path, 'test_files/test_encoder/test_music21_tonal.mid')

    os.remove(encode_file_path)
    os.rmdir(encode_file_folder)
