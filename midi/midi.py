import os
import numpy as np

from enum import Enum
from abc import ABC, abstractmethod
from mido import MidiTrack, MidiFile
from mido.messages import Message

GRID_ACCURACY = 64  # sets accuracy to 1 / GRID_ACCURACY of a measure, best if it's a power of 2


class Mode(Enum):
    BOOLEANS = 0
    VELOCITIES = 1
    NOTES = 2


# abstract class of notes
class Note(ABC):
    velocity: float
    height: int
    tone: int
    octave: int

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def normalise(self,
                  max_velocity: int | float):
        self.velocity /= float(max_velocity)


# stored in arrays
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


# stored in sequences
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


# used to store values in sequential processing
class ActiveElement:
    height: int
    value: bool | float | EventNote
    mode: Mode

    def __init__(
            self,
            height: int,
            value: bool | int | float | EventNote,
            mode: Mode
    ):
        self.height = height
        self.mode = mode

        if isinstance(value, bool):  # as isinstance(BOOLEAN, int) == True
            self.value = value
        elif isinstance(value, int):
            self.value = float(value)
        else:
            self.value = value


# used to store states in sequential processing
class Event:
    time: int                                            # time from previous event, in grid accuracy
    length: int                                          # event length, in grid accuracy
    offset: int                                          # from the beginning, in grid accuracy
    track: int                                           # omits 'Track 0'
    tempo: int                                           # from 'Track 0' (MetaMessages)
    active_notes: list[ActiveElement]
    all_notes: list[None | bool | float | SeparateNote]  # of size 128
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
        self.active_notes = list[ActiveElement]()

        match mode:
            case Mode.BOOLEANS:
                self.__set_booleans_dictionary(notes)
                self.__set_booleans_array(notes)

            case Mode.VELOCITIES:
                self.__set_velocities_dictionary(notes)
                self.__set_velocities_array(notes)

            case Mode.NOTES:
                self.__set_notes_dictionary(notes)
                # set_notes_array needs set_notes_dictionary and length set up to run correctly

            case _:
                raise ValueError

    # returns a list of SeparateNotes
    def translate_event_to_separate_notes(self):
        notes = list[SeparateNote]()
        for note in self.active_notes:
            notes.append(SeparateNote(note.value.velocity, self.length, self.offset,
                                      self.track, self.tempo, note.value.height))
        return notes

    def __set_booleans_dictionary(self, notes):
        for height in notes.keys():
            self.active_notes.append(ActiveElement(height, True, Mode.BOOLEANS))
            self.active_notes.sort(key=lambda x: x.height)

    def __set_velocities_dictionary(self, notes):
        for height in notes.keys():
            self.active_notes.append(ActiveElement(height, notes[height].velocity, Mode.VELOCITIES))
            self.active_notes.sort(key=lambda x: x.height)

    def __set_notes_dictionary(self, notes):
        for height in notes.keys():
            self.active_notes.append(ActiveElement(height, notes[height], Mode.NOTES))
            self.active_notes.sort(key=lambda x: x.height)

    def __set_booleans_array(self, notes):
        self.all_notes = [False] * 128
        for height in notes.keys():
            self.all_notes[height] = True

    def __set_velocities_array(self, notes):
        self.all_notes = [float(0)] * 128
        for height in notes.keys():
            self.all_notes[height] = notes[height].velocity

    def set_notes_array(self):
        self.all_notes = [None] * 128
        notes = self.translate_event_to_separate_notes()
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
                    self.all_notes[element.height] /= float(max_velocity)

            case Mode.NOTES:
                for element in self.active_notes:
                    element.value.normalise(float(max_velocity))
                    self.all_notes[element.height].normalise(float(max_velocity))

            case _:
                raise ValueError


# translates MIDI ticks to the closest grid accuracy time units
def get_offset(time: int,
               ticks: int,
               accuracy: float):
    begin = int(round(float(ticks) / accuracy))
    finish = int(round(float(ticks + time) / accuracy))

    return finish - begin


# gets the length of the longest track
def get_midi_length(file: MidiFile,
                    accuracy: float):
    lengths = list[int]()
    for i, track in enumerate(file.tracks):
        ticks = 0
        value = 0
        for msg in track:
            value += get_offset(msg.time, ticks, accuracy)
            ticks += msg.time
        lengths.append(value)

    return max(lengths)


def check_file_type(file: MidiFile):
    if file.type == 2:
        raise ValueError('impossible to perform calculations for type 2 (asynchronous) file')


def open_file(filepath: str):
    filename = os.path.basename(filepath)
    if filename[-4:] != '.mid':
        raise TypeError('file must be of ".mid" format')

    filename = filename[:-4]
    file = MidiFile(filepath)
    check_file_type(file)

    # translates notated_32nd_notes_per_beat to pulses per quarter (PPQ) if necessary
    try:
        beat_amount = file.tracks[0][0].notated_32nd_notes_per_beat
    except (AttributeError, IndexError, NameError) as _:
        beat_amount = 8

    # calculates amount of PPQ in grid units
    accuracy = (file.ticks_per_beat * 32) / (GRID_ACCURACY * beat_amount)
    return file, filename, float(accuracy)


