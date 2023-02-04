import copy
from pathlib import Path
from typing import *

import numpy as np
from mido import MidiFile, MidiTrack
from mido.messages import Message
from mido.midifiles.meta import MetaMessage

DEFAULT_VELOCITY = 64
TICKS_PER_BEAT = 240
GRID_ACCURACY = 64


def get_tempo_meta_messages(array: list[int],
                            accuracy: float) -> MidiTrack:
    """
    translates a provided tempo array into a MetaMessage track

    :param array:
    :param accuracy:
    :return:
    """
    events = [MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                          notated_32nd_notes_per_beat=8, time=0)]

    time = float(0)
    last_tempo = 0
    for i in range(len(array)):
        if array[i] != last_tempo:
            events.append(MetaMessage('set_tempo', tempo=array[i], time=round(time)))
            last_tempo = array[i]
            time -= float(round(time))
        time += accuracy
    events.append(MetaMessage('end_of_track', time=round(time)))

    return MidiTrack(events)


def get_tempo_array_from_tempo_sequences(input_tempos: list[int],
                                         event_lengths: list[int]) -> list[int]:
    """
    translates tempos from an events' list into a time distributed list

    :param input_tempos:
    :param event_lengths:
    :return:
    """
    if len(input_tempos) != len(event_lengths):
        print(Warning('input tempo and event length arrays are of different length - '
                      'rewriting of the tempo array skipped'))
        return input_tempos

    tempos = list[int]()
    for i, value in enumerate(event_lengths):
        tempos.extend([input_tempos[i]] * value)

    return tempos


def get_sequences_from_array(array: np.ndarray) -> Tuple[list[Union[list[bool], list[float]]], list[int]]:
    """
    translates a time distributed single-track array into a list of events

    :param array:
    :return:
    """
    events = list[Union[list[bool], list[float]]]()
    event_lengths = list[int]()

    current_notes = array[0]
    current_length = 0
    for value in array:
        if not np.array_equal(current_notes, value):
            events.append(current_notes.tolist())
            event_lengths.append(current_length)
            current_notes = value
            current_length = 0
        current_length += 1
    events.append(current_notes.tolist())
    event_lengths.append(current_length)

    return events, event_lengths


def get_tuples_from_sequences(input_events: list[Union[list[bool], list[float]]]) -> list[list[Tuple[int, int]]]:
    """
    translates a list of events into a list of tuples of active notes

    :param input_events:
    :return:
    """
    events = list[list[Tuple[int, int]]]()
    for event in input_events:
        notes = list[Tuple[int, int]]()
        for i, value in enumerate(event):
            if value:  # True or > 0.0
                notes.append((i, min(127, round(value * 128))))  # velocity scaled from [0, 1] to [0, 128]
        events.append(notes)

    return events


def get_messages_from_tuples(track: list[list[Tuple[int, int]]],
                             track_channel: int,
                             event_lengths: list[int],
                             accuracy: float,
                             join_notes: bool,
                             use_default_velocity: bool,
                             default_velocity: int = DEFAULT_VELOCITY) -> MidiTrack:
    """
    translates a list of tuples of active notes into a MidiTrack

    :param track:
    :param track_channel:
    :param event_lengths:
    :param accuracy:
    :param join_notes:
    :param use_default_velocity:
    :param default_velocity:
    :return:
    """
    if len(track) != len(event_lengths):
        raise IndexError('input event length array and data event dimension must be of equal length')

    messages = list[Union[Message, MetaMessage]]()
    last_event = list[Tuple[int, int]]()
    time = 0
    for i, current_event in enumerate(track):
        if join_notes:
            subtract = [elem for elem in last_event if elem not in current_event]
            add = [elem for elem in current_event if elem not in last_event]
        else:
            subtract = last_event
            add = current_event

        for elem in subtract:
            messages.append(Message('note_off', note=elem[0], channel=track_channel,
                                    velocity=0, time=round(time * accuracy)))
            time = 0
        for elem in add:
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


def prepare_meta_file(tempos: list[int],
                      grid_accuracy: int,
                      event_lengths: Union[list[int], None] = None,
                      ticks_per_beat: int = TICKS_PER_BEAT) -> Tuple[list[int], float, MidiFile]:
    """
    generates a MIDI file with MetaMessages tempo track from the tempos' array

    :param tempos:
    :param grid_accuracy:
    :param event_lengths:
    :param ticks_per_beat:
    :return:
    """
    midi_file = MidiFile(ticks_per_beat=ticks_per_beat)
    accuracy = float(4 * ticks_per_beat / grid_accuracy)  # equal to ticks_per_measure / grid_accuracy
    if event_lengths is not None:
        new_tempos = get_tempo_array_from_tempo_sequences(copy.deepcopy(tempos), event_lengths)
    else:
        new_tempos = copy.deepcopy(tempos)

    midi_file.tracks.append(get_tempo_meta_messages(new_tempos, accuracy))
    return new_tempos, accuracy, midi_file


def get_messages_from_standard_2d_input(data: np.ndarray,
                                        track_channel: int,
                                        accuracy: float,
                                        join_notes: bool,
                                        use_sequences: bool,
                                        use_velocities: bool,
                                        event_lengths: Union[list[int], None] = None) -> MidiTrack:
    """
    translates a two-dimensional single-track array into a MidiTrack

    :param data:
    :param track_channel:
    :param accuracy:
    :param join_notes:
    :param use_sequences:
    :param use_velocities:
    :param event_lengths:
    :return:
    """
    lengths: list[int]
    if use_sequences:
        events = data.tolist()
        if isinstance(event_lengths, list):
            lengths = event_lengths
        else:
            raise ValueError('no argument \'event_lengths\' for \'use_sequences\' mode provided')
    else:
        events, lengths = get_sequences_from_array(data)

    events = get_tuples_from_sequences(events)
    track = get_messages_from_tuples(events, track_channel, lengths, accuracy, join_notes, not use_velocities)

    return track


def get_file_from_standard_features(data: np.ndarray,
                                    tempos: Union[int, list[int]],
                                    output_path: Path | str,
                                    join_notes: bool,
                                    use_sequences: bool,
                                    use_velocities: bool,
                                    event_lengths: Union[list[int], None] = None,
                                    grid_accuracy: int = GRID_ACCURACY) -> None:
    output_path = Path(output_path)
    """
    translates a multi-dimensional array into a MIDI file

    :param data:
    :param tempos:
    :param output_path:
    :param join_notes:
    :param use_sequences:
    :param use_velocities:
    :param event_lengths:
    :param grid_accuracy:
    :return:
    """
    lengths = list[int]()  # type checking consistency
    if use_sequences:
        if isinstance(event_lengths, list):
            lengths = event_lengths
        else:
            raise ValueError('no argument \'event_lengths\' for \'use_sequences\' mode provided')

    # tempos' array configuration
    if isinstance(tempos, int):
        if data.ndim == 2:
            tempos = [tempos] * data.shape[0]
        elif data.ndim == 3:
            tempos = [tempos] * data.shape[1]
        else:
            raise TypeError('input array must have 2 or 3 dimensions')
    else:
        if use_sequences:
            if len(lengths) != len(tempos):
                raise IndexError('length of tempos and event lengths\' arrays must be equal')
        else:
            if data.ndim == 2:
                if data.shape[0] != len(tempos):
                    raise IndexError('length of tempos array and input array\'s time dimension must be equal')
            elif data.ndim == 3:
                if data.shape[1] != len(tempos):
                    raise IndexError('length of tempos array and input array\'s time dimension must be equal')
            else:
                raise TypeError('input array must have 2 or 3 dimensions')

    # tracks generation
    _, accuracy, midi_file = prepare_meta_file(tempos, grid_accuracy, event_lengths)
    if data.ndim == 2:
        midi_file.tracks.append(get_messages_from_standard_2d_input(data, 0, accuracy, join_notes,
                                                                    use_sequences, use_velocities, event_lengths))
    elif data.ndim == 3:
        for i in range(data.shape[0]):  # channels are limited to 16 in MIDI 1.0
            midi_file.tracks.append(get_messages_from_standard_2d_input(data[i], i % 16, accuracy, join_notes,
                                                                        use_sequences, use_velocities, event_lengths))
    else:
        raise TypeError('input array must have 2 or 3 dimensions')

    output_path.parent.mkdir(exist_ok=True, parents=True)
    midi_file.save(output_path)


def get_file_from_music21_features(data: np.ndarray,
                                   output_path: str,
                                   use_tonal_features: bool,
                                   join_notes: bool,
                                   grid_accuracy: int = GRID_ACCURACY) -> None:
    """
    translates a music_21.py output matrix of tonal features into a MIDI file

    :param data:
    :param output_path:
    :param use_tonal_features:
    :param join_notes:
    :param grid_accuracy:
    :return:
    """
    if data.ndim != 2:
        raise TypeError('input array must have exactly 2 dimensions')

    if data.shape[1] <= 2:
        raise ValueError('number of MIDI tracks with notes\' messages must be at least 1')

    if use_tonal_features and data.shape[1] % 2 == 1:
        raise ValueError('odd number of tracks - each tonal track must be provided with two features')

    event_lengths = list[int]()
    tempos = list[int]()
    array = list[list[list[bool]]]()
    feature_range = range(int(data.shape[1] / 2 - 1)) if use_tonal_features else range(data.shape[1] - 2)

    for feature_index in feature_range:
        track = list[list[bool]]()
        for event_index in range(data.shape[0]):
            notes = [False] * 128

            if use_tonal_features:
                if data[event_index][2 * feature_index + 1] != 0:  # ignore 'empty notes'
                    # recalculating normalised octaves [1, 11] and tones [1, 12] to MIDI notes [0, 127]
                    feature = round((data[event_index][2 * feature_index] * 11 - 1) * 12 +
                                    data[event_index][2 * feature_index + 1] * 12 - 1)
                    notes[feature] = True

            else:
                # recalculating normalised feature notes [1, 128] to MIDI notes [0, 127]
                feature = round(data[event_index][feature_index] * 128 - 1)
                if feature > -1:  # ignore 'empty notes'
                    notes[feature] = True

            track.append(notes)
        array.append(track)

    for event_index in range(data.shape[0]):
        length = round(1 / data[event_index][-2])
        tempo = round(1000 / data[event_index][-1])
        event_lengths.append(length)
        tempos.append(tempo)

    new_data = np.asarray(array)
    get_file_from_standard_features(new_data, tempos, output_path, join_notes,
                                    True, False, event_lengths, grid_accuracy)


if __name__ == '__main__':
    from decode import export_tempo_array

    file = '../tests/test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid'
    # path = '../tests/test_files/test_polyphony/SVTF_array.npy'
    path = '../tests/test_files/test_polyphony/ABT.npy'
    out_path = '../tests/test_files/test_encode.mid'

    try:
        in_array = np.load(path, allow_pickle=True)

        tempo_array = export_tempo_array(file, False)
        get_file_from_standard_features(in_array, 500000, out_path, True, False, False)

        # in_tempos = [500000] * 8
        # in_tempos.extend([555555] * 8)
        # in_tempos.extend([500000] * 9)
        # get_file_from_standard_features(in_array, in_tempos, out_path, False, True, True,
        #                                 [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 24, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 8, 4, 4, 0])

        # get_file_from_music21_features(in_array, out_path, True, True)

    except Exception as ex:
        print("{}: {}".format(path, ex))
