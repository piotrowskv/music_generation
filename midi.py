import os
import mido
import numpy as np

from enum import Enum
from abc import ABC, abstractmethod

"""
this version creates a simple boolean matrix,
next up I'll create a sequenced input
and their versions with unified tracks
as well as notes metadata

VALUES RETURNED:
"""
# TODO: write documentation here

GRID_ACCURACY = 64   # sets accuracy to 1/value of a measure, best if power of 2


class Mode(Enum):
    BOOLEANS = 0
    VELOCITIES = 1
    NOTES = 2


class Note(ABC):
    velocity: float
    height: int
    tone: int
    octave: int

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def normalise(self, max_velocity: int | float):
        self.velocity /= float(max_velocity)


class ActiveElement:
    height: int
    value: bool | float | Note
    mode: Mode

    def __init__(
            self,
            height: int,
            value: bool | int | float | Note,
            mode: Mode
    ):
        self.height = height
        self.mode = mode

        if isinstance(value, int):
            self.value = float(value)
        else:
            self.value = value


def get_element_height(x):
    return x.height


class SeparateNote(Note):
    velocity: float  # normalised to [0, 1] from [0, 127]
    length: int      # note length, in grid accuracy
    offset: int      # from the beginning, in grid accuracy
    track: int       # not counting track 0 (metadata)
    tempo: int       # from track 0 (MetaMessages)
    height: int      # [0, 127] possible, with [21, 108] being on the piano
    tone: int        # from 'height', [1, 12]
    octave: int      # from 'height', [-1, 9] possible, with [0, 8] being on the piano

    def __init__(
            self,
            velocity: int | float,
            length: int,
            offset: int,
            track: int,
            tempo: int,
            height: int
    ):
        self.velocity = float(velocity)
        self.length = length
        self.offset = offset
        self.track = track
        self.tempo = tempo
        self.height = height
        self.tone = height % 12 + 1
        self.octave = height // 12 - 1


def translate_event_to_separate_note(event):
    notes = []
    for note in event.active_notes:
        notes.append(SeparateNote(note.velocity, event.length, event.offset, event.track, event.tempo, note.height))

    return notes


class EventNote(Note):
    velocity: float  # normalised to [0, 1] from [0, 127]
    height: int      # [0, 127] possible, with [21, 108] being on the piano
    tone: int        # from 'height', [1, 12]
    octave: int      # from 'height', [-1, 9] possible, with [0, 8] being on the piano

    def __init__(
            self,
            velocity: int | float,
            height: int
    ):
        self.velocity = float(velocity)
        self.height = height
        self.tone = height % 12 + 1
        self.octave = height // 12 - 1


class Event:
    time: int        # time from previous event, in grid accuracy
    length: int      # event length, in grid accuracy
    offset: int      # from the beginning, in grid accuracy
    track: int       # not counting track 0 (metadata)
    tempo: int       # from track 0 (MetaMessages)
    active_notes: list[ActiveElement]
    all_notes: list  # of size 128, values depend on the mode
    mode: Mode

    def __init__(
            self,
            time: int,
            length: int,
            offset: int,
            track: int,
            tempo: int,
            notes: dict[int, EventNote],
            mode: Mode
    ):
        self.time = time
        self.length = length
        self.offset = offset
        self.track = track
        self.tempo = tempo
        self.mode = mode

        match mode:
            case Mode.BOOLEANS:
                self.__set_booleans_dictionary(notes)
                self.__set_booleans_array(notes)

            case Mode.VELOCITIES:
                self.__set_velocities_dictionary(notes)
                self.__set_velocities_array(notes)

            case Mode.NOTES:
                self.__set_notes_dictionary(notes)
                self.__set_notes_array()  # needs __set_notes_dictionary(notes) executed to work correctly

            case _:
                raise ValueError

    def __set_booleans_dictionary(self, notes):
        for height, _ in notes:
            self.active_notes.append(ActiveElement(height, True, Mode.BOOLEANS))
            self.active_notes.sort(key=get_element_height)

    def __set_velocities_dictionary(self, notes):
        for height, note in notes:
            self.active_notes.append(ActiveElement(height, note.velocity, Mode.VELOCITIES))
            self.active_notes.sort(key=get_element_height)

    def __set_notes_dictionary(self, notes):
        for height, note in notes:
            self.active_notes.append(ActiveElement(height, note, Mode.NOTES))
            self.active_notes.sort(key=get_element_height)

    def __set_booleans_array(self, notes):
        self.all_notes = [False] * 128
        for height, _ in notes:
            self.all_notes[height] = True

    def __set_velocities_array(self, notes):
        self.all_notes = [float(0)] * 128
        for height, note in notes:
            self.all_notes[height] = note.velocity

    def __set_notes_array(self):
        self.all_notes = [None] * 128
        notes = translate_event_to_separate_note(self)
        for note in notes:
            self.all_notes[note.height] = note

    def normalise(self,
                  max_velocity: int | float):

        match self.mode:
            case Mode.BOOLEANS:
                pass

            case Mode.VELOCITIES:
                for element in self.active_notes:
                    element.value /= float(max_velocity)

            case Mode.NOTES:
                for element in self.active_notes:
                    element.value.normalise(float(max_velocity))

            case _:
                raise ValueError


def get_offset(time, ticks, acc):
    begin = int(round(float(ticks) / acc))
    finish = int(round(float(ticks + time) / acc))

    return finish - begin


def check_file_type(file):
    if file.type == 2:
        raise ValueError('impossible to perform calculations for type 2 (asynchronous) file')


def get_midi_length(file, acc):
    vals = []
    for i, track in enumerate(file.tracks):
        ticks = 0
        value = 0
        for msg in track:
            value += get_offset(msg.time, ticks, acc)
            ticks += msg.time
        vals.append(value)

    return max(vals)