# translates 'Track 0' MetaMessages to an array of tempos for each grid unit
def get_tempo_array(file: MidiFile,
                    length: int,
                    accuracy: float):
    tempos = [0] * (length + 1)
    ticks = 0
    offset = 0
    tempo = 500000  # default MIDI tempo

    for msg in file.tracks[0]:
        increment = get_offset(msg.time, ticks, accuracy)
        for time in range(offset, offset + increment):
            tempos[time] = tempo
        ticks += msg.time
        offset += increment

        if msg.type == 'set_tempo':
            tempo = msg.tempo

    for time in range(offset, length + 1):  # additional position for an ending event
        tempos[time] = tempo

    return tempos


def export_output(filepath: str,
                  filename: str,
                  output):  # output as defined in DOCUMENTATION.md
    os.makedirs(filepath, exist_ok=True)
    np.save('{}/{}'.format(filepath, filename), output)


# translates all Messages to a single list, then removes vacuous Messages
def combine_and_clean_tracks(tracks: list[MidiTrack]):
    note_grid = [0] * 128                            # list with numbers of active notes, one for each height
    raw_messages = list[tuple[int, Message]]()       # all messages with their starting times
    filtered_messages = list[tuple[int, Message]]()  # as raw_messages, but without repetitions
    messages = list[Message]()                       # all messages with corrected timestamps

    for track in tracks:
        offset = 0
        for msg in track:
            offset += msg.time
            if msg.type in ['note_on', 'note_off']:
                raw_messages.append((offset, msg))

    last_message_time = 0
    delta_error = 0  # saves 'time' argument from omitted messages
    for time, msg in raw_messages:
        if msg.type == 'note_on':
            if note_grid[msg.note] == 0:
                filtered_messages.append((time + delta_error, msg))
                delta_error = 0
                last_message_time = time
                note_grid[msg.note] = 1

            elif note_grid[msg.note] > 0:  # in case of overlapping tracks, loss of following notes' metadata
                note_grid[msg.note] += 1
                delta_error += (time - last_message_time)
                last_message_time = time

            else:
                delta_error += (time - last_message_time)
                last_message_time = time

        elif msg.type == 'note_off':
            if note_grid[msg.note] == 1:
                filtered_messages.append((time + delta_error, msg))
                delta_error = 0
                last_message_time = time
                note_grid[msg.note] = 0

            elif note_grid[msg.note] > 1:
                note_grid[msg.note] -= 1
                delta_error += (time - last_message_time)
                last_message_time = time

            else:
                delta_error += (time - last_message_time)
                last_message_time = time

        else:
            delta_error += (time - last_message_time)
            last_message_time = time
    filtered_messages.sort(key=lambda x: x[0])

    offset = 0
    for time, msg in filtered_messages:
        if time - offset != msg.time:
            msg.time = time - offset
        offset += msg.time
        messages.append(msg)

    return MidiTrack(messages)


# gets the highest velocity across all Messages
def get_max_velocity(tracks: list[MidiTrack]):
    max_velocities = list[int]()

    for track_index, track in enumerate(tracks):
        max_velocity = 0
        for msg in track:
            if msg.type == 'note_on':
                if msg.velocity > max_velocity:
                    max_velocity = msg.velocity
        max_velocities.append(max_velocity)

    return max(max_velocities)


def prepare_file(filepath: str,
                 join_tracks: bool):
    file, filename, accuracy = open_file(filepath)
    length = get_midi_length(file, accuracy)
    tempos = get_tempo_array(file, length, accuracy)

    if join_tracks:
        track = combine_and_clean_tracks(file.tracks[1:])
        file.tracks = [file.tracks[0], track]
    else:
        for i in range(1, len(file.tracks)):
            file.tracks[i] = combine_and_clean_tracks([file.tracks[i]])

    return file, filename, accuracy, length, tempos


# returns raw sequences of events
def get_lists_of_events(file: MidiFile,
                        accuracy: float,
                        tempos: list[int],
                        mode: Mode):
    initial_sequences = list[list[Event]]()

    for track_index, track in enumerate(file.tracks[1:]):
        initial_sequence = list[Event]()
        ticks = 0
        offset = 0
        event_notes = dict[int, EventNote]()
        initial_sequence.append(Event(0, 0, 0, track_index, tempos[0], {}, mode))

        for msg in track:
            increment = get_offset(msg.time, ticks, accuracy)

            if msg.type == 'note_on':
                event_notes[msg.note] = EventNote(msg.velocity, msg.note)
            elif msg.type == 'note_off':
                try:
                    event_notes.pop(msg.note)
                except:
                    ticks += msg.time
                    offset += increment
                    continue

            ticks += msg.time
            offset += increment
            if msg.type in ['note_on', 'note_off']:
                initial_sequence.append(Event(increment, 0, offset, track_index, tempos[offset], event_notes, mode))
        
        # creates another list without zero-length events
        nonzero_sequence = list[Event]()
        for i in range(len(initial_sequence) - 1):
            if initial_sequence[i + 1].time > 0:
                initial_sequence[i].length = initial_sequence[i + 1].time
                nonzero_sequence.append(initial_sequence[i])
        nonzero_sequence.append(initial_sequence[-1])

        # arrays of notes must be set after event lengths setup, as they're stored in SeparateNotes
        if mode == Mode.NOTES:
            for i in range(len(nonzero_sequence)):
                nonzero_sequence[i].set_notes_array()

        initial_sequences.append(nonzero_sequence)
    return initial_sequences


