import numpy as np

from mido import MidiTrack, MidiFile
from mido.messages import Message
from mido.midifiles.meta import MetaMessage

DEFAULT_VELOCITY = 64
GRID_ACCURACY = 64


def get_tempo_meta_messages(array, accuracy):
    """
    translates a provided tempo array into a MetaMessage track
    """
    events = [MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                          notated_32nd_notes_per_beat=8, time=0)]

    time = 0
    last_tempo = 0
    for i in range(len(array)):
        if array[i] != last_tempo:
            events.append(MetaMessage('set_tempo', tempo=array[i], time=round(time)))
            last_tempo = array[i]
            time -= round(time)
        time += accuracy
    events.append(MetaMessage('end_of_track', time=round(time)))

    return MidiTrack(events)


def get_tempo_array_from_tempo_sequences(input_tempos, event_lengths):
    """
    translates tempos from an events' list into a time distributed list
    """
    if len(input_tempos) != len(event_lengths):
        print(Warning('input tempo and event length arrays are of different length - '
                      'rewriting of the tempo array skipped'))
        return input_tempos

    tempos = []
    for i, value in enumerate(event_lengths):
        tempos.extend([input_tempos[i]] * value)

    return tempos


def get_sequences_from_array(array):
    """
    translates a time distributed single-track array into a list of events
    """
    events = []
    event_lengths = []

    current_notes = array[0]
    current_length = 0
    for value in array:
        if not np.array_equal(current_notes, value):
            events.append(current_notes)
            event_lengths.append(current_length)
            current_notes = value
            current_length = 0
        current_length += 1
    events.append(current_notes)
    event_lengths.append(current_length)

    return events, event_lengths


def get_tuples_from_sequences(input_events):
    """
    translates a list of events into a list of tuples of active notes
    """
    events = []
    for event in input_events:
        notes = []
        for i, value in enumerate(event):
            if value:  # True or > 0.0
                notes.append((i, min(127, round(value * 128))))
        events.append(notes)

    return events


def get_messages_from_tuples(track, track_channel, event_lengths,
                             accuracy, join_notes, use_default_velocity, default_velocity=DEFAULT_VELOCITY):
    """
    translates a list of tuples of active notes into a MidiTrack
    """
    if len(track) != len(event_lengths):
        raise IndexError('input event length array and data event dimension must be of equal length')

    messages = []
    last_event = []
    time = 0
    for i, current_event in enumerate(track):
        if join_notes:
            subtract = [elem for elem in last_event if elem not in current_event]
            add = [elem for elem in current_event if elem not in last_event]

            for elem in subtract:
                messages.append(Message('note_off', note=elem[0], channel=track_channel,
                                        velocity=0, time=round(time * accuracy)))
                time = 0

            for elem in add:
                messages.append(Message('note_on', note=elem[0], channel=track_channel,
                                        velocity=default_velocity if use_default_velocity else elem[1],
                                        time=round(time * accuracy)))
                time = 0

        else:
            for elem in last_event:
                messages.append(Message('note_off', note=elem[0], channel=track_channel,
                                        velocity=0, time=round(time * accuracy)))
                time = 0

            for elem in current_event:
                messages.append(Message('note_on', note=elem[0], channel=track_channel,
                                        velocity=default_velocity if use_default_velocity else elem[1],
                                        time=round(time * accuracy)))
                time = 0

        last_event = current_event
        time += event_lengths[i]

    for elem in last_event:
        messages.append(Message('note_off', note=elem[0], channel=track_channel,
                                velocity=0, time=round(time * accuracy)))
        time = 0

    messages.append(MetaMessage('end_of_track', time=0))
    return MidiTrack(messages)


def prepare_meta_file(tempos, grid_accuracy, event_lengths=None):
    midi_file = MidiFile(ticks_per_beat=240)  # constant of arbitrary choice
    accuracy = float(4 * midi_file.ticks_per_beat / grid_accuracy)  # = ticks_per_measure / grid_accuracy
    if event_lengths is not None:
        tempos = get_tempo_array_from_tempo_sequences(tempos, event_lengths)
    midi_file.tracks.append(get_tempo_meta_messages(tempos, accuracy))

    return tempos, accuracy, midi_file


def get_messages_from_standard_2d_input(data, track_channel, tempos, accuracy, join_notes, use_sequences,
                                        use_velocities, event_lengths=None):
    """
    translates a two-dimensional single-track array into a MidiTrack
    """
    if data.shape[0] != len(tempos):
        raise IndexError('length of tempos array and input array\'s time dimension must be equal')

    if use_sequences and event_lengths is None:
        raise ValueError('no argument \'event_lengths\' for \'use_sequences\' mode provided')

    if use_sequences:
        events = data.tolist()
    else:
        events, event_lengths = get_sequences_from_array(data)

    events = get_tuples_from_sequences(events)
    track = get_messages_from_tuples(events, track_channel, event_lengths, accuracy, join_notes, not use_velocities)

    return track


def get_file_from_standard_features(data, tempos, output_path, join_notes, use_sequences, use_velocities,
                                    event_lengths=None, grid_accuracy=GRID_ACCURACY):  # TODO: create if doesnt exist
    """
    translates a multi-dimensional array into a MIDI file
    """
    tempos, accuracy, midi_file = prepare_meta_file(tempos, grid_accuracy, event_lengths)
    if data.ndim == 2:
        midi_file.tracks.append(get_messages_from_standard_2d_input(data, 0, tempos, accuracy, join_notes,
                                                                    use_sequences, use_velocities, event_lengths))

    elif data.ndim == 3:
        for i in range(data.shape[0]):  # channels are limited to 16 in MIDI 1.0
            midi_file.tracks.append(get_messages_from_standard_2d_input(data[i], i % 16, tempos, accuracy, join_notes,
                                                                        use_sequences, use_velocities, event_lengths))

    else:
        raise TypeError('input array must have 2 or 3 dimensions')

    midi_file.save(output_path)


def get_file_from_music21_features(data, output_path, use_tonal_features, join_notes, grid_accuracy=GRID_ACCURACY):
    """
    translates a music_21.py output matrix of tonal features into a MIDI file
    """
    if data.ndim != 2:
        raise TypeError('input array must have exactly 2 dimensions')

    if data.shape[1] <= 2:
        raise ValueError('number of MIDI tracks with notes\' messages must be at least 1')

    if use_tonal_features and data.shape[1] % 2 == 1:
        raise ValueError('odd number of tracks - each tonal track must be provided with two features')

    event_lengths = []
    tempos = []
    array = []

    for feature_index in range(int(data.shape[1] / 2 - 1)):
        track = []
        for event_index in range(data.shape[0]):
            notes = [False] * 128

            if use_tonal_features:
                if data[event_index][2 * feature_index + 1] != 0:  # ignore zero-length events
                    # recalculating normalised octaves [1, 11] and tones [1, 12] to MIDI notes [0, 127]
                    feature = round((data[event_index][2 * feature_index] * 11 - 1) * 12 +
                                    data[event_index][2 * feature_index + 1] * 12 - 1)
                    notes[feature] = True

            else:
                # recalculating normalised feature notes [1, 128] to MIDI notes [0, 127]
                feature = round(data[event_index][feature_index] * 128 - 1)
                if feature != 0:
                    notes[feature] = True

            track.append([notes])
        array.append(track)

    for event_index in range(data.shape[0]):
        length = round(1 / data[event_index][-2])
        tempo = round(1000 / data[event_index][-1])
        event_lengths.append(length)
        tempos.append(tempo)

    array = np.asarray(array)
    get_file_from_standard_features(array, tempos, output_path, join_notes, True, False, event_lengths, grid_accuracy)


if __name__ == '__main__':
    from decode import export_tempo_array

    file = '../tests/test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid'
    path = '../tests/test_files/test_polyphony/AVF.npy'
    out_path = ''

    try:
        in_array = np.load(path, allow_pickle=True)
        tempo_array = export_tempo_array(file)
        tempo_array.extend(tempo_array)
        get_file_from_standard_features(in_array, tempo_array, out_path, False, False, True)

    except Exception as ex:
        print("{}: {}".format(path, ex))
