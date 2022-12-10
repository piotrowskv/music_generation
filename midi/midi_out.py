import os
# import mido
import numpy as np

from mido import MidiTrack, MidiFile
from mido.messages import Message
from mido.midifiles.meta import MetaMessage

TICKS_IN_BEAT = 0.5
TEMPO = 937500
VELOCITY = 64


def prepare_meta_track(length):  # TODO: length?
    events = [MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24,
                          notated_32nd_notes_per_beat=8, time=0),  # TODO: notated_32nd_notes_per_beat - calculate
              MetaMessage('set_tempo', tempo=TEMPO, time=0),
              MetaMessage('end_of_track', time=0)]
    return MidiTrack(events)


def get_events_from_array(track):
    events = [MetaMessage('track_name', name='Grand Piano', time=0)]
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
            events.append(Message('note_off', note=elem, velocity=VELOCITY, time=int(last_offset*TICKS_IN_BEAT)))
            last_offset = 0
        for elem in add:
            events.append(Message('note_on', note=elem, velocity=VELOCITY, time=int(last_offset*TICKS_IN_BEAT)))
            last_offset = 0

        notes = current_notes
        last_offset += 1

    for elem in notes:
        events.append(Message('note_off', note=elem, velocity=VELOCITY, time=int(last_offset*TICKS_IN_BEAT)))
        last_offset = 0

    events.append(MetaMessage('end_of_track', time=0))  # time=last_offset*TICKS_IN_BEAT
    return MidiTrack(events)


def get_sequences(filepath):
    return np.load(filepath, allow_pickle=True)


if __name__ == '__main__':
    for name in os.listdir('../sequences'):
        path = os.path.join('../sequences', name)
        name = name.split('.')[0]

        try:
            file_input = get_sequences(path)
            if file_input.ndim == 3:
                for track in file_input:
                    raise NotImplementedError

            elif file_input.ndim == 2:
                midi_file = MidiFile(ticks_per_beat=8)  # TODO: notated_32nd_notes_per_beat - calculate
                midi_file.tracks.append(prepare_meta_track(int(len(file_input) * TICKS_IN_BEAT)))
                midi_file.tracks.append(get_events_from_array(file_input))
                midi_file.save(f'../outputs/{name}.mid')

            else:
                raise TypeError

            print(name)

        except Exception as ex:
            print("{}: {}".format(name, ex))
