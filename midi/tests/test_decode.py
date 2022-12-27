import filecmp
import os.path

import numpy as np
import pytest

from midi.decode import *
from mido.midifiles.meta import MetaMessage

# one-time setup
file_notes_folder = 'test_files/test_notes/'
file_polyphony_folder = 'test_files/test_polyphony/'
file_types_folder = 'test_files/test_types/'

file_1_name = 'test_all_notes'
file_2_name = 'test_tempos_velocities_and_polyphony'
file_3_name = 'test_type_0'
file_4_name = 'test_type_1_corrupt'
file_5_name = 'test_type_1_empty'
file_6_name = 'test_type_1_untrimmed'
file_7_name = 'test_type_2'

dictionary = dict[int, EventNote]()
dictionary[64] = EventNote(64, 64)
dictionary[65] = EventNote(64, 65)
dictionary[67] = EventNote(64, 67)

expected_booleans = [False] * 64
expected_booleans.extend([True, True, False, True])
expected_booleans.extend([False] * 60)

expected_velocities = [0.0] * 64
expected_velocities.extend([64.0, 64.0, 0.0, 64.0])
expected_velocities.extend([0.0] * 60)

expected_tempos = [500000] * 80
expected_tempos.extend([555555] * 64)
expected_tempos.extend([500000] * 49)

expected_trimmed_tempos = [500000] * 33

expected_untrimmed_tempos = [500000] * 65

expected_midi_track = MidiTrack([
    Message('note_on', channel=0, note=80, velocity=64, time=0),
    Message('note_off', channel=0, note=80, velocity=0, time=96),
    Message('note_on', channel=0, note=79, velocity=64, time=0),
    Message('note_on', channel=1, note=70, velocity=64, time=0),
    Message('note_off', channel=0, note=79, velocity=0, time=96),
    Message('note_on', channel=0, note=77, velocity=64, time=0),
    Message('note_off', channel=1, note=70, velocity=0, time=0),
    Message('note_on', channel=1, note=69, velocity=64, time=0),
    Message('note_off', channel=0, note=77, velocity=0, time=96),
    Message('note_on', channel=0, note=76, velocity=64, time=0),
    Message('note_off', channel=1, note=69, velocity=0, time=0),
    Message('note_on', channel=1, note=66, velocity=64, time=0),
    Message('note_off', channel=0, note=76, velocity=0, time=96),
    Message('note_on', channel=0, note=77, velocity=64, time=0),
    Message('note_off', channel=1, note=66, velocity=0, time=0),
    Message('note_on', channel=1, note=67, velocity=64, time=0),
    Message('note_off', channel=0, note=77, velocity=0, time=96),
    Message('note_on', channel=0, note=76, velocity=64, time=0),
    Message('note_on', channel=2, note=63, velocity=64, time=0),
    Message('note_off', channel=0, note=76, velocity=0, time=96),
    Message('note_on', channel=0, note=74, velocity=64, time=0),
    Message('note_off', channel=2, note=63, velocity=0, time=0),
    Message('note_on', channel=2, note=62, velocity=64, time=0),
    Message('note_off', channel=0, note=74, velocity=0, time=96),
    Message('note_on', channel=0, note=72, velocity=64, time=0),
    Message('note_off', channel=2, note=62, velocity=0, time=0),
    Message('note_on', channel=2, note=60, velocity=64, time=0),
    Message('note_off', channel=0, note=72, velocity=0, time=96),
    Message('note_on', channel=0, note=74, velocity=64, time=0),
    Message('note_off', channel=1, note=67, velocity=0, time=0),
    Message('note_off', channel=2, note=60, velocity=0, time=0),
    Message('note_on', channel=2, note=59, velocity=64, time=0),
    Message('note_off', channel=0, note=74, velocity=0, time=96),
    Message('note_on', channel=0, note=72, velocity=64, time=0),
    Message('note_off', channel=0, note=72, velocity=0, time=96),
    Message('note_off', channel=2, note=59, velocity=0, time=0),
    Message('note_on', channel=2, note=60, velocity=64, time=0),
    Message('note_on', channel=3, note=49, velocity=48, time=288),
    Message('note_on', channel=1, note=67, velocity=64, time=96),
    Message('note_off', channel=2, note=60, velocity=0, time=0),
    Message('note_on', channel=2, note=59, velocity=64, time=0),
    Message('note_off', channel=3, note=49, velocity=0, time=96),
    Message('note_on', channel=3, note=51, velocity=48, time=0),
    Message('note_off', channel=1, note=67, velocity=0, time=96),
    Message('note_off', channel=2, note=59, velocity=0, time=0),
    Message('note_on', channel=2, note=60, velocity=64, time=0),
    Message('note_off', channel=3, note=51, velocity=0, time=96),
    Message('note_on', channel=3, note=54, velocity=48, time=0),
    Message('note_on', channel=1, note=67, velocity=64, time=96),
    Message('note_off', channel=2, note=60, velocity=0, time=0),
    Message('note_on', channel=2, note=64, velocity=64, time=0),
    Message('note_off', channel=3, note=54, velocity=0, time=96),
    Message('note_on', channel=3, note=52, velocity=32, time=0),
    Message('note_off', channel=3, note=52, velocity=0, time=48),
    Message('note_on', channel=3, note=53, velocity=32, time=0),
    Message('note_on', channel=0, note=72, velocity=32, time=48),
    Message('note_off', channel=1, note=67, velocity=0, time=0),
    Message('note_on', channel=1, note=66, velocity=96, time=0),
    Message('note_off', channel=2, note=64, velocity=0, time=0),
    Message('note_on', channel=2, note=61, velocity=96, time=0),
    Message('note_on', channel=2, note=59, velocity=96, time=0),
    Message('note_off', channel=3, note=53, velocity=0, time=0),
    Message('note_on', channel=3, note=55, velocity=32, time=0),
    Message('note_off', channel=0, note=72, velocity=0, time=96),
    Message('note_on', channel=0, note=73, velocity=32, time=0),
    Message('note_off', channel=0, note=73, velocity=0, time=96),
    Message('note_on', channel=0, note=76, velocity=32, time=0),
    Message('note_off', channel=0, note=76, velocity=0, time=96),
    Message('note_on', channel=0, note=78, velocity=32, time=0),
    Message('note_off', channel=3, note=55, velocity=0, time=48),
    Message('note_off', channel=0, note=78, velocity=0, time=48),
    Message('note_off', channel=1, note=66, velocity=0, time=0),
    Message('note_off', channel=2, note=61, velocity=0, time=0),
    Message('note_off', channel=2, note=59, velocity=0, time=0)
])

expected_prepared_file_with_join = MidiFile(type=1, ticks_per_beat=192, tracks=[
    MidiTrack([
        MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                    notated_32nd_notes_per_beat=8, time=0),
        MetaMessage('set_tempo', tempo=500000, time=0),
        MetaMessage('set_tempo', tempo=555555, time=960),
        MetaMessage('set_tempo', tempo=500000, time=768),
        MetaMessage('end_of_track', time=576)]),
    expected_midi_track
])

expected_prepared_file_without_join = MidiFile(type=1, ticks_per_beat=192, tracks=[
    MidiTrack([
        MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                    notated_32nd_notes_per_beat=8, time=0),
        MetaMessage('set_tempo', tempo=500000, time=0),
        MetaMessage('set_tempo', tempo=555555, time=960),
        MetaMessage('set_tempo', tempo=500000, time=768),
        MetaMessage('end_of_track', time=576)]),
    MidiTrack([
        Message('note_on', channel=0, note=80, velocity=64, time=0),
        Message('note_off', channel=0, note=80, velocity=0, time=96),
        Message('note_on', channel=0, note=79, velocity=64, time=0),
        Message('note_off', channel=0, note=79, velocity=0, time=96),
        Message('note_on', channel=0, note=77, velocity=64, time=0),
        Message('note_off', channel=0, note=77, velocity=0, time=96),
        Message('note_on', channel=0, note=76, velocity=64, time=0),
        Message('note_off', channel=0, note=76, velocity=0, time=96),
        Message('note_on', channel=0, note=77, velocity=64, time=0),
        Message('note_off', channel=0, note=77, velocity=0, time=96),
        Message('note_on', channel=0, note=76, velocity=64, time=0),
        Message('note_off', channel=0, note=76, velocity=0, time=96),
        Message('note_on', channel=0, note=74, velocity=64, time=0),
        Message('note_off', channel=0, note=74, velocity=0, time=96),
        Message('note_on', channel=0, note=72, velocity=64, time=0),
        Message('note_off', channel=0, note=72, velocity=0, time=96),
        Message('note_on', channel=0, note=74, velocity=64, time=0),
        Message('note_off', channel=0, note=74, velocity=0, time=96),
        Message('note_on', channel=0, note=72, velocity=64, time=0),
        Message('note_off', channel=0, note=72, velocity=0, time=96),
        Message('note_on', channel=0, note=72, velocity=32, time=960),
        Message('note_off', channel=0, note=72, velocity=0, time=96),
        Message('note_on', channel=0, note=73, velocity=32, time=0),
        Message('note_off', channel=0, note=73, velocity=0, time=96),
        Message('note_on', channel=0, note=76, velocity=32, time=0),
        Message('note_off', channel=0, note=76, velocity=0, time=96),
        Message('note_on', channel=0, note=78, velocity=32, time=0),
        Message('note_off', channel=0, note=78, velocity=0, time=96)]),
    MidiTrack([
        Message('note_on', channel=1, note=70, velocity=64, time=96),
        Message('note_off', channel=1, note=70, velocity=0, time=96),
        Message('note_on', channel=1, note=69, velocity=64, time=0),
        Message('note_off', channel=1, note=69, velocity=0, time=96),
        Message('note_on', channel=1, note=66, velocity=64, time=0),
        Message('note_off', channel=1, note=66, velocity=0, time=96),
        Message('note_on', channel=1, note=67, velocity=64, time=0),
        Message('note_off', channel=1, note=67, velocity=0, time=384),
        Message('note_on', channel=1, note=67, velocity=64, time=576),
        Message('note_off', channel=1, note=67, velocity=0, time=192),
        Message('note_on', channel=1, note=67, velocity=64, time=192),
        Message('note_off', channel=1, note=67, velocity=0, time=192),
        Message('note_on', channel=1, note=66, velocity=96, time=0),
        Message('note_off', channel=1, note=66, velocity=0, time=384)]),
    MidiTrack([
        Message('note_on', channel=2, note=63, velocity=64, time=480),
        Message('note_off', channel=2, note=63, velocity=0, time=96),
        Message('note_on', channel=2, note=62, velocity=64, time=0),
        Message('note_off', channel=2, note=62, velocity=0, time=96),
        Message('note_on', channel=2, note=60, velocity=64, time=0),
        Message('note_off', channel=2, note=60, velocity=0, time=96),
        Message('note_on', channel=2, note=59, velocity=64, time=0),
        Message('note_off', channel=2, note=59, velocity=0, time=192),
        Message('note_on', channel=2, note=60, velocity=64, time=0),
        Message('note_off', channel=2, note=60, velocity=0, time=384),
        Message('note_on', channel=2, note=59, velocity=64, time=0),
        Message('note_off', channel=2, note=59, velocity=0, time=192),
        Message('note_on', channel=2, note=60, velocity=64, time=0),
        Message('note_off', channel=2, note=60, velocity=0, time=192),
        Message('note_on', channel=2, note=64, velocity=64, time=0),
        Message('note_off', channel=2, note=64, velocity=0, time=192),
        Message('note_on', channel=2, note=61, velocity=96, time=0),
        Message('note_on', channel=2, note=59, velocity=96, time=0),
        Message('note_off', channel=2, note=61, velocity=0, time=384),
        Message('note_off', channel=2, note=59, velocity=0, time=0)]),
    MidiTrack([
        Message('note_on', channel=3, note=49, velocity=48, time=1248),
        Message('note_off', channel=3, note=49, velocity=0, time=192),
        Message('note_on', channel=3, note=51, velocity=48, time=0),
        Message('note_off', channel=3, note=51, velocity=0, time=192),
        Message('note_on', channel=3, note=54, velocity=48, time=0),
        Message('note_off', channel=3, note=54, velocity=0, time=192),
        Message('note_on', channel=3, note=52, velocity=32, time=0),
        Message('note_off', channel=3, note=52, velocity=0, time=48),
        Message('note_on', channel=3, note=53, velocity=32, time=0),
        Message('note_off', channel=3, note=53, velocity=0, time=48),
        Message('note_on', channel=3, note=55, velocity=32, time=0),
        Message('note_off', channel=3, note=55, velocity=0, time=336)])
])

expected_trimmed_file = MidiFile(type=1, ticks_per_beat=192, tracks=[
    MidiTrack([
        MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                    notated_32nd_notes_per_beat=8, time=0),
        MetaMessage('set_tempo', tempo=500000, time=0),
        MetaMessage('track_name', name='Tempo Track', time=0),
        MetaMessage('end_of_track', time=768)]),
    MidiTrack([
        Message('note_on', channel=0, note=60, velocity=100, time=0),
        Message('note_off', channel=0, note=60, velocity=0, time=192),
        Message('note_on', channel=0, note=57, velocity=100, time=0),
        Message('note_off', channel=0, note=57, velocity=0, time=192)])
])

expected_sequence_ff = [
    [Event(0, 8, 0, 0, 500000, {80: EventNote(1.0, 80)}, False),
     Event(8, 8, 8, 0, 500000, {79: EventNote(1.0, 79)}, False),
     Event(8, 8, 16, 0, 500000, {77: EventNote(1.0, 77)}, False),
     Event(8, 8, 24, 0, 500000, {76: EventNote(1.0, 76)}, False),
     Event(8, 8, 32, 0, 500000, {77: EventNote(1.0, 77)}, False),
     Event(8, 8, 40, 0, 500000, {76: EventNote(1.0, 76)}, False),
     Event(8, 8, 48, 0, 500000, {74: EventNote(1.0, 74)}, False),
     Event(8, 8, 56, 0, 500000, {72: EventNote(1.0, 72)}, False),
     Event(8, 8, 64, 0, 500000, {74: EventNote(1.0, 74)}, False),
     Event(8, 8, 72, 0, 500000, {72: EventNote(1.0, 72)}, False),
     Event(8, 80, 80, 0, 555555, {}, False),
     Event(80, 8, 160, 0, 500000, {72: EventNote(1.0, 72)}, False),
     Event(8, 8, 168, 0, 500000, {73: EventNote(1.0, 73)}, False),
     Event(8, 8, 176, 0, 500000, {76: EventNote(1.0, 76)}, False),
     Event(8, 8, 184, 0, 500000, {78: EventNote(1.0, 78)}, False),
     Event(8, 0, 192, 0, 500000, {}, False)],
    [Event(0, 8, 0, 1, 500000, {}, False),
     Event(8, 8, 8, 1, 500000, {70: EventNote(1.0, 70)}, False),
     Event(8, 8, 16, 1, 500000, {69: EventNote(1.0, 69)}, False),
     Event(8, 8, 24, 1, 500000, {66: EventNote(1.0, 66)}, False),
     Event(8, 32, 32, 1, 500000, {67: EventNote(1.0, 67)}, False),
     Event(32, 48, 64, 1, 500000, {}, False),
     Event(48, 16, 112, 1, 555555, {67: EventNote(1.0, 67)}, False),
     Event(16, 16, 128, 1, 555555, {}, False),
     Event(16, 16, 144, 1, 500000, {67: EventNote(1.0, 67)}, False),
     Event(16, 32, 160, 1, 500000, {66: EventNote(1.0, 66)}, False),
     Event(32, 0, 192, 1, 500000, {}, False)],
    [Event(0, 40, 0, 2, 500000, {}, False),
     Event(40, 8, 40, 2, 500000, {63: EventNote(1.0, 63)}, False),
     Event(8, 8, 48, 2, 500000, {62: EventNote(1.0, 62)}, False),
     Event(8, 8, 56, 2, 500000, {60: EventNote(1.0, 60)}, False),
     Event(8, 16, 64, 2, 500000, {59: EventNote(1.0, 59)}, False),
     Event(16, 32, 80, 2, 555555, {60: EventNote(1.0, 60)}, False),
     Event(32, 16, 112, 2, 555555, {59: EventNote(1.0, 59)}, False),
     Event(16, 16, 128, 2, 555555, {60: EventNote(1.0, 60)}, False),
     Event(16, 16, 144, 2, 500000, {64: EventNote(1.0, 64)}, False),
     Event(16, 32, 160, 2, 500000, {59: EventNote(1.0, 59), 61: EventNote(1.0, 61)}, False),
     Event(32, 0, 192, 2, 500000, {}, False)],
    [Event(0, 104, 0, 3, 500000, {}, False),
     Event(104, 16, 104, 3, 555555, {49: EventNote(1.0, 49)}, False),
     Event(16, 16, 120, 3, 555555, {51: EventNote(1.0, 51)}, False),
     Event(16, 16, 136, 3, 555555, {54: EventNote(1.0, 54)}, False),
     Event(16, 4, 152, 3, 500000, {52: EventNote(1.0, 52)}, False),
     Event(4, 4, 156, 3, 500000, {53: EventNote(1.0, 53)}, False),
     Event(4, 28, 160, 3, 500000, {55: EventNote(1.0, 55)}, False),
     Event(28, 0, 188, 3, 500000, {}, False)]]

