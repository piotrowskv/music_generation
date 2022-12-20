import pytest
from midi.decode import *
from mido.midifiles.meta import MetaMessage

# one-time setup
filepath = 'files/test_tempos_velocities_and_polyphony.mid'

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


def test_get_midi_length():  # test_tempos_velocities_and_polyphony.mid used
    file = MidiFile(filepath)
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


def test_open_file():  # test_tempos_velocities_and_polyphony.mid used
    file, filename, accuracy = open_file(filepath)

    assert isinstance(file, MidiFile)
    assert isinstance(filename, str)
    assert isinstance(accuracy, float)
    assert filename == 'test_tempos_velocities_and_polyphony'
    assert accuracy == float(12)


def test_get_tempo_array():  # test_tempos_velocities_and_polyphony.mid used
    file = MidiFile(filepath)
    tempos = get_tempo_array(file, 192, 12)

    assert isinstance(tempos, list)
    assert tempos == expected_tempos


def test_export_tempo_array():  # test_tempos_velocities_and_polyphony.mid used
    tempos = export_tempo_array(filepath)

    assert isinstance(tempos, list)
    assert tempos == expected_tempos


def test_combine_and_clean_tracks():  # test_tempos_velocities_and_polyphony.mid used
    file = MidiFile(filepath)
    tracks = file.tracks[1:]
    out_track = combine_and_clean_tracks(tracks)

    assert isinstance(out_track, MidiTrack)
    assert out_track == expected_midi_track


def test_get_max_velocity():  # test_tempos_velocities_and_polyphony.mid used
    file = MidiFile(filepath)
    tracks = file.tracks[1:]
    velocity = get_max_velocity(tracks)

    assert isinstance(velocity, int)
    assert velocity == 96
