import os
import numpy as np

from mido import MidiTrack, MidiFile
from mido.messages import Message
from mido.midifiles.meta import MetaMessage

from midi_decode import export_tempo_array, get_array_of_notes, Mode

VELOCITY = 64
ACCURACY = 64


def get_object(filepath):
    return np.load(filepath, allow_pickle=True)


def get_tempo_meta_messages(array, acc):
    events = [MetaMessage('track_name', name='Track 0', time=0),
              MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
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


def get_note_messages_from_2d_array(track, track_name, track_channel, acc):
    events = [MetaMessage('track_name', name=track_name, time=0)]
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
    if input_array.ndim != 2:
        raise TypeError

    if input_array.shape[0] + 1 != len(tempos):
        raise IndexError

    midi_file = MidiFile(ticks_per_beat=240)
    acc_factor = float(960 / accuracy)  # acc_factor = ticks_per_beat / (notated_32nd_notes_per_beat * accuracy / 32)
    midi_file.tracks.append(get_tempo_meta_messages(tempos, acc_factor))

    midi_file.tracks.append(get_note_messages_from_2d_array(input_array, 'Track 1', 0, acc_factor))
    midi_file.save(f'../outputs/{output_filename}.mid')


def generate_file_from_3d_array(input_array, tempos, output_filename, accuracy):
    if input_array.ndim != 3:
        raise TypeError

    if input_array.shape[1] + 1 != len(tempos):
        raise IndexError

    midi_file = MidiFile(ticks_per_beat=240)
    acc_factor = float(960 / accuracy)  # acc_factor = ticks_per_beat / (notated_32nd_notes_per_beat * accuracy / 32)
    midi_file.tracks.append(get_tempo_meta_messages(tempos, acc_factor))

    for i in range(input_array.shape[0]):
        midi_file.tracks.append(get_note_messages_from_2d_array(input_array[i], 'Track {}'.format(i + 1),
                                                                i, acc_factor))
    midi_file.save(f'../outputs/{output_filename}.mid')


def generate_file_from_midi_features(input_array, output_filename, accuracy):
    if input_array.ndim != 2:
        raise TypeError

    tempos = []
    array = []

    for feature_index in range(input_array.shape[1] - 2):
        track = []
        for event_index in range(input_array.shape[0]):
            notes = [False] * 128
            feature = round(input_array[event_index][feature_index] * 128)
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


def generate_file_from_tonal_features(input_array, output_filename, accuracy):
    if input_array.ndim != 2:
        raise TypeError

    tempos = []
    array = []

    for feature_index in range(int(input_array.shape[1] / 2 - 1)):
        track = []
        for event_index in range(input_array.shape[0]):
            notes = [False] * 128
            if input_array[event_index][2 * feature_index + 1] != 0:
                feature = round((input_array[event_index][2 * feature_index] * 8 + 1) * 12 +
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
    # for name in os.listdir('../sequences'):
    #     path = os.path.join('../sequences', name)
    #     name = name.split('.')[0]

    path = '../sequences/fugue1.npy'
    name = 'fugue1'
    try:
        # output_file = get_array_of_notes(path, Mode.BOOLEANS, True)               # ENCODER 1
        # # output_file = get_object(path)
        # tempo_array = export_tempo_array(path)
        # generate_file_from_2d_array(output_file, tempo_array, name, ACCURACY)
        #
        # output_file = get_array_of_notes(path, Mode.BOOLEANS, False)              # ENCODER 2
        # # output_file = get_object(path)
        # tempo_array = export_tempo_array(path)
        # generate_file_from_3d_array(output_file, tempo_array, name, ACCURACY)

        output_file = np.load(path, allow_pickle=True)
        generate_file_from_midi_features(output_file, name, ACCURACY)               # ENCODER 3
        # generate_file_from_tonal_features(output_file, name, ACCURACY)            # ENCODER 4

    except Exception as ex:
        print("{}: {}".format(name, ex))