expected_sequence_ft = [[
    Event(0, 8, 0, 0, 500000, {80: EventNote(1.0, 80)}, False),
    Event(8, 8, 8, 0, 500000, {70: EventNote(1.0, 70), 79: EventNote(1.0, 79)}, False),
    Event(8, 8, 16, 0, 500000, {69: EventNote(1.0, 69), 77: EventNote(1.0, 77)}, False),
    Event(8, 8, 24, 0, 500000, {66: EventNote(1.0, 66), 76: EventNote(1.0, 76)}, False),
    Event(8, 8, 32, 0, 500000, {67: EventNote(1.0, 67), 77: EventNote(1.0, 77)}, False),
    Event(8, 8, 40, 0, 500000, {63: EventNote(1.0, 63), 67: EventNote(1.0, 67), 76: EventNote(1.0, 76)}, False),
    Event(8, 8, 48, 0, 500000, {62: EventNote(1.0, 62), 67: EventNote(1.0, 67), 74: EventNote(1.0, 74)}, False),
    Event(8, 8, 56, 0, 500000, {60: EventNote(1.0, 60), 67: EventNote(1.0, 67), 72: EventNote(1.0, 72)}, False),
    Event(8, 8, 64, 0, 500000, {59: EventNote(1.0, 59), 74: EventNote(1.0, 74)}, False),
    Event(8, 8, 72, 0, 500000, {59: EventNote(1.0, 59), 72: EventNote(1.0, 72)}, False),
    Event(8, 24, 80, 0, 555555, {60: EventNote(1.0, 60)}, False),
    Event(24, 8, 104, 0, 555555, {49: EventNote(1.0, 49), 60: EventNote(1.0, 60)}, False),
    Event(8, 8, 112, 0, 555555, {49: EventNote(1.0, 49), 59: EventNote(1.0, 59), 67: EventNote(1.0, 67)}, False),
    Event(8, 8, 120, 0, 555555, {51: EventNote(1.0, 51), 59: EventNote(1.0, 59), 67: EventNote(1.0, 67)}, False),
    Event(8, 8, 128, 0, 555555, {51: EventNote(1.0, 51), 60: EventNote(1.0, 60)}, False),
    Event(8, 8, 136, 0, 555555, {54: EventNote(1.0, 54), 60: EventNote(1.0, 60)}, False),
    Event(8, 8, 144, 0, 500000, {54: EventNote(1.0, 54), 64: EventNote(1.0, 64), 67: EventNote(1.0, 67)}, False),
    Event(8, 4, 152, 0, 500000, {52: EventNote(1.0, 52), 64: EventNote(1.0, 64), 67: EventNote(1.0, 67)}, False),
    Event(4, 4, 156, 0, 500000, {53: EventNote(1.0, 53), 64: EventNote(1.0, 64), 67: EventNote(1.0, 67)}, False),
    Event(4, 8, 160, 0, 500000,
          {55: EventNote(1.0, 55), 59: EventNote(1.0, 59), 61: EventNote(1.0, 61), 66: EventNote(1.0, 66),
           72: EventNote(1.0, 72)}, False),
    Event(8, 8, 168, 0, 500000,
          {55: EventNote(1.0, 55), 59: EventNote(1.0, 59), 61: EventNote(1.0, 61), 66: EventNote(1.0, 66),
           73: EventNote(1.0, 73)}, False),
    Event(8, 8, 176, 0, 500000,
          {55: EventNote(1.0, 55), 59: EventNote(1.0, 59), 61: EventNote(1.0, 61), 66: EventNote(1.0, 66),
           76: EventNote(1.0, 76)}, False),
    Event(8, 4, 184, 0, 500000,
          {55: EventNote(1.0, 55), 59: EventNote(1.0, 59), 61: EventNote(1.0, 61), 66: EventNote(1.0, 66),
           78: EventNote(1.0, 78)}, False),
    Event(4, 4, 188, 0, 500000,
          {59: EventNote(1.0, 59), 61: EventNote(1.0, 61), 66: EventNote(1.0, 66), 78: EventNote(1.0, 78)}, False),
    Event(4, 0, 192, 0, 500000, {}, False)]]

expected_sequence_tff = [
    [Event(0, 8, 0, 0, 500000, {80: EventNote(0.5, 80)}, True),
     Event(8, 8, 8, 0, 500000, {79: EventNote(0.5, 79)}, True),
     Event(8, 8, 16, 0, 500000, {77: EventNote(0.5, 77)}, True),
     Event(8, 8, 24, 0, 500000, {76: EventNote(0.5, 76)}, True),
     Event(8, 8, 32, 0, 500000, {77: EventNote(0.5, 77)}, True),
     Event(8, 8, 40, 0, 500000, {76: EventNote(0.5, 76)}, True),
     Event(8, 8, 48, 0, 500000, {74: EventNote(0.5, 74)}, True),
     Event(8, 8, 56, 0, 500000, {72: EventNote(0.5, 72)}, True),
     Event(8, 8, 64, 0, 500000, {74: EventNote(0.5, 74)}, True),
     Event(8, 8, 72, 0, 500000, {72: EventNote(0.5, 72)}, True),
     Event(8, 80, 80, 0, 555555, {}, True),
     Event(80, 8, 160, 0, 500000, {72: EventNote(0.25, 72)}, True),
     Event(8, 8, 168, 0, 500000, {73: EventNote(0.25, 73)}, True),
     Event(8, 8, 176, 0, 500000, {76: EventNote(0.25, 76)}, True),
     Event(8, 8, 184, 0, 500000, {78: EventNote(0.25, 78)}, True),
     Event(8, 0, 192, 0, 500000, {}, True)],
    [Event(0, 8, 0, 1, 500000, {}, True),
     Event(8, 8, 8, 1, 500000, {70: EventNote(0.5, 70)}, True),
     Event(8, 8, 16, 1, 500000, {69: EventNote(0.5, 69)}, True),
     Event(8, 8, 24, 1, 500000, {66: EventNote(0.5, 66)}, True),
     Event(8, 32, 32, 1, 500000, {67: EventNote(0.5, 67)}, True),
     Event(32, 48, 64, 1, 500000, {}, True),
     Event(48, 16, 112, 1, 555555, {67: EventNote(0.5, 67)}, True),
     Event(16, 16, 128, 1, 555555, {}, True),
     Event(16, 16, 144, 1, 500000, {67: EventNote(0.5, 67)}, True),
     Event(16, 32, 160, 1, 500000, {66: EventNote(0.75, 66)}, True),
     Event(32, 0, 192, 1, 500000, {}, True)],
    [Event(0, 40, 0, 2, 500000, {}, True),
     Event(40, 8, 40, 2, 500000, {63: EventNote(0.5, 63)}, True),
     Event(8, 8, 48, 2, 500000, {62: EventNote(0.5, 62)}, True),
     Event(8, 8, 56, 2, 500000, {60: EventNote(0.5, 60)}, True),
     Event(8, 16, 64, 2, 500000, {59: EventNote(0.5, 59)}, True),
     Event(16, 32, 80, 2, 555555, {60: EventNote(0.5, 60)}, True),
     Event(32, 16, 112, 2, 555555, {59: EventNote(0.5, 59)}, True),
     Event(16, 16, 128, 2, 555555, {60: EventNote(0.5, 60)}, True),
     Event(16, 16, 144, 2, 500000, {64: EventNote(0.5, 64)}, True),
     Event(16, 32, 160, 2, 500000, {59: EventNote(0.75, 59), 61: EventNote(0.75, 61)}, True),
     Event(32, 0, 192, 2, 500000, {}, True)],
    [Event(0, 104, 0, 3, 500000, {}, True),
     Event(104, 16, 104, 3, 555555, {49: EventNote(0.375, 49)}, True),
     Event(16, 16, 120, 3, 555555, {51: EventNote(0.375, 51)}, True),
     Event(16, 16, 136, 3, 555555, {54: EventNote(0.375, 54)}, True),
     Event(16, 4, 152, 3, 500000, {52: EventNote(0.25, 52)}, True),
     Event(4, 4, 156, 3, 500000, {53: EventNote(0.25, 53)}, True),
     Event(4, 28, 160, 3, 500000, {55: EventNote(0.25, 55)}, True),
     Event(28, 0, 188, 3, 500000, {}, True)]]

expected_sequence_tft = [
    [Event(0, 8, 0, 0, 500000, {80: EventNote(0.6666666666666666, 80)}, True),
     Event(8, 8, 8, 0, 500000, {79: EventNote(0.6666666666666666, 79)}, True),
     Event(8, 8, 16, 0, 500000, {77: EventNote(0.6666666666666666, 77)}, True),
     Event(8, 8, 24, 0, 500000, {76: EventNote(0.6666666666666666, 76)}, True),
     Event(8, 8, 32, 0, 500000, {77: EventNote(0.6666666666666666, 77)}, True),
     Event(8, 8, 40, 0, 500000, {76: EventNote(0.6666666666666666, 76)}, True),
     Event(8, 8, 48, 0, 500000, {74: EventNote(0.6666666666666666, 74)}, True),
     Event(8, 8, 56, 0, 500000, {72: EventNote(0.6666666666666666, 72)}, True),
     Event(8, 8, 64, 0, 500000, {74: EventNote(0.6666666666666666, 74)}, True),
     Event(8, 8, 72, 0, 500000, {72: EventNote(0.6666666666666666, 72)}, True),
     Event(8, 80, 80, 0, 555555, {}, True),
     Event(80, 8, 160, 0, 500000, {72: EventNote(0.3333333333333333, 72)}, True),
     Event(8, 8, 168, 0, 500000, {73: EventNote(0.3333333333333333, 73)}, True),
     Event(8, 8, 176, 0, 500000, {76: EventNote(0.3333333333333333, 76)}, True),
     Event(8, 8, 184, 0, 500000, {78: EventNote(0.3333333333333333, 78)}, True),
     Event(8, 0, 192, 0, 500000, {}, True)],
    [Event(0, 8, 0, 1, 500000, {}, True),
     Event(8, 8, 8, 1, 500000, {70: EventNote(0.6666666666666666, 70)}, True),
     Event(8, 8, 16, 1, 500000, {69: EventNote(0.6666666666666666, 69)}, True),
     Event(8, 8, 24, 1, 500000, {66: EventNote(0.6666666666666666, 66)}, True),
     Event(8, 32, 32, 1, 500000, {67: EventNote(0.6666666666666666, 67)}, True),
     Event(32, 48, 64, 1, 500000, {}, True),
     Event(48, 16, 112, 1, 555555, {67: EventNote(0.6666666666666666, 67)}, True),
     Event(16, 16, 128, 1, 555555, {}, True),
     Event(16, 16, 144, 1, 500000, {67: EventNote(0.6666666666666666, 67)}, True),
     Event(16, 32, 160, 1, 500000, {66: EventNote(1.0, 66)}, True),
     Event(32, 0, 192, 1, 500000, {}, True)],
    [Event(0, 40, 0, 2, 500000, {}, True),
     Event(40, 8, 40, 2, 500000, {63: EventNote(0.6666666666666666, 63)}, True),
     Event(8, 8, 48, 2, 500000, {62: EventNote(0.6666666666666666, 62)}, True),
     Event(8, 8, 56, 2, 500000, {60: EventNote(0.6666666666666666, 60)}, True),
     Event(8, 16, 64, 2, 500000, {59: EventNote(0.6666666666666666, 59)}, True),
     Event(16, 32, 80, 2, 555555, {60: EventNote(0.6666666666666666, 60)}, True),
     Event(32, 16, 112, 2, 555555, {59: EventNote(0.6666666666666666, 59)}, True),
     Event(16, 16, 128, 2, 555555, {60: EventNote(0.6666666666666666, 60)}, True),
     Event(16, 16, 144, 2, 500000, {64: EventNote(0.6666666666666666, 64)}, True),
     Event(16, 32, 160, 2, 500000, {59: EventNote(1.0, 59), 61: EventNote(1.0, 61)}, True),
     Event(32, 0, 192, 2, 500000, {}, True)],
    [Event(0, 104, 0, 3, 500000, {}, True),
     Event(104, 16, 104, 3, 555555, {49: EventNote(0.5, 49)}, True),
     Event(16, 16, 120, 3, 555555, {51: EventNote(0.5, 51)}, True),
     Event(16, 16, 136, 3, 555555, {54: EventNote(0.5, 54)}, True),
     Event(16, 4, 152, 3, 500000, {52: EventNote(0.3333333333333333, 52)}, True),
     Event(4, 4, 156, 3, 500000, {53: EventNote(0.3333333333333333, 53)}, True),
     Event(4, 28, 160, 3, 500000, {55: EventNote(0.3333333333333333, 55)}, True),
     Event(28, 0, 188, 3, 500000, {}, True)]]

expected_sequence_ttf = [[
    Event(0, 8, 0, 0, 500000, {80: EventNote(0.5, 80)}, True),
    Event(8, 8, 8, 0, 500000, {70: EventNote(0.5, 70), 79: EventNote(0.5, 79)}, True),
    Event(8, 8, 16, 0, 500000, {69: EventNote(0.5, 69), 77: EventNote(0.5, 77)}, True),
    Event(8, 8, 24, 0, 500000, {66: EventNote(0.5, 66), 76: EventNote(0.5, 76)}, True),
    Event(8, 8, 32, 0, 500000, {67: EventNote(0.5, 67), 77: EventNote(0.5, 77)}, True),
    Event(8, 8, 40, 0, 500000, {63: EventNote(0.5, 63), 67: EventNote(0.5, 67), 76: EventNote(0.5, 76)}, True),
    Event(8, 8, 48, 0, 500000, {62: EventNote(0.5, 62), 67: EventNote(0.5, 67), 74: EventNote(0.5, 74)}, True),
    Event(8, 8, 56, 0, 500000, {60: EventNote(0.5, 60), 67: EventNote(0.5, 67), 72: EventNote(0.5, 72)}, True),
    Event(8, 8, 64, 0, 500000, {59: EventNote(0.5, 59), 74: EventNote(0.5, 74)}, True),
    Event(8, 8, 72, 0, 500000, {59: EventNote(0.5, 59), 72: EventNote(0.5, 72)}, True),
    Event(8, 24, 80, 0, 555555, {60: EventNote(0.5, 60)}, True),
    Event(24, 8, 104, 0, 555555, {49: EventNote(0.375, 49), 60: EventNote(0.5, 60)}, True),
    Event(8, 8, 112, 0, 555555, {49: EventNote(0.375, 49), 59: EventNote(0.5, 59), 67: EventNote(0.5, 67)}, True),
    Event(8, 8, 120, 0, 555555, {51: EventNote(0.375, 51), 59: EventNote(0.5, 59), 67: EventNote(0.5, 67)}, True),
    Event(8, 8, 128, 0, 555555, {51: EventNote(0.375, 51), 60: EventNote(0.5, 60)}, True),
    Event(8, 8, 136, 0, 555555, {54: EventNote(0.375, 54), 60: EventNote(0.5, 60)}, True),
    Event(8, 8, 144, 0, 500000, {54: EventNote(0.375, 54), 64: EventNote(0.5, 64), 67: EventNote(0.5, 67)}, True),
    Event(8, 4, 152, 0, 500000, {52: EventNote(0.25, 52), 64: EventNote(0.5, 64), 67: EventNote(0.5, 67)}, True),
    Event(4, 4, 156, 0, 500000, {53: EventNote(0.25, 53), 64: EventNote(0.5, 64), 67: EventNote(0.5, 67)}, True),
    Event(4, 8, 160, 0, 500000,
          {55: EventNote(0.25, 55), 59: EventNote(0.75, 59), 61: EventNote(0.75, 61), 66: EventNote(0.75, 66),
           72: EventNote(0.25, 72)}, True),
    Event(8, 8, 168, 0, 500000,
          {55: EventNote(0.25, 55), 59: EventNote(0.75, 59), 61: EventNote(0.75, 61), 66: EventNote(0.75, 66),
           73: EventNote(0.25, 73)}, True),
    Event(8, 8, 176, 0, 500000,
          {55: EventNote(0.25, 55), 59: EventNote(0.75, 59), 61: EventNote(0.75, 61), 66: EventNote(0.75, 66),
           76: EventNote(0.25, 76)}, True),
    Event(8, 4, 184, 0, 500000,
          {55: EventNote(0.25, 55), 59: EventNote(0.75, 59), 61: EventNote(0.75, 61), 66: EventNote(0.75, 66),
           78: EventNote(0.25, 78)}, True),
    Event(4, 4, 188, 0, 500000,
          {59: EventNote(0.75, 59), 61: EventNote(0.75, 61), 66: EventNote(0.75, 66), 78: EventNote(0.25, 78)}, True),
    Event(4, 0, 192, 0, 500000, {}, True)]]

expected_sequence_ttt = [[
    Event(0, 8, 0, 0, 500000, {80: EventNote(0.6666666666666666, 80)}, True),
    Event(8, 8, 8, 0, 500000, {70: EventNote(0.6666666666666666, 70), 79: EventNote(0.6666666666666666, 79)}, True),
    Event(8, 8, 16, 0, 500000, {69: EventNote(0.6666666666666666, 69), 77: EventNote(0.6666666666666666, 77)}, True),
    Event(8, 8, 24, 0, 500000, {66: EventNote(0.6666666666666666, 66), 76: EventNote(0.6666666666666666, 76)}, True),
    Event(8, 8, 32, 0, 500000, {67: EventNote(0.6666666666666666, 67), 77: EventNote(0.6666666666666666, 77)}, True),
    Event(8, 8, 40, 0, 500000, {63: EventNote(0.6666666666666666, 63), 67: EventNote(0.6666666666666666, 67),
                                76: EventNote(0.6666666666666666, 76)}, True),
    Event(8, 8, 48, 0, 500000, {62: EventNote(0.6666666666666666, 62), 67: EventNote(0.6666666666666666, 67),
                                74: EventNote(0.6666666666666666, 74)}, True),
    Event(8, 8, 56, 0, 500000, {60: EventNote(0.6666666666666666, 60), 67: EventNote(0.6666666666666666, 67),
                                72: EventNote(0.6666666666666666, 72)}, True),
    Event(8, 8, 64, 0, 500000, {59: EventNote(0.6666666666666666, 59), 74: EventNote(0.6666666666666666, 74)}, True),
    Event(8, 8, 72, 0, 500000, {59: EventNote(0.6666666666666666, 59), 72: EventNote(0.6666666666666666, 72)}, True),
    Event(8, 24, 80, 0, 555555, {60: EventNote(0.6666666666666666, 60)}, True),
    Event(24, 8, 104, 0, 555555, {49: EventNote(0.5, 49), 60: EventNote(0.6666666666666666, 60)}, True),
    Event(8, 8, 112, 0, 555555,
          {49: EventNote(0.5, 49), 59: EventNote(0.6666666666666666, 59), 67: EventNote(0.6666666666666666, 67)}, True),
    Event(8, 8, 120, 0, 555555,
          {51: EventNote(0.5, 51), 59: EventNote(0.6666666666666666, 59), 67: EventNote(0.6666666666666666, 67)}, True),
    Event(8, 8, 128, 0, 555555, {51: EventNote(0.5, 51), 60: EventNote(0.6666666666666666, 60)}, True),
    Event(8, 8, 136, 0, 555555, {54: EventNote(0.5, 54), 60: EventNote(0.6666666666666666, 60)}, True),
    Event(8, 8, 144, 0, 500000,
          {54: EventNote(0.5, 54), 64: EventNote(0.6666666666666666, 64), 67: EventNote(0.6666666666666666, 67)}, True),
    Event(8, 4, 152, 0, 500000, {52: EventNote(0.3333333333333333, 52), 64: EventNote(0.6666666666666666, 64),
                                 67: EventNote(0.6666666666666666, 67)}, True),
    Event(4, 4, 156, 0, 500000, {53: EventNote(0.3333333333333333, 53), 64: EventNote(0.6666666666666666, 64),
                                 67: EventNote(0.6666666666666666, 67)}, True),
    Event(4, 8, 160, 0, 500000, {55: EventNote(0.3333333333333333, 55), 59: EventNote(1.0, 59), 61: EventNote(1.0, 61),
                                 66: EventNote(1.0, 66), 72: EventNote(0.3333333333333333, 72)}, True),
    Event(8, 8, 168, 0, 500000, {55: EventNote(0.3333333333333333, 55), 59: EventNote(1.0, 59), 61: EventNote(1.0, 61),
                                 66: EventNote(1.0, 66), 73: EventNote(0.3333333333333333, 73)}, True),
    Event(8, 8, 176, 0, 500000, {55: EventNote(0.3333333333333333, 55), 59: EventNote(1.0, 59), 61: EventNote(1.0, 61),
                                 66: EventNote(1.0, 66), 76: EventNote(0.3333333333333333, 76)}, True),
    Event(8, 4, 184, 0, 500000, {55: EventNote(0.3333333333333333, 55), 59: EventNote(1.0, 59), 61: EventNote(1.0, 61),
                                 66: EventNote(1.0, 66), 78: EventNote(0.3333333333333333, 78)}, True),
    Event(4, 4, 188, 0, 500000, {59: EventNote(1.0, 59), 61: EventNote(1.0, 61), 66: EventNote(1.0, 66),
                                 78: EventNote(0.3333333333333333, 78)}, True),
    Event(4, 0, 192, 0, 500000, {}, True)]]

