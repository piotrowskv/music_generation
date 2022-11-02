import os
import mido
import numpy as np

"""
this version creates a simple boolean matrix,
next up I'll create a sequenced input
and their versions with unified tracks
as well as notes metadata

accuracy is set to 1/64th
"""


def get_ticks(time, offset, acc):
    begin = int(round(float(offset) / acc))
    finish = int(round(float(offset + time) / acc))

    return finish - begin


def check_type(file):
    if file.type == 2:
        raise ValueError('impossible to perform calculations'
                         ' for type 2 (asynchronous) file')


def get_midi_length(file):
    vals = []
    for i, track in enumerate(file.tracks):
        value = 0
        for msg in track:
            value += msg.time
        vals.append(value)

    return max(vals)


def insert_notes(array, track, time, notes):
    for note in notes:
        array[track, time, note] = True


def main_np(filepath):  # TODO: prepare saving path and name arguments

    filename = os.path.basename(filepath)
    if filename[-4:] != '.mid':
        raise TypeError('file must be of ".mid" format')

    filename = filename[:-4]
    f1 = mido.MidiFile(filepath)
    check_type(f1)

    try:
        beat_acc = f1.tracks[0][100].notated_32nd_notes_per_beat
    except (AttributeError, IndexError, NameError) as _:
        beat_acc = 8

    acc = f1.ticks_per_beat / (2 * beat_acc)  # maybe round it to int?

    length = int(float(get_midi_length(f1)) / acc)
    tempos = np.zeros(length, dtype=np.intc)

    offset = 0
    tempo = 500000
    for msg in f1.tracks[0]:
        incr = get_ticks(msg.time, offset, acc)
        for time in range(offset, offset+incr):
            tempos[time] = tempo
        offset += incr

        if msg.type == 'set_tempo':
            tempo = msg.tempo

    for time in range(offset, length):
        tempos[time] = tempo

    chart = np.zeros((len(f1.tracks) - 1, length, 88), dtype=np.bool_)  # 0th track is metadata
    min_offset = length
    max_offset = 0

    for track_index, track in enumerate(f1.tracks[1:]):  # different numbers in file
        # print('Track {}: {}'.format(track_index, track.name))  # TODO: test for unwanted tracks
        offset = 0
        notes = []  # TODO: replace with objects

        for msg in track:
            incr = get_ticks(msg.time, offset, acc)
            for time in range(offset, offset + incr):
                insert_notes(chart, track_index, time, notes)
            offset += incr  # offset is always ahead of saved data

            if msg.type == 'note_on':
                notes.append(msg.note - 20)
                if min_offset > offset:
                    min_offset = offset
            elif msg.type == 'note_off':
                notes.remove(msg.note - 20)

        for time in range(offset, length):
            insert_notes(chart, track_index, time, notes)

        if offset > max_offset:
            max_offset = offset

    chart = chart[:, min_offset:max_offset, :]  # delete empty entries
    np.save('./sequences/{}'.format(filename), chart)

    return chart


if __name__ == '__main__':
    for name in os.listdir('./data'):
        path = os.path.join('./data', name)
        print(name)
        try:
            _ = main_np(path)
        except Exception as ex:
            print(ex)
