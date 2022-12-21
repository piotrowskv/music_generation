import numpy as np

from mido import MidiTrack, MidiFile
from mido.messages import Message
from mido.midifiles.meta import MetaMessage

VELOCITY = 64
ACCURACY = 64


def get_tempo_meta_messages(array, acc):
    """
    translates provided tempo array into a MetaMessage track

    :param array:
    :param acc:
    :return:
    """
    events = [MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                          notated_32nd_notes_per_beat=8, time=0)]

    time = 0
    last_tempo = 0
    for i in range(len(array) - 1):
        if array[i] != last_tempo:
            events.append(MetaMessage('set_tempo', tempo=array[i], time=round(time)))
            last_tempo = array[i]
            time -= round(time)
        time += acc
    events.append(MetaMessage('end_of_track', time=round(time)))

    return MidiTrack(events)


def get_note_messages_from_2d_array(track, track_channel, acc):
    """
    translates a time distributed event_lengths' matrix into a MidiTrack of Messages

    :param track:
    :param track_channel:
    :param acc:
    :return:
    """
    events = []
    notes = []

    last_offset = 0
    for tick in track:
        current_notes = []
        for i in range(len(tick)):
            if tick[i]:
                current_notes.append(i)

        subtract = [elem for elem in notes if elem not in current_notes]
        add = [elem for elem in current_notes if elem not in notes]

        for elem in subtract:
            events.append(Message('note_off', note=elem, channel=track_channel,
                                  velocity=VELOCITY, time=round(last_offset * acc)))
            last_offset = 0
        for elem in add:
            events.append(Message('note_on', note=elem, channel=track_channel,
                                  velocity=VELOCITY, time=round(last_offset * acc)))
            last_offset = 0

        notes = current_notes
        last_offset += 1

    for elem in notes:
        events.append(Message('note_off', note=elem, channel=track_channel,
                              velocity=VELOCITY, time=round(last_offset * acc)))
        last_offset = 0

    events.append(MetaMessage('end_of_track', time=0))
    return MidiTrack(events)


def generate_file_from_2d_array(input_array, tempos, output_filename, accuracy):
    """
    translates a time distributed single-track array into a MIDI file

    :param input_array:
    :param tempos:
    :param output_filename:
    :param accuracy:
    :return:
    """
    if input_array.ndim != 2:
        raise TypeError('input array must have exactly 2 dimensions')

    if input_array.shape[0] + 1 != len(tempos):
        raise IndexError('length of input array\'s time dimension must be shorter by 1 than tempos array')

    midi_file = MidiFile(ticks_per_beat=240)
    acc_factor = float(960 / accuracy)  # acc_factor = ticks_per_beat / (notated_32nd_notes_per_beat * accuracy / 32)
    midi_file.tracks.append(get_tempo_meta_messages(tempos, acc_factor))

    midi_file.tracks.append(get_note_messages_from_2d_array(input_array, 0, acc_factor))
    midi_file.save(f'../../outputs/{output_filename}.mid')  # TODO: parametrization


def generate_file_from_3d_array(input_array, tempos, output_filename, accuracy):
    """
    translates a time distributed multi-track array into a MIDI file

    :param input_array:
    :param tempos:
    :param output_filename:
    :param accuracy:
    :return:
    """
    if input_array.ndim != 3:
        raise TypeError('input array must have exactly 3 dimensions')

    if input_array.shape[1] + 1 != len(tempos):
        raise IndexError('length of input array\'s time dimension must be shorter by 1 than tempos array')

    midi_file = MidiFile(ticks_per_beat=240)
    acc_factor = float(960 / accuracy)  # acc_factor = ticks_per_beat / (notated_32nd_notes_per_beat * accuracy / 32)
    midi_file.tracks.append(get_tempo_meta_messages(tempos, acc_factor))

    for i in range(input_array.shape[0]):
        midi_file.tracks.append(get_note_messages_from_2d_array(input_array[i], i, acc_factor))
    midi_file.save(f'../../outputs/{output_filename}.mid')  # TODO: parametrization


def generate_file_from_midi_features(input_array, output_filename, accuracy):   # TODO: check if > 0
    """
    translates a music_21.py output matrix of MIDI features into a MIDI file

    :param input_array:
    :param output_filename:
    :param accuracy:
    :return:
    """
    if input_array.ndim != 2:
        raise TypeError('input array must have exactly 2 dimensions')

    tempos = []
    array = []

    for feature_index in range(input_array.shape[1] - 2):
        track = []
        for event_index in range(input_array.shape[0]):
            notes = [False] * 128
            feature = round(input_array[event_index][feature_index] * 128 - 1)
            if feature != 0:
                notes[feature] = True

            length = round(1 / input_array[event_index][-2])
            track.extend([notes] * length)

        array.append(track)

    for event_index in range(input_array.shape[0]):
        length = round(1 / input_array[event_index][-2])
        tempo = round(1000 / input_array[event_index][-1])
        tempos.extend([tempo] * length)
    tempos.extend([round(1000 / input_array[-1][-1])])

    array = np.asarray(array)
    generate_file_from_3d_array(array, tempos, output_filename, accuracy)


def generate_file_from_tonal_features(input_array, output_filename, accuracy):   # TODO: check if even and > 0
    """
    translates a music_21.py output matrix of tonal features into a MIDI file

    :param input_array:
    :param output_filename:
    :param accuracy:
    :return:
    """
    if input_array.ndim != 2:
        raise TypeError('input array must have exactly 2 dimensions')

    tempos = []
    array = []

    for feature_index in range(int(input_array.shape[1] / 2 - 1)):
        track = []
        for event_index in range(input_array.shape[0]):
            notes = [False] * 128
            if input_array[event_index][2 * feature_index + 1] != 0:
                feature = round((input_array[event_index][2 * feature_index] * 11 - 1) * 12 +
                                input_array[event_index][2 * feature_index + 1] * 12 - 1)
                notes[feature] = True

            length = round(1 / input_array[event_index][-2])
            track.extend([notes] * length)

        array.append(track)

    for event_index in range(input_array.shape[0]):
        length = round(1 / input_array[event_index][-2])
        tempo = round(1000 / input_array[event_index][-1])
        tempos.extend([tempo] * length)
    tempos.extend([round(1000 / input_array[-1][-1])])

    array = np.asarray(array)
    generate_file_from_3d_array(array, tempos, output_filename, accuracy)


if __name__ == '__main__':
    # import os
    # from decode import export_tempo_array, get_array_of_notes

    # for name in os.listdir('../../sequences'):
    #     path = os.path.join('../../sequences', name)
    #     name = name.split('.')[0]

    path = '../../sequences/fugue1.npy'
    name = 'fugue1'
    try:
        # output_file = get_array_of_notes(path, False, True)               # ENCODER 1
        # # output_file = np.load(path, allow_pickle=True)
        # tempo_array = export_tempo_array(path)
        # generate_file_from_2d_array(output_file, tempo_array, name, ACCURACY)

        # output_file = get_array_of_notes(path, False, False)              # ENCODER 2
        # # output_file = np.load(path, allow_pickle=True)
        # tempo_array = export_tempo_array(path)
        # generate_file_from_3d_array(output_file, tempo_array, name, ACCURACY)

        output_file = np.load(path, allow_pickle=True)
        generate_file_from_midi_features(output_file, name, ACCURACY)       # ENCODER 3
        # generate_file_from_tonal_features(output_file, name, ACCURACY)    # ENCODER 4

    except Exception as ex:
        print("{}: {}".format(name, ex))