expected_events_f = [
    [Event(0, 8, 0, 0, 500000, {80: EventNote(1.0, 80)}, False),
     Event(8, 8, 8, 0, 500000, {79: EventNote(1.0, 79)}, False),
     Event(8, 8, 16, 0, 500000, {77: EventNote(1.0, 77)}, False),
     Event(8, 8, 24, 0, 500000, {76: EventNote(1.0, 76)}, False),
     Event(8, 8, 32, 0, 500000, {77: EventNote(1.0, 77)}, False),
     Event(8, 8, 40, 0, 500000, {76: EventNote(1.0, 76)}, False),
     Event(8, 8, 48, 0, 500000, {74: EventNote(1.0, 74)}, False),
     Event(8, 8, 56, 0, 500000, {72: EventNote(1.0, 72)}, False),
     Event(8, 8, 64, 0, 500000, {74: EventNote(1.0, 74)}, False),
     Event(8, 8, 72, 0, 500000, {72: EventNote(1.0, 72)}, False),
     Event(8, 80, 80, 0, 555555, {}, False),
     Event(80, 8, 160, 0, 500000, {72: EventNote(1.0, 72)}, False),
     Event(8, 8, 168, 0, 500000, {73: EventNote(1.0, 73)}, False),
     Event(8, 8, 176, 0, 500000, {76: EventNote(1.0, 76)}, False),
     Event(8, 8, 184, 0, 500000, {78: EventNote(1.0, 78)}, False),
     Event(8, 0, 192, 0, 500000, {}, False)],
    [Event(0, 8, 0, 1, 500000, {}, False),
     Event(8, 8, 8, 1, 500000, {70: EventNote(1.0, 70)}, False),
     Event(8, 8, 16, 1, 500000, {69: EventNote(1.0, 69)}, False),
     Event(8, 8, 24, 1, 500000, {66: EventNote(1.0, 66)}, False),
     Event(8, 32, 32, 1, 500000, {67: EventNote(1.0, 67)}, False),
     Event(32, 48, 64, 1, 500000, {}, False),
     Event(48, 16, 112, 1, 555555, {67: EventNote(1.0, 67)}, False),
     Event(16, 16, 128, 1, 555555, {}, False),
     Event(16, 16, 144, 1, 500000, {67: EventNote(1.0, 67)}, False),
     Event(16, 32, 160, 1, 500000, {66: EventNote(1.0, 66)}, False),
     Event(32, 0, 192, 1, 500000, {}, False)],
    [Event(0, 40, 0, 2, 500000, {}, False),
     Event(40, 8, 40, 2, 500000, {63: EventNote(1.0, 63)}, False),
     Event(8, 8, 48, 2, 500000, {62: EventNote(1.0, 62)}, False),
     Event(8, 8, 56, 2, 500000, {60: EventNote(1.0, 60)}, False),
     Event(8, 16, 64, 2, 500000, {59: EventNote(1.0, 59)}, False),
     Event(16, 32, 80, 2, 555555, {60: EventNote(1.0, 60)}, False),
     Event(32, 16, 112, 2, 555555, {59: EventNote(1.0, 59)}, False),
     Event(16, 16, 128, 2, 555555, {60: EventNote(1.0, 60)}, False),
     Event(16, 16, 144, 2, 500000, {64: EventNote(1.0, 64)}, False),
     Event(16, 32, 160, 2, 500000, {59: EventNote(1.0, 59), 61: EventNote(1.0, 61)}, False),
     Event(32, 0, 192, 2, 500000, {}, False)],
    [Event(0, 104, 0, 3, 500000, {}, False),
     Event(104, 16, 104, 3, 555555, {49: EventNote(1.0, 49)}, False),
     Event(16, 16, 120, 3, 555555, {51: EventNote(1.0, 51)}, False),
     Event(16, 16, 136, 3, 555555, {54: EventNote(1.0, 54)}, False),
     Event(16, 4, 152, 3, 500000, {52: EventNote(1.0, 52)}, False),
     Event(4, 4, 156, 3, 500000, {53: EventNote(1.0, 53)}, False),
     Event(4, 28, 160, 3, 500000, {55: EventNote(1.0, 55)}, False),
     Event(28, 0, 188, 3, 500000, {}, False)]]

expected_events_t = [
    [Event(0, 8, 0, 0, 500000, {80: EventNote(64.0, 80)}, True),
     Event(8, 8, 8, 0, 500000, {79: EventNote(64.0, 79)}, True),
     Event(8, 8, 16, 0, 500000, {77: EventNote(64.0, 77)}, True),
     Event(8, 8, 24, 0, 500000, {76: EventNote(64.0, 76)}, True),
     Event(8, 8, 32, 0, 500000, {77: EventNote(64.0, 77)}, True),
     Event(8, 8, 40, 0, 500000, {76: EventNote(64.0, 76)}, True),
     Event(8, 8, 48, 0, 500000, {74: EventNote(64.0, 74)}, True),
     Event(8, 8, 56, 0, 500000, {72: EventNote(64.0, 72)}, True),
     Event(8, 8, 64, 0, 500000, {74: EventNote(64.0, 74)}, True),
     Event(8, 8, 72, 0, 500000, {72: EventNote(64.0, 72)}, True),
     Event(8, 80, 80, 0, 555555, {}, True),
     Event(80, 8, 160, 0, 500000, {72: EventNote(32.0, 72)}, True),
     Event(8, 8, 168, 0, 500000, {73: EventNote(32.0, 73)}, True),
     Event(8, 8, 176, 0, 500000, {76: EventNote(32.0, 76)}, True),
     Event(8, 8, 184, 0, 500000, {78: EventNote(32.0, 78)}, True),
     Event(8, 0, 192, 0, 500000, {}, True)],
    [Event(0, 8, 0, 1, 500000, {}, True),
     Event(8, 8, 8, 1, 500000, {70: EventNote(64.0, 70)}, True),
     Event(8, 8, 16, 1, 500000, {69: EventNote(64.0, 69)}, True),
     Event(8, 8, 24, 1, 500000, {66: EventNote(64.0, 66)}, True),
     Event(8, 32, 32, 1, 500000, {67: EventNote(64.0, 67)}, True),
     Event(32, 48, 64, 1, 500000, {}, True),
     Event(48, 16, 112, 1, 555555, {67: EventNote(64.0, 67)}, True),
     Event(16, 16, 128, 1, 555555, {}, True),
     Event(16, 16, 144, 1, 500000, {67: EventNote(64.0, 67)}, True),
     Event(16, 32, 160, 1, 500000, {66: EventNote(96.0, 66)}, True),
     Event(32, 0, 192, 1, 500000, {}, True)],
    [Event(0, 40, 0, 2, 500000, {}, True),
     Event(40, 8, 40, 2, 500000, {63: EventNote(64.0, 63)}, True),
     Event(8, 8, 48, 2, 500000, {62: EventNote(64.0, 62)}, True),
     Event(8, 8, 56, 2, 500000, {60: EventNote(64.0, 60)}, True),
     Event(8, 16, 64, 2, 500000, {59: EventNote(64.0, 59)}, True),
     Event(16, 32, 80, 2, 555555, {60: EventNote(64.0, 60)}, True),
     Event(32, 16, 112, 2, 555555, {59: EventNote(64.0, 59)}, True),
     Event(16, 16, 128, 2, 555555, {60: EventNote(64.0, 60)}, True),
     Event(16, 16, 144, 2, 500000, {64: EventNote(64.0, 64)}, True),
     Event(16, 32, 160, 2, 500000, {59: EventNote(96.0, 59), 61: EventNote(96.0, 61)}, True),
     Event(32, 0, 192, 2, 500000, {}, True)],
    [Event(0, 104, 0, 3, 500000, {}, True),
     Event(104, 16, 104, 3, 555555, {49: EventNote(48.0, 49)}, True),
     Event(16, 16, 120, 3, 555555, {51: EventNote(48.0, 51)}, True),
     Event(16, 16, 136, 3, 555555, {54: EventNote(48.0, 54)}, True),
     Event(16, 4, 152, 3, 500000, {52: EventNote(32.0, 52)}, True),
     Event(4, 4, 156, 3, 500000, {53: EventNote(32.0, 53)}, True),
     Event(4, 28, 160, 3, 500000, {55: EventNote(32.0, 55)}, True),
     Event(28, 0, 188, 3, 500000, {}, True)]]


def test_class_event_note_init_int():
    note = EventNote(25, 60)

    assert isinstance(note, EventNote)
    assert isinstance(note.velocity, float)
    assert note.velocity == float(25)
    assert note.height == 60
    assert note.tone == 1
    assert note.octave == 4


def test_class_event_note_normalise_int():
    note = EventNote(64, 64)
    note.normalise(128)

    assert isinstance(note.velocity, float)
    assert note.velocity == float(0.5)


