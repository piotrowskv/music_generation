import os
import numpy as np

from music21 import *

f = np.load('../sequences/fugue1.npy', allow_pickle=True)
f = f.tolist()

events = [[] for _ in range((len(f) + 1))]
tuples = [None] * len(f)

active_tracks = range(len(f))
active_tracks = list(active_tracks)
to_remove = []
removed_tracks = []

for track in active_tracks:
    if len(f[track]) > 0:
        tuples[track] = f[track].pop(0)
    else:
        to_remove.append(track)
        # active_tracks.remove(track)

for track in to_remove:
    active_tracks.remove(track)
    removed_tracks.append(track)
to_remove.clear()

while len(active_tracks) > 0:
    d = [tuples[i][0] for i in active_tracks]
    diff = min(d)
    events[len(f)].append(diff)

    for track in active_tracks:
        events[track].append(tuples[track][1])
        tuples[track] = (tuples[track][0] - diff, tuples[track][1])

        while tuples[track][0] == 0:
            if len(f[track]) == 0:
                to_remove.append(track)
                break
            else:
                tuples[track] = f[track].pop(0)

    for track in removed_tracks:
        events[track].append([])

    for track in to_remove:
        active_tracks.remove(track)
        removed_tracks.append(track)
    to_remove.clear()


''' VERSION WITH OCTAVE/TONE '''
# features = [[] for _ in range((2 * len(f) + 2))]
# for track in range(len(events) - 1):
#     while len(events[track]) > 0:
#         state = events[track].pop(0)
#
#         if len(state) == 0:
#             features[2 * track + 0].append(0.0)
#             features[2 * track + 1].append(0.0)
#         elif len(state) == 1:
#             features[2 * track + 0].append((state[0] // 12 - 1) / 8)    # octaves mapping x/8
#             features[2 * track + 1].append((state[0] % 12 + 1) / 12)    # tones mapping x/12
#         else:
#             ch = chord.Chord(state)
#             ch = ch.root().midi
#             features[2 * track + 0].append((ch // 12 - 1) / 8)
#             features[2 * track + 1].append((ch % 12 + 1) / 12)
#
# while len(events[-1]) > 0:
#     state = events[-1].pop(0)
#     features[-2].append(1 / state) # lengths mapping 1/x
#     features[-1].append(0.0) # TODO: tempos + mapping 1000/x


''' VERSION WITH MIDI NOTE '''
features = [[] for _ in range((len(f) + 1))]
for track in range(len(events) - 1):
    while len(events[track]) > 0:
        state = events[track].pop(0)

        if len(state) == 0:
            features[track].append(0.0)
        elif len(state) == 1:
            features[track].append(state[0] / 128)    # notes mapping x/128
        else:
            ch = chord.Chord(state)
            ch = ch.root().midi
            features[track].append(ch / 128)

while len(events[-1]) > 0:
    state = events[-1].pop(0)
    features[-1].append(1 / state) # lengths mapping 1/x


# for each note list determine the main note, if 0-1-N, calc features and put to the array
# collect tempo array and iterate through last list += offset to get tempo array positions

# output = np.asarray(features)
os.makedirs('../sequences', exist_ok=True)
np.save('../sequences/chords21', features)
print(features.__sizeof__())