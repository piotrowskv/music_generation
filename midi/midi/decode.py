import os
import numpy as np

from mido import MidiTrack, MidiFile
from mido.messages import Message

GRID_ACCURACY = 64  # sets accuracy to 1 / GRID_ACCURACY of a measure, best if it's a power of 2


class EventNote:
    """
    stores a single note with metadata, used to store event_lengths content
    """
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

    def __eq__(self, other):
        return self.velocity == other.velocity and \
               self.height == other.height and \
               self.tone == other.tone and \
               self.octave == other.octave

    def normalise(self,
                  max_velocity: int | float):  # TODO: check if 128
        """
        divides note velocity by a given value

        :param max_velocity:
        :return:
        """
        self.velocity /= float(max_velocity)


class ActiveElement:
    """
    stores single output-typed value, used to store values in sequential processing
    """
    height: int
    value: bool | float
    use_velocities: bool

    def __init__(
            self,
            height: int,
            value: bool | int | float,
            use_velocities: bool
    ):
        self.height = height
        self.use_velocities = use_velocities

        if isinstance(value, bool):  # as isinstance(BOOLEAN, int) == True
            self.value = value
        elif isinstance(value, int):
            self.value = float(value)
        else:                        # isinstance(value, float)
            self.value = value

    def __eq__(self, other):
        return self.height == other.height and \
               self.value == other.value and \
               self.use_velocities == other.use_velocities


class Event:
    """
    stores all information available about a single piano keyboard state,
    used to store states in sequential processing
    """
    time: int                             # time from previous event, in grid accuracy
    length: int                           # event length, in grid accuracy
    offset: int                           # from the beginning, in grid accuracy
    track: int                            # omits 'Track 0'
    tempo: int                            # from 'Track 0' (MetaMessages)
    active_notes: list[ActiveElement]
    all_notes: list[bool | float]  # of size 128
    use_velocities: bool

    def __init__(
            self,
            time: int,
            length: int,
            offset: int,
            track: int,
            tempo: int,
            notes: dict[int, EventNote],
            use_velocities: bool
    ):
        self.time = time
        self.length = length
        self.offset = offset
        self.track = track
        self.tempo = tempo
        self.use_velocities = use_velocities
        self.active_notes = list[ActiveElement]()

        if use_velocities:
            self.__set_velocities_dictionary(notes)
            self.__set_velocities_array(notes)

        else:
            self.__set_booleans_dictionary(notes)
            self.__set_booleans_array(notes)

    def __eq__(self, other):
        return self.time == other.time and \
               self.length == other.length and \
               self.offset == other.offset and \
               self.track == other.track and \
               self.tempo == other.tempo and \
               self.active_notes == other.active_notes and \
               self.all_notes == other.all_notes and \
               self.use_velocities == other.use_velocities

    def __set_booleans_dictionary(self, notes):
        for height in notes.keys():
            self.active_notes.append(ActiveElement(height, True, False))
            self.active_notes.sort(key=lambda x: x.height)

    def __set_velocities_dictionary(self, notes):
        for height in notes.keys():
            self.active_notes.append(ActiveElement(height, notes[height].velocity, True))
            self.active_notes.sort(key=lambda x: x.height)

    def __set_booleans_array(self, notes):
        self.all_notes = [False] * 128
        for height in notes.keys():
            self.all_notes[height] = True

    def __set_velocities_array(self, notes):
        self.all_notes = [float(0)] * 128
        for height in notes.keys():
            self.all_notes[height] = notes[height].velocity

    def normalise(self,
                  max_velocity: int | float):
        """
        if velocities are used, divides note velocity by a given value

        :param max_velocity:
        :return:
        """
        if self.use_velocities:
            for element in self.active_notes:
                element.value /= float(max_velocity)
                self.all_notes[element.height] /= float(max_velocity)


def get_offset(time: int,
               ticks: int,
               accuracy: float):
    """
    translates MIDI ticks to the closest grid accuracy time units

    :param time:
    :param ticks:
    :param accuracy:
    :return:
    """
    begin = int(round(float(ticks) / accuracy))
    finish = int(round(float(ticks + time) / accuracy))

    return finish - begin


# gets the length of the longest track
def get_midi_length(file: MidiFile,
                    accuracy: float):
    """
    returns the length of the longest track

    :param file:
    :param accuracy:
    :return:
    """
    lengths = list[int]()
    for i, track in enumerate(file.tracks[1:]):
        ticks = 0
        value = 0
        for msg in track:
            value += get_offset(msg.time, ticks, accuracy)
            ticks += msg.time
        lengths.append(value)

    return max(lengths)


def check_file_type(file: MidiFile):
    """
    checks if MIDI file type is 2: if yes, raises a ValueError

    :param file:
    :return:
    """
    if file.type == 2:
        raise ValueError('impossible to perform calculations for type 2 (asynchronous) file')


def get_filename(filepath: str):
    """
    checks if file is of '.mid' format:
    if yes, returns a filename without extension; if not, raises a TypeError

    :param filepath:
    :return:
    """
    filename = os.path.basename(filepath)
    if filename[-4:] != '.mid':
        raise TypeError('file must be of ".mid" format')

    filename = filename[:-4]
    return filename


def open_file(filepath: str,
              grid_accuracy: int = GRID_ACCURACY):
    """
    opens and checks if a given file is a '.mid' file:
    if yes, translates notated_32nd_notes_per_beat to pulses per quarter (PPQ) if necessary
    and calculates amount of PPQ in grid units; if not, raises a TypeError

    :param filepath:
    :param grid_accuracy:
    :return:
    """
    filename = get_filename(filepath)
    file = MidiFile(filepath)
    check_file_type(file)

    # translates notated_32nd_notes_per_beat to pulses per quarter (PPQ) if necessary
    try:
        beat_amount = file.tracks[0][0].notated_32nd_notes_per_beat  # TODO: search for 'time_signature'
    except (AttributeError, IndexError, NameError) as _:
        beat_amount = 8

    # calculates amount of PPQ in grid units
    accuracy = (file.ticks_per_beat * 32) / (grid_accuracy * beat_amount)
    return file, filename, float(accuracy)


def get_tempo_array(file: MidiFile,
                    length: int,
                    accuracy: float):
    """
    translates Track 0 MetaMessages to an array of tempos for each time unit,
    with an additional time unit for the last, closing event

    :param file:
    :param length:
    :param accuracy:
    :return:
    """
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


def export_tempo_array(filepath: str):
    """
    returns an array of tempos for each time unit in a given MIDI file

    :param filepath:
    :return:
    """
    file, _, accuracy = open_file(filepath)
    length = get_midi_length(file, accuracy)
    tempos = get_tempo_array(file, length, accuracy)[:-1]

    return tempos


def export_output(folder: str,
                  filename: str,
                  output):
    """
    saves a given object under the path defined by parameters

    :param folder:
    :param filename:
    :param output:
    :return:
    """
    os.makedirs(folder, exist_ok=True)
    np.save('{}/{}'.format(folder, filename), output)


def combine_and_clean_tracks(tracks: list[MidiTrack]):
    """
    translates all Messages to a single list, then removes vacuous Messages

    :param tracks:
    :return:
    """
    note_grid = [0] * 128                            # list with numbers of active notes, one for each height
    raw_messages = list[tuple[int, Message]]()       # all messages with their starting times
    filtered_messages = list[tuple[int, Message]]()  # as raw_messages, but without repetitions
    messages = list[Message]()                       # all messages with corrected timestamps

    # in case of 'note_on' messages only, 'note_off' is marked by velocity == 0
    for i in range(len(tracks)):
        phantom_track = list[Message]()
        off_notes = [x.type for x in tracks[i] if x.type == 'note_off']
        if len(off_notes) == 0:
            for msg in tracks[i]:
                if msg.type == 'note_on':
                    if msg.velocity != 0:
                        phantom_track.append(msg)
                    else:
                        phantom_msg = Message('note_off', channel=msg.channel, note=msg.note,
                                              time=msg.time, velocity=msg.velocity)
                        phantom_track.append(phantom_msg)
                else:
                    phantom_track.append(msg)
            tracks[i] = MidiTrack(phantom_track)

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


def get_max_velocity(tracks: list[MidiTrack]):
    """
    returns the highest velocity across all Messages inside MidiTracks

    :param tracks:
    :return:
    """
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
    """
    opens MIDI file, calculates accuracy factor, input length and tempo array,
    then cleans and optionally joins tracks

    :param filepath:
    :param join_tracks:
    :return:
    """
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


def get_lists_of_events(file: MidiFile,
                        accuracy: float,
                        tempos: list[int],
                        use_velocities: bool):
    """
    translates Messages to raw sequences of Events

    :param file:
    :param accuracy:
    :param tempos:
    :param use_velocities:
    :return:
    """
    initial_sequences = list[list[Event]]()

    for track_index, track in enumerate(file.tracks[1:]):
        initial_sequence = list[Event]()
        ticks = 0
        offset = 0
        accumulated_increment = 0

        event_notes = dict[int, EventNote]()
        initial_sequence.append(Event(0, 0, 0, track_index, tempos[0], {}, use_velocities))

        for msg in track:
            increment = get_offset(msg.time, ticks, accuracy)

            if msg.type == 'note_on':
                event_notes[msg.note] = EventNote(msg.velocity, msg.note)
            elif msg.type == 'note_off':
                try:
                    event_notes.pop(msg.note)
                except KeyError:
                    ticks += msg.time
                    offset += increment
                    accumulated_increment += increment
                    continue

            ticks += msg.time
            offset += increment
            increment += accumulated_increment
            accumulated_increment = 0

            if msg.type in ['note_on', 'note_off']:
                initial_sequence.append(Event(increment, 0, offset, track_index,
                                              tempos[offset], event_notes, use_velocities))

        # creates another list without zero-length event_lengths
        nonzero_sequence = list[Event]()
        for i in range(len(initial_sequence) - 1):
            if initial_sequence[i + 1].time > 0:
                initial_sequence[i].length = initial_sequence[i + 1].time
                nonzero_sequence.append(initial_sequence[i])
        nonzero_sequence.append(initial_sequence[-1])

        for i in range(1, len(nonzero_sequence)):
            nonzero_sequence[i].time = nonzero_sequence[i - 1].length

        initial_sequences.append(nonzero_sequence)
    return initial_sequences


def initialise_sequences(filepath: str,
                         use_velocities: bool,
                         join_tracks: bool,
                         use_custom_normalization: bool = False):
    """
    gets sequences of event_lengths from a MIDI file and normalises them to either 128 or maximal velocity

    :param filepath:
    :param use_velocities:
    :param join_tracks:
    :param use_custom_normalization:
    :return:
    """
    file, filename, accuracy, length, tempos = prepare_file(filepath, join_tracks)
    initial_sequences = get_lists_of_events(file, accuracy, tempos, use_velocities)

    if use_custom_normalization:
        max_velocity = get_max_velocity(file.tracks[1:])
        for sequence in initial_sequences:
            for event in sequence:
                event.normalise(max_velocity)

    else:
        for sequence in initial_sequences:
            for event in sequence:
                event.normalise(128)

    return file, filename, length, initial_sequences