def test_class_active_element_init_bool():
    element = ActiveElement(60, True, False)

    assert isinstance(element, ActiveElement)
    assert element.height == 60
    assert element.value is True
    assert element.use_velocities is False


def test_class_active_element_init_int():
    element = ActiveElement(60, 30, True)

    assert isinstance(element, ActiveElement)
    assert isinstance(element.value, float)
    assert element.height == 60
    assert element.value == float(30)
    assert element.use_velocities is True


def test_class_event_init_booleans_mode():
    event = Event(200, 100, 1000, 1, 500000, dictionary, False)

    assert isinstance(event, Event)
    assert event.time == 200
    assert event.length == 100
    assert event.offset == 1000
    assert event.track == 1
    assert event.tempo == 500000
    assert event.use_velocities is False

    assert isinstance(event.all_notes, list)
    assert event.all_notes == expected_booleans

    assert isinstance(event.active_notes, list)
    assert isinstance(event.active_notes[0], ActiveElement)
    assert isinstance(event.active_notes[1], ActiveElement)
    assert isinstance(event.active_notes[2], ActiveElement)
    assert event.active_notes[0] == ActiveElement(64, True, False)
    assert event.active_notes[1] == ActiveElement(65, True, False)
    assert event.active_notes[2] == ActiveElement(67, True, False)


def test_class_event_init_velocities_mode():
    event = Event(200, 100, 5000, 1, 500000, dictionary, True)

    assert isinstance(event, Event)
    assert event.time == 200
    assert event.length == 100
    assert event.offset == 5000
    assert event.track == 1
    assert event.tempo == 500000
    assert event.use_velocities is True

    assert isinstance(event.all_notes, list)
    assert event.all_notes == expected_velocities

    assert isinstance(event.active_notes, list)
    assert isinstance(event.active_notes[0], ActiveElement)
    assert isinstance(event.active_notes[1], ActiveElement)
    assert isinstance(event.active_notes[2], ActiveElement)
    assert event.active_notes[0] == ActiveElement(64, 64, True)
    assert event.active_notes[1] == ActiveElement(65, 64, True)
    assert event.active_notes[2] == ActiveElement(67, 64, True)


def test_class_event_normalise_int():
    d = dict[int, EventNote]()
    d[64] = EventNote(64, 64)
    event = Event(200, 100, 1000, 1, 500000, d, True)
    event.normalise(128)

    expected = [0.0] * 64
    expected.append(0.5)
    expected.extend([0.0] * 63)

    assert isinstance(event.all_notes, list)
    assert event.all_notes == expected


def test_get_offset():
    offset = get_offset(63, 22, 16)

    assert isinstance(offset, int)
    assert offset == 4


def test_get_midi_length():
    file = MidiFile(file_polyphony_folder + file_2_name + '.mid')
    length = get_midi_length(file, float(12))

    assert isinstance(length, int)
    assert length == 192


def test_get_filename_correct():
    filename = get_filename('test/relative/path/file.mid')

    assert isinstance(filename, str)
    assert filename == 'file'


def test_get_filename_incorrect():
    with pytest.raises(TypeError):
        _ = get_filename('test/relative/path/file.pdf')


def test_open_file_correct():
    file, filename, accuracy = open_file(file_polyphony_folder + file_2_name + '.mid')

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(accuracy, float)
    assert filename == 'test_tempos_velocities_and_polyphony'
    assert accuracy == float(12)


def test_open_file_corrupt():
    with pytest.raises(ImportError):
        _, _, _ = open_file(file_types_folder + file_4_name + '.mid')


def test_get_tempo_array():
    file = MidiFile(file_polyphony_folder + file_2_name + '.mid')
    tempos = get_tempo_array(file, 192, 12)

    assert isinstance(tempos, list)
    assert tempos == expected_tempos


def test_export_tempo_array_trimmed():
    tempos = export_tempo_array(file_types_folder + file_6_name + '.mid', True)

    assert isinstance(tempos, list)
    assert tempos == expected_trimmed_tempos[:-1]


def test_export_tempo_array_untrimmed():
    tempos = export_tempo_array(file_types_folder + file_6_name + '.mid', False)

    assert isinstance(tempos, list)
    assert tempos == expected_untrimmed_tempos[:-1]


def test_combine_and_clean_tracks():
    file = MidiFile(file_polyphony_folder + file_2_name + '.mid')
    tracks = file.tracks[1:]
    out_track = combine_and_clean_tracks(tracks)

    assert isinstance(out_track, MidiTrack)
    assert out_track == expected_midi_track


def test_get_max_velocity():
    file = MidiFile(file_polyphony_folder + file_2_name + '.mid')
    tracks = file.tracks[1:]
    velocity = get_max_velocity(tracks)

    assert isinstance(velocity, int)
    assert velocity == 96


def test_check_file_type_0():
    file = MidiFile(file_types_folder + file_3_name + '.mid')

    with pytest.raises(ValueError):
        check_file_type(file)


def test_check_file_type_1():
    file = MidiFile(file_types_folder + file_6_name + '.mid')
    check_file_type(file)


def test_check_file_type_2():
    file = MidiFile(file_types_folder + file_7_name + '.mid')

    with pytest.raises(ValueError):
        check_file_type(file)


def test_export_output_booleans_mode():
    output = get_array_of_notes(file_polyphony_folder + file_2_name + '.mid', True, False)
    if not os.path.exists('test_outputs'):
        os.makedirs('test_outputs')

    export_output('test_outputs', 'output_AVF', output)
    assert filecmp.cmp(file_polyphony_folder + 'AVF.npy', 'test_outputs/output_AVF.npy')

    os.remove('test_outputs/output_AVF.npy')
    os.rmdir('test_outputs')


def test_export_output_sequences_mode():
    output = get_sequence_of_notes(file_polyphony_folder + file_2_name + '.mid', False, True, True)
    if not os.path.exists('test_outputs'):
        os.makedirs('test_outputs')

    export_output('test_outputs', 'output_SBTT', output)
    assert filecmp.cmp(file_polyphony_folder + 'SBTT.npy', 'test_outputs/output_SBTT.npy')

    os.remove('test_outputs/output_SBTT.npy')
    os.rmdir('test_outputs')


def test_prepare_file_empty():
    with pytest.raises(ValueError):
        _, _, _, _, _ = prepare_file(file_types_folder + file_5_name + '.mid', True)


def test_prepare_file_joined_mode():
    file, filename, accuracy, length, tempos = prepare_file(file_polyphony_folder + file_2_name + '.mid', True)

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(accuracy, float)
    assert isinstance(length, int)
    assert isinstance(tempos, list)

    assert repr(file) == repr(expected_prepared_file_with_join)
    assert filename == 'test_tempos_velocities_and_polyphony'
    assert accuracy == float(12)
    assert length == 192
    assert tempos == expected_tempos


def test_prepare_file_separated_mode():
    file, filename, accuracy, length, tempos = prepare_file(file_polyphony_folder + file_2_name + '.mid', False)

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(accuracy, float)
    assert isinstance(length, int)
    assert isinstance(tempos, list)

    assert repr(file) == repr(expected_prepared_file_without_join)
    assert filename == 'test_tempos_velocities_and_polyphony'
    assert accuracy == float(12)
    assert length == 192
    assert tempos == expected_tempos


def test_prepare_file_untrimmed():
    file, filename, accuracy, length, tempos = prepare_file(file_types_folder + file_6_name + '.mid', False)

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(accuracy, float)
    assert isinstance(length, int)
    assert isinstance(tempos, list)

    assert repr(file) == repr(expected_trimmed_file)
    assert filename == 'test_type_1_untrimmed'
    assert accuracy == float(12)
    assert length == 32
    assert tempos == expected_trimmed_tempos


def test_get_lists_of_events_booleans_mode():
    events = get_lists_of_events(expected_prepared_file_without_join, float(12), expected_tempos, False)

    assert isinstance(events, list)
    assert events == expected_events_f


