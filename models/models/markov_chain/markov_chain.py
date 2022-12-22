import os
import random

import numpy as np
from keras.callbacks import Callback, ModelCheckpoint
from midi.decode import get_array_of_notes

from models.music_model import MusicModel

N_GRAM = 3


class MarkovChain(MusicModel):
    def __init__(self):
        self.data = []
        self.tokens = set()
        self.n_grams = set()
        self.tokens_list = []
        self.n_grams_list = []
        self.probabilities = []
        self.n_grams_next_token = []

    def train(self, epochs=0, xtrain=None, ytrain=None, loss_callback=None, checkpoint_path=None):

        # count probabilities
        n = len(self.n_grams_list[0])
        n_gram_next = np.ndarray((len(self.n_grams_list,)), dtype=object)
        for i in range(n_gram_next.shape[0]):
            n_gram_next[i] = []

        for i in range(len(self.data)):
            print(str(i) + "/" + str(len(self.data)))
            for j in range(len(self.data[i])-n-1):
                curr_n_gram = tuple(self.data[i][j:j+n])
                next_note = self.data[i][j+n+1]
                n_gram_next[self.n_grams_list.index(
                    curr_n_gram)].append(next_note)

        self.probabilities = np.ndarray(
            (len(self.n_grams_list,)), dtype=object)
        for i in range(n_gram_next.shape[0]):
            self.probabilities[i] = {}

        for i in range(len(n_gram_next)):
            for j in range(len(n_gram_next[i])):
                if len(n_gram_next[i]) <= 1:
                    self.probabilities[n_gram_next[i]][j] = 1
                else:
                    if self.probabilities[i].get(n_gram_next[i][j]) is None:
                        self.probabilities[i][n_gram_next[i][j]] = float(
                            n_gram_next[i].count(n_gram_next[i][j]) / len(n_gram_next[i]))

    def create_dataset(self, dataset: list[tuple[any, any]]) -> tuple[any, any]:

        self.generate_tokens()
        self.generate_n_grams(N_GRAM)
        return (0, 0)

    def generate_tokens(self):

        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                notes = []
                for k in range(128):
                    if self.data[i][j][k] == True:
                        notes.append(k)

                self.data[i][j] = tuple(notes)
                self.tokens.add(tuple(notes))

    def prepare_data(self, midi_file) -> tuple[any, any]:

        data_lines = get_array_of_notes(midi_file, False, False)
        for i in range(len(data_lines)):  # serialize tracks
            self.data.append(data_lines[i].tolist())
        return data_lines

    def save(self, path):
        np.save(path, np.asarray(self.probabilities))

    def load(self, path):
        self.probabilities = np.load(path, allow_pickle=True)

    def generate_n_grams(self, n):
        print("Generating " + str(n) + "-grams")
        for i in range(len(self.data)):
            for j in range(len(self.data[i])-n+1):
                self.n_grams.add(tuple(self.data[i][j:j+n]))

        self.tokens_list = list(self.tokens)
        self.n_grams_list = list(self.n_grams)
        print(len(self.n_grams_list))
        print(str(n) + "-grams generated!")

    def model_summary(self) -> str:
        return (
            "Markov chain basing on " + str(N_GRAM) + "-grams:\n" + str(len(self.tokens_list)) + " tokens\n" +
            str(len(self.n_grams_list)) + " n_grams\n" +
            str(len(self.data)) + " files"
        )

    def predict(self, initial_notes, length, deterministic, rand, save_path, save_name):

        # deterministic - if True, next note will be always note with maximum probability
        #               - if False, next note will be sampled according to all notes probability
        # rand - chance of selecting compeletly ranodm token next

        prediction = []
        previous_n_gram = initial_notes
        for i in range(len(initial_notes)):
            prediction.append(initial_notes[i])
        for i in range(length):
            idx = None
            if previous_n_gram in self.n_grams:
                idx = self.n_grams_list.index(previous_n_gram)
            else:
                idx = random.randrange(len(self.probabilities))
            probs = self.probabilities[idx]
            while len(probs) == 0:
                idx = random.randrange(len(self.probabilities))
                probs = self.probabilities[idx]

            next_note = None
            if random.randrange(100) < rand*100:
                next_note = random.choice(self.tokens_list)
            elif deterministic:
                next_note = max(probs, key=probs.get)
            else:
                next_note = random.choices(
                    list(probs.keys()), weights=probs.values(), k=1)[0]
            previous_n_gram = previous_n_gram[1:] + (next_note,)
            prediction.append(next_note)

        print(prediction)
        result = np.full((len(prediction), 128), False)
        for i in range(len(prediction)):
            for j in range(len(prediction[i])):
                note = prediction[i][j]
                result[i][note] = True

        os.makedirs(save_path, exist_ok=True)
        np.save('{}/{}'.format(save_path, save_name), result)


# 21379, 21133, 21095, 20987, 20750
if __name__ == '__main__':
    path = '..\\data\\chorales'
    midi_paths = []
    for filename in os.listdir(path):
        midi_paths.append(os.path.join(path, filename))
    model = MarkovChain()
    model.train_on_files(midi_paths, 10, lambda epoch, loss: None)
