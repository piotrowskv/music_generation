import pytest

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