def test_get_lists_of_events_velocities_mode():
    events = get_lists_of_events(expected_prepared_file_without_join, float(12), expected_tempos, True)

    assert isinstance(events, list)
    assert events == expected_events_t


def test_initialise_sequences_booleans_f_mode():
    file, filename, length, initial_sequences = initialise_sequences(file_polyphony_folder + file_2_name + '.mid',
                                                                     False, False, False)

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(length, int)
    assert isinstance(initial_sequences, list)

    assert repr(file) == repr(expected_prepared_file_without_join)
    assert filename == 'test_tempos_velocities_and_polyphony'
    assert length == 192
    assert initial_sequences == expected_sequence_ff


def test_initialise_sequences_booleans_t_mode():
    file, filename, length, initial_sequences = initialise_sequences(file_polyphony_folder + file_2_name + '.mid',
                                                                     False, True, False)

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(length, int)
    assert isinstance(initial_sequences, list)

    assert repr(file) == repr(expected_prepared_file_with_join)
    assert filename == 'test_tempos_velocities_and_polyphony'
    assert length == 192
    assert initial_sequences == expected_sequence_ft


def test_initialise_sequences_velocities_ff_mode():
    file, filename, length, initial_sequences = initialise_sequences(file_polyphony_folder + file_2_name + '.mid',
                                                                     True, False, False)

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(length, int)
    assert isinstance(initial_sequences, list)

    assert repr(file) == repr(expected_prepared_file_without_join)
    # assert file == expected_prepared_file_without_join  # TODO - talk with Marcin about this
    assert filename == 'test_tempos_velocities_and_polyphony'
    assert length == 192
    assert initial_sequences == expected_sequence_tff


def test_initialise_sequences_velocities_ft_mode():
    file, filename, length, initial_sequences = initialise_sequences(file_polyphony_folder + file_2_name + '.mid',
                                                                     True, False, True)

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(length, int)
    assert isinstance(initial_sequences, list)

    assert repr(file) == repr(expected_prepared_file_without_join)
    assert filename == 'test_tempos_velocities_and_polyphony'
    assert length == 192
    assert initial_sequences == expected_sequence_tft


def test_initialise_sequences_velocities_tf_mode():
    file, filename, length, initial_sequences = initialise_sequences(file_polyphony_folder + file_2_name + '.mid',
                                                                     True, True, False)

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(length, int)
    assert isinstance(initial_sequences, list)

    assert repr(file) == repr(expected_prepared_file_with_join)
    assert filename == 'test_tempos_velocities_and_polyphony'
    assert length == 192
    assert initial_sequences == expected_sequence_ttf


def test_initialise_sequences_velocities_tt_mode():
    file, filename, length, initial_sequences = initialise_sequences(file_polyphony_folder + file_2_name + '.mid',
                                                                     True, True, True)

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(length, int)
    assert isinstance(initial_sequences, list)

    assert repr(file) == repr(expected_prepared_file_with_join)
    assert filename == 'test_tempos_velocities_and_polyphony'
    assert length == 192
    assert initial_sequences == expected_sequence_ttt


def test_get_sequence_of_notes_booleans_ff_mode_file_1():
    array = np.load(file_notes_folder + '/SBFF.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_notes_folder + file_1_name + '.mid', False, False, False)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_booleans_ft_mode_file_1():
    array = np.load(file_notes_folder + '/SBFT.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_notes_folder + file_1_name + '.mid', False, False, True)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_booleans_tf_mode_file_1():
    array = np.load(file_notes_folder + '/SBTF.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_notes_folder + file_1_name + '.mid', False, True, False)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_booleans_tt_mode_file_1():
    array = np.load(file_notes_folder + '/SBTT.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_notes_folder + file_1_name + '.mid', False, True, True)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_velocities_ff_mode_file_1():
    array = np.load(file_notes_folder + '/SVFF.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_notes_folder + file_1_name + '.mid', True, False, False)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_velocities_ft_mode_file_1():
    array = np.load(file_notes_folder + '/SVFT.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_notes_folder + file_1_name + '.mid', True, False, True)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_velocities_tf_mode_file_1():
    array = np.load(file_notes_folder + '/SVTF.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_notes_folder + file_1_name + '.mid', True, True, False)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_velocities_tt_mode_file_1():
    array = np.load(file_notes_folder + '/SVTT.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_notes_folder + file_1_name + '.mid', True, True, True)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_array_of_notes_booleans_f_mode_file_1():
    array = np.load(file_notes_folder + '/ABF.npy', allow_pickle=True)
    out_array = get_array_of_notes(file_notes_folder + file_1_name + '.mid', False, False)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(array, out_array)


def test_get_array_of_notes_booleans_t_mode_file_1():
    array = np.load(file_notes_folder + '/ABT.npy', allow_pickle=True)
    out_array = get_array_of_notes(file_notes_folder + file_1_name + '.mid', False, True)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(array, out_array)


def test_get_array_of_notes_velocities_f_mode_file_1():
    array = np.load(file_notes_folder + '/AVF.npy', allow_pickle=True)
    out_array = get_array_of_notes(file_notes_folder + file_1_name + '.mid', True, False)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(array, out_array)


def test_get_array_of_notes_velocities_t_mode_file_1():
    array = np.load(file_notes_folder + '/AVT.npy', allow_pickle=True)
    out_array = get_array_of_notes(file_notes_folder + file_1_name + '.mid', True, True)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_booleans_ff_mode_file_2():
    array = np.load(file_polyphony_folder + '/SBFF.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_polyphony_folder + file_2_name + '.mid', False, False, False)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_booleans_ft_mode_file_2():
    array = np.load(file_polyphony_folder + '/SBFT.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_polyphony_folder + file_2_name + '.mid', False, False, True)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_booleans_tf_mode_file_2():
    array = np.load(file_polyphony_folder + '/SBTF.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_polyphony_folder + file_2_name + '.mid', False, True, False)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_booleans_tt_mode_file_2():
    array = np.load(file_polyphony_folder + '/SBTT.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_polyphony_folder + file_2_name + '.mid', False, True, True)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_velocities_ff_mode_file_2():
    array = np.load(file_polyphony_folder + '/SVFF.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_polyphony_folder + file_2_name + '.mid', True, False, False)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_velocities_ft_mode_file_2():
    array = np.load(file_polyphony_folder + '/SVFT.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_polyphony_folder + file_2_name + '.mid', True, False, True)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_velocities_tf_mode_file_2():
    array = np.load(file_polyphony_folder + '/SVTF.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_polyphony_folder + file_2_name + '.mid', True, True, False)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_sequence_of_notes_velocities_tt_mode_file_2():
    array = np.load(file_polyphony_folder + '/SVTT.npy', allow_pickle=True)
    out_array = get_sequence_of_notes(file_polyphony_folder + file_2_name + '.mid', True, True, True)

    assert isinstance(out_array, list)
    assert np.array_equal(array, out_array)


def test_get_array_of_notes_booleans_f_mode_file_2():
    array = np.load(file_polyphony_folder + '/ABF.npy', allow_pickle=True)
    out_array = get_array_of_notes(file_polyphony_folder + file_2_name + '.mid', False, False)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(array, out_array)


def test_get_array_of_notes_booleans_t_mode_file_2():
    array = np.load(file_polyphony_folder + '/ABT.npy', allow_pickle=True)
    out_array = get_array_of_notes(file_polyphony_folder + file_2_name + '.mid', False, True)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(array, out_array)


def test_get_array_of_notes_velocities_f_mode_file_2():
    array = np.load(file_polyphony_folder + '/AVF.npy', allow_pickle=True)
    out_array = get_array_of_notes(file_polyphony_folder + file_2_name + '.mid', True, False)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(array, out_array)


def test_get_array_of_notes_velocities_t_mode_file_2():
    array = np.load(file_polyphony_folder + '/AVT.npy', allow_pickle=True)
    out_array = get_array_of_notes(file_polyphony_folder + file_2_name + '.mid', True, True)

    assert isinstance(out_array, np.ndarray)
    assert np.array_equal(array, out_array)