def get_sequence_of_notes(filepath: str,
                          use_velocities: bool,
                          join_tracks: bool,
                          only_active_notes: bool):
    """
    translates a MIDI file into a sequence representing notes;
    output type depends on parameters:

    get_sequence_of_notes(str, False, False, True) -> <list> 'tracks'
      (<list> 'event_lengths' (<tuple> (<int> 'time offset', <list> 'active notes')))
    get_sequence_of_notes(str, False, False, False) -> <list> 'tracks'
      (<list> 'event_lengths' (<tuple> (<int> 'time offset', <list> (<list [bool], size: 128>))))
    get_sequence_of_notes(str, False, True, True) ->
      <list> 'event_lengths' (<tuple> (<int> 'time offset', <list> 'active notes'))
    get_sequence_of_notes(str, False, True, False) ->
      <list> 'event_lengths' (<tuple> (<int> 'time offset', <list> (<list [bool], size: 128>)))

    get_sequence_of_notes(str, True, False, True) -> <list> 'tracks'
      (<list> 'event_lengths' (<tuple> (<int> 'time offset', <list> (<tuple> (<int> 'note height', <float> 'note velocity')))))
    get_sequence_of_notes(str, True, False, False) -> <list> 'tracks'
      (<list> 'event_lengths' (<tuple> (<int> 'time offset', <list> (<list [float], size: 128>))))
    get_sequence_of_notes(str, True, True, True) ->
      <list> 'event_lengths' (<tuple> (<int> 'time offset', <list> (<tuple> (<int> 'note height', <float> 'note velocity'))))
    get_sequence_of_notes(str, True, True, False) ->
      <list> 'event_lengths' (<tuple> (<int> 'time offset', <list> (<list [float], size: 128>)))

    :param filepath:
    :param use_velocities:
    :param join_tracks:
    :param only_active_notes:
    :return:
    """
    file, filename, length, initial_sequences = initialise_sequences(filepath, use_velocities, join_tracks, False)
    output_list = list[list[tuple[int, list[int | tuple[int, bool | float]]] | tuple[int, list[bool | float]]]]()

    for sequence in initial_sequences:
        track_list = list[tuple[int, list[int | tuple[int, bool | float]]] | tuple[int, list[bool | float]]]()

        if only_active_notes:
            for event in sequence:
                event_list = list[int | tuple[int, bool | float]]()
                for element in event.active_notes:
                    if use_velocities:
                        event_list.append((element.height, element.value))
                    else:
                        event_list.append(element.height)

                track_list.append((event.length, event_list))
        else:
            for event in sequence:
                track_list.append((event.length, event.all_notes))

        output_list.append(track_list)

    if join_tracks:
        output_list = output_list[0]

    return output_list


def get_array_of_notes(filepath: str,
                       use_velocities: bool,
                       join_tracks: bool):
    """
    translates a MIDI file into an array representing notes;
    output type depends on parameters:

    get_array_of_notes(str, False, False) ->
      <np.ndarray [bool], size: 'tracks' x 'grid length' x 128>
    get_array_of_notes(str, False, True) ->
      <np.ndarray [bool], size: 'grid length' x 128>

    get_array_of_notes(str, True, False) ->
      <np.ndarray [float], size: 'tracks' x 'grid length' x 128>
    get_array_of_notes(str, True, True) ->
      <np.ndarray [float], size: 'grid length' x 128>

    :param filepath:
    :param use_velocities:
    :param join_tracks:
    :return:
    """
    file, filename, length, initial_sequences = initialise_sequences(filepath, use_velocities, join_tracks, False)

    if join_tracks:
        array_size = (length, 128)
    else:
        array_size = (len(file.tracks) - 1, length, 128)

    if use_velocities:
        output_array = np.zeros(array_size, dtype=np.float_)
    else:
        output_array = np.zeros(array_size, dtype=np.bool_)

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

    return output_array


if __name__ == '__main__':
    # for name in os.listdir('../../data'):
    #     path = os.path.join('../../data', name)
    #     print(name)

    try:
        path = '../tests/files/test_4_notes.mid'
        output_file = get_sequence_of_notes(path, False, False, True)
        # output_file = get_sequence_of_notes(path, False, False, False)
        output_file = get_sequence_of_notes(path, False, True, True)
        out_array = export_tempo_array(path)
        # output_file = get_sequence_of_notes(path, False, True, False)
        # output_file = get_sequence_of_notes(path, True, False, True)
        # output_file = get_sequence_of_notes(path, True, False, False)
        # output_file = get_sequence_of_notes(path, True, True, True)
        # output_file = get_sequence_of_notes(path, True, True, False)

        # output_file = get_array_of_notes(path, False, False)
        # output_file = get_array_of_notes(path, False, True)
        # output_file = get_array_of_notes(path, True, False)
        # output_file = get_array_of_notes(path, True, True)

        # export_output('../../sequences', get_filename(path), output_file)
        print("    success")

    except Exception as ex:
        print("    {}".format(ex))