def open_file(filepath):
    filename = os.path.basename(filepath)
    if filename[-4:] != '.mid':
        raise TypeError('file must be of ".mid" format')

    filename = filename[:-4]
    file = mido.MidiFile(filepath)
    check_file_type(file)

    try:
        beat_amount = file.tracks[0][0].notated_32nd_notes_per_beat
    except (AttributeError, IndexError, NameError) as _:
        beat_amount = 8

    acc = (file.ticks_per_beat * 32) / (GRID_ACCURACY * beat_amount)  # maybe round it to int?
    return file, filename, acc


def get_tempo_array(file, length, acc):
    tempos = np.zeros(length, dtype=np.intc)

    ticks = 0
    offset = 0
    tempo = 500000
    for msg in file.tracks[0]:
        increment = get_offset(msg.time, ticks, acc)
        for time in range(offset, offset + increment):
            tempos[time] = tempo
        ticks += msg.time
        offset += increment

        if msg.type == 'set_tempo':
            tempo = msg.tempo

    for time in range(offset, length):
        tempos[time] = tempo

    return tempos


def export_output(filepath, filename, output):
    os.makedirs(filepath, exist_ok=True)
    np.save('{}/{}'.format(filepath, filename), output)


def combine_tracks(file):
    return mido.merge_tracks(file.tracks[1:])


def get_max_velocity(tracks):
    max_velocities = []

    for track_index, track in enumerate(tracks):
        max_velocity = 0
        for msg in track:
            if msg.type == 'note_on':
                if msg.velocity > max_velocity:
                    max_velocity = msg.velocity
        max_velocities.append(max_velocity)

    return max(max_velocities)


def prepare_file(filepath, join_tracks):
    file, filename, acc = open_file(filepath)
    length = get_midi_length(file, acc)
    tempos = get_tempo_array(file, length, acc)

    if join_tracks:
        file.tracks = [file.tracks[0], combine_tracks(file.tracks[1:])]

    return file, filename, acc, length, tempos


def get_lists_of_events(file, acc, tempos, mode):
    initial_sequences = []

    for track_index, track in enumerate(file.tracks[1:]):
        initial_sequence = []
        ticks = 0
        offset = 0
        event_notes = dict[int, EventNote]()

        for msg in track:
            increment = get_offset(msg.time, ticks, acc)

            if msg.type == 'note_on':
                event_notes[msg.height] = (EventNote(msg.velocity, msg.height))
            elif msg.type == 'note_off':
                event_notes.pop(msg.height)

            ticks += msg.time
            offset += increment
            initial_sequence.append(Event(increment, 0, offset, track_index, tempos[offset], event_notes, mode))

        for i in range(len(initial_sequence) - 1):
            initial_sequence[i].length = initial_sequence[i + 1].time

        initial_sequences.append(initial_sequence)
    return initial_sequences


def initialise_sequences(filepath, mode, join_tracks=False):
    file, filename, acc, length, tempos = prepare_file(filepath, join_tracks)
    initial_sequences = get_lists_of_events(file, acc, tempos, mode)

    max_velocity = get_max_velocity(file.tracks[1:])
    for sequence in initial_sequences:
        for event in sequence:
            event.normalise(max_velocity)

    return file, filename, acc, length, tempos, initial_sequences


def get_sequence_of_notes(filepath, mode, join_tracks=False, only_active_notes=True):
    file, filename, acc, length, tempos, initial_sequences = initialise_sequences(filepath, mode, join_tracks)

    output_list = []
    for sequence in initial_sequences:
        track_list = []

        if only_active_notes:
            for event in sequence:
                event_list = []
                for element in event.active_notes:
                    event_list.append([element.height, element.value])
                track_list.append((event.length, event_list))
        else:
            for event in sequence:
                track_list.append((event.length, event.all_notes))

        output_list.append(track_list)

    if join_tracks:
        export_output('./sequences', filename, output_list[0])
        return output_list[0]
    else:
        export_output('./sequences', filename, output_list)
        return output_list


def get_array_of_notes(filepath, mode, join_tracks=False):
    file, filename, acc, length, tempos, initial_sequences = initialise_sequences(filepath, mode, join_tracks)

    if join_tracks:
        array_size = (length, 128)
    else:
        array_size = (len(file.tracks) - 1, length, 128)

    match mode:
        case Mode.BOOLEANS:
            output_array = np.zeros(array_size, dtype=np.bool_)
        case Mode.VELOCITIES:
            output_array = np.zeros(array_size, dtype=np.float_)
        case Mode.NOTES:
            output_array = np.zeros(array_size, dtype=SeparateNote)
        case _:
            raise ValueError

    if join_tracks:
        for ev_index in range(len(initial_sequences[0])):
            for time in range(initial_sequences[0][ev_index].offset,
                              initial_sequences[0][ev_index].length):
                for i in range(128):
                    output_array[time][i] = initial_sequences[0][ev_index].all_notes[i]
    else:
        for seq_index in range(len(initial_sequences)):  # maybe there exists more gentle formula?
            for ev_index in range(len(initial_sequences[seq_index])):
                for time in range(initial_sequences[seq_index][ev_index].offset,
                                  initial_sequences[seq_index][ev_index].length):
                    for i in range(128):
                        output_array[seq_index][time][i] = initial_sequences[seq_index][ev_index].all_notes[i]

    export_output('./sequences', filename, output_array)
    return output_array


if __name__ == '__main__':
    for name in os.listdir('./data'):
        path = os.path.join('./data', name)
        print(name)

        try:
            # _ = get_sequence_of_notes(path, Mode.BOOLEANS)
            _ = get_array_of_notes(path, Mode.BOOLEANS)
            print("success")
        except Exception as ex:
            print(ex)
