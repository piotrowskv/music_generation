import random
import time
from pathlib import Path
from typing import Any, cast

import numpy as np
from midi.decode import get_array_of_notes
from midi.encode import get_file_from_standard_features

from models.music_model import MusicModel, ProgressCallback, ProgressMetadata


class MarkovChain(MusicModel):
    n_gram_size: int

    def __init__(self, n_gram_size: int = 1) -> None:
        self.data: list = []
        self.tokens: set = set()
        self.n_grams: set = set()
        self.tokens_list: list[tuple] = []
        self.n_grams_list: list[tuple] = []
        self.probabilities: np.ndarray
        self.n_gram_size = n_gram_size

    def train(self, epochs: int | None, x_train: Any, y_train: Any, progress_callback: ProgressCallback,
              checkpoint_path: Path | None = None) -> None:

        # count probabilities
        n = len(self.n_grams_list[0])
        n_gram_next: np.ndarray = np.ndarray(
            (len(self.n_grams_list, )), dtype=object)

        for i in range(n_gram_next.shape[0]):
            n_gram_next[i] = []

        start = time.time()
        time.perf_counter()

        for i in range(len(self.data)):

            elapsed = time.time() - start
            progress_callback([(elapsed, 100 * i / len(self.data))])

            for j in range(len(self.data[i]) - n - 1 - self.n_gram_size):
                curr_n_gram = tuple(self.data[i][j:j + n])
                next_note = self.data[i][j + n + 1]
                n_gram_next[self.n_grams_list.index(
                    curr_n_gram)].append(next_note)

        elapsed = time.time() - start
        progress_callback([(elapsed, 100)])

        self.probabilities = np.ndarray(
            (len(self.n_grams_list, )), dtype=object)
        for i in range(n_gram_next.shape[0]):
            self.probabilities[i] = {}

        len_n_gram_next = len(n_gram_next)

        for i in range(len_n_gram_next):
            for j in range(len(n_gram_next[i])):
                if len(n_gram_next[i]) <= 1:
                    self.probabilities[n_gram_next[i]][j] = 1
                else:
                    if self.probabilities[i].get(n_gram_next[i][j]) is None:
                        self.probabilities[i][n_gram_next[i][j]] = float(
                            n_gram_next[i].count(n_gram_next[i][j]) / len(n_gram_next[i]))

    def create_dataset(self, dataset: list[tuple[Any, Any]]) -> tuple[Any, Any]:

        self.generate_tokens()
        self.generate_n_grams(self.n_gram_size)
        return 0, 0

    def generate_tokens(self) -> None:

        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                notes = []
                for k in range(128):
                    if self.data[i][j][k]:
                        notes.append(k)

                self.data[i][j] = tuple(notes)
                self.tokens.add(tuple(notes))

    def prepare_data(self, midi_file: Path) -> tuple[Any, Any]:
        data_lines = get_array_of_notes(midi_file, False, False)
        for i in range(len(data_lines)):  # serialize tracks
            self.data.append(data_lines[i].tolist())
        return 0, 0

    def save(self, path: Path) -> None:
        np.savez(path, probabilities=np.asarray(self.probabilities, dtype=object),
                 tokens=np.asarray(self.tokens_list, dtype=object))

    def load(self, path: Path) -> None:
        path = path if path.name.endswith('.npz') else path.with_suffix('.npz')
        data = np.load(path, allow_pickle=True)
        self.probabilities = data['probabilities']
        self.tokens_list = data['tokens']

    def generate_n_grams(self, n: int) -> None:
        print("Generating " + str(n) + "-grams")
        for i in range(len(self.data)):
            for j in range(len(self.data[i]) - n + 1):
                self.n_grams.add(tuple(self.data[i][j:j + n]))

        self.tokens_list = list(self.tokens)
        self.n_grams_list = list(self.n_grams)
        print(str(len(self.n_grams_list)) + " " + str(n) + "-grams generated!")

    def model_summary(self) -> str:
        return ("Markov chain basing on " +
                str(self.n_gram_size) + "-grams:\n" +
                str(len(self.tokens_list)) + " tokens\n" +
                str(len(self.n_grams_list)) + " n_grams\n" +
                str(len(self.data)) + " files")

    def generate(self, path: Path, seed: int | None = None) -> None:

        assert len(self.tokens_list) > 0, "Model was not initiated with data"

        if seed is None:
            result = self.predict(self.tokens_list[0], 512, True, 0, None, path)
            get_file_from_standard_features(result, 500000, path, False, False, False)

        elif isinstance(seed, int):
            # seed of random.randrange

            cast(int, seed)
            result = self.predict(self.tokens_list[0], 512, False, 0, seed, path)
            get_file_from_standard_features(result, 500000, path, False, False, False)

    def predict(self, initial_notes: tuple, length: int, deterministic: bool, rand: int,
                seed: int | None, save_path: Path) -> np.ndarray:

        # deterministic - if True, next note will be always note with maximum probability
        #               - if False, next note will be sampled according to all notes probability
        # rand - % chance of selecting random token next (int [0;100])

        prediction = []
        previous_n_gram = initial_notes

        for i in range(len(initial_notes)):
            prediction.append(initial_notes[i])

        for i in range(length):
            idx = None
            if tuple(previous_n_gram) in self.n_grams:
                idx = self.n_grams_list.index(previous_n_gram)
            else:
                idx = random.randrange(len(self.probabilities))

            probs = self.probabilities[idx]
            while len(probs) == 0:
                idx = random.randrange(len(self.probabilities))
                probs = self.probabilities[idx]

            next_note = None
            if random.randrange(100) < rand:
                next_note = random.choice(self.tokens_list)
            elif deterministic:
                next_note = max(probs, key=probs.get)
            else:
                if seed is not None:
                    random.seed(seed)
                next_note = random.choices(
                    list(probs.keys()), weights=probs.values(), k=1)[0]

            if next_note is not None:
                previous_n_gram = next_note

        result = np.full((len(prediction), 128), False)
        for i in range(len(prediction)):
            if isinstance(prediction[i], int):
                result[i][prediction[i]] = True
            else:
                for j in range(len(prediction[i])):
                    note = prediction[i][j]
                    result[i][note] = True

        return result

    @staticmethod
    def get_progress_metadata() -> ProgressMetadata:
        return ProgressMetadata(x_label='Time [s]', y_label='Progress [%]', legends=['Markov Chain'])