# gets normalised sequences of events from a file
def initialise_sequences(filepath: str,
                         mode: Mode,
                         join_tracks: bool = False):
    file, filename, accuracy, length, tempos = prepare_file(filepath, join_tracks)
    initial_sequences = get_lists_of_events(file, accuracy, tempos, mode)

    # normalises velocity floats from [0, max_velocity(0 - 127)] to [0, 1]
    max_velocity = get_max_velocity(file.tracks[1:])
    for sequence in initial_sequences:
        for event in sequence:
            event.normalise(max_velocity)

    return file, filename, length, initial_sequences


# check the DOCUMENTATION.md file
def get_sequence_of_notes(filepath: str,
                          mode: Mode,
                          join_tracks: bool = False,
                          only_active_notes: bool = True):
    file, filename, length, initial_sequences = initialise_sequences(filepath, mode, join_tracks)

    output_list = list[list[tuple[int, list[int | tuple[int, bool | float | EventNote]]] |
                            tuple[int, list[None | bool | float | SeparateNote]]]]()
    for sequence in initial_sequences:
        track_list = list[tuple[int, list[int | tuple[int, bool | float | EventNote]]] |
                          tuple[int, list[None | bool | float | SeparateNote]]]()

        if only_active_notes:
            for event in sequence:
                event_list = list[int | tuple[int, bool | float | EventNote]]()
                for element in event.active_notes:
                    match mode:
                        case Mode.BOOLEANS:
                            event_list.append(element.height)
                        case _:
                            event_list.append((element.height, element.value))

                track_list.append((event.length, event_list))
        else:
            for event in sequence:
                track_list.append((event.length, event.all_notes))

        output_list.append(track_list)

    if join_tracks:
        export_output('../sequences', filename, output_list[0])
        return output_list[0]
    else:
        export_output('../sequences', filename, output_list)
        return output_list


# check the DOCUMENTATION.md file
def get_array_of_notes(filepath: str,
                       mode: Mode,
                       join_tracks: bool = False):
    file, filename, length, initial_sequences = initialise_sequences(filepath, mode, join_tracks)

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
                              initial_sequences[0][ev_index].offset +
                              initial_sequences[0][ev_index].length):
                output_array[time] = initial_sequences[0][ev_index].all_notes

    else:
        for seq_index in range(len(initial_sequences)):
            for ev_index in range(len(initial_sequences[seq_index])):
                for time in range(initial_sequences[seq_index][ev_index].offset,
                                  initial_sequences[seq_index][ev_index].offset +
                                  initial_sequences[seq_index][ev_index].length):
                    output_array[seq_index][time] = initial_sequences[seq_index][ev_index].all_notes

    export_output('../sequences', filename, output_array)
    return output_array


if __name__ == '__main__':
    for name in os.listdir('../data'):
        path = os.path.join('../data', name)
        print(name)

        try:
            _ = get_sequence_of_notes(path, Mode.BOOLEANS, False, True)
            # _ = get_sequence_of_notes(path, Mode.BOOLEANS, False, False)
            # _ = get_sequence_of_notes(path, Mode.BOOLEANS, True, True)
            # _ = get_sequence_of_notes(path, Mode.BOOLEANS, True, False)
            # _ = get_sequence_of_notes(path, Mode.VELOCITIES, False, True)
            # _ = get_sequence_of_notes(path, Mode.VELOCITIES, False, False)
            # _ = get_sequence_of_notes(path, Mode.VELOCITIES, True, True)
            # _ = get_sequence_of_notes(path, Mode.VELOCITIES, True, False)
            # _ = get_sequence_of_notes(path, Mode.NOTES, False, True)
            # _ = get_sequence_of_notes(path, Mode.NOTES, False, False)
            # _ = get_sequence_of_notes(path, Mode.NOTES, True, True)
            # _ = get_sequence_of_notes(path, Mode.NOTES, True, False)
            # _ = get_array_of_notes(path, Mode.BOOLEANS, False)
            # _ = get_array_of_notes(path, Mode.BOOLEANS, True)
            # _ = get_array_of_notes(path, Mode.VELOCITIES, False)
            # _ = get_array_of_notes(path, Mode.VELOCITIES, True)
            # _ = get_array_of_notes(path, Mode.NOTES, False)
            # _ = get_array_of_notes(path, Mode.NOTES, True)
            print("    success")

        except Exception as ex:
            print("    {}".format(ex))