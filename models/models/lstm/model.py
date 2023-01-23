from pathlib import Path
from typing import Any

import numpy as np
from keras.callbacks import ModelCheckpoint
from keras.layers import LSTM, Activation, BatchNormalization, Dense, Dropout
from keras.models import Sequential, load_model
from midi.bach import download_clean_dataset
from midi.decode import get_sequence_of_notes

from models.loss_callback import LossCallback

from ..music_model import MusicModel, ProgressCallback, ProgressMetadata


class MusicLstm(MusicModel):
    model: Sequential
    sequence_length: int

    _NOTES_SPAN: int = 128

    def __init__(self, sequence_length: int = 100) -> None:
        self.sequence_length = sequence_length

        self.model = Sequential()
        self.model.add(LSTM(
            256,
            input_shape=(self.sequence_length, self._NOTES_SPAN),
            return_sequences=True,
            recurrent_activation="sigmoid"
        ))
        self.model.add(BatchNormalization())
        self.model.add(Dropout(0.02))

        self.model.add(LSTM(512))
        self.model.add(BatchNormalization())
        self.model.add(Dropout(0.02))

        self.model.add(Dense(128))
        self.model.add(Activation('relu'))
        self.model.add(BatchNormalization())
        self.model.add(Dropout(0.02))

        self.model.add(Dense(self._NOTES_SPAN))
        self.model.add(Activation('sigmoid'))

        self.model.compile(
            loss='mean_squared_error',
            optimizer='rmsprop'
        )

    def train(self, epochs: int | None, xtrain: Any, ytrain: Any, progress_callback: ProgressCallback,
              checkpoint_path: Path | None = None) -> None:
        epochs = epochs or 10
        loss_callback = LossCallback(progress_callback)
        callbacks = [loss_callback] if checkpoint_path is None else [ModelCheckpoint(
            checkpoint_path,
            monitor='loss',
            verbose=0,
            save_best_only=True,
            mode='min'
        ), loss_callback]

        self.model.fit(
            xtrain,
            ytrain,
            epochs=epochs,
            batch_size=64,
            callbacks=callbacks
        )

    def create_dataset(self, dataset: list[tuple[Any, Any]]) -> tuple[Any, Any]:
        notes_input = []
        notes_output = []

        for (x, y) in dataset:
            notes_input.extend(x)
            notes_output.extend(y)

        return np.asarray(notes_input), np.asarray(notes_output)
        # return [x for (x, y) in dataset], [y for (x, y) in dataset]

    def prepare_data(self, midi_file: Path) -> tuple[Any, Any]:
        midi_input: list[tuple[int, list[bool]]] = get_sequence_of_notes(str(midi_file), False, True, False)

        notes_matrix = np.array([notes for (_, notes) in midi_input], dtype='float')

        notes_sequences = np.lib.stride_tricks.sliding_window_view(
            notes_matrix[:-1], (self.sequence_length, self._NOTES_SPAN)).squeeze()
        notes_predictions = notes_matrix[self.sequence_length:]

        """
        TODO: ideally, data should be as below. LSTM is supposed to predict
        sequences, where a single sequence is the whole song. SEQUENCE_LENGTH
        should not exist. This introduces non-uniform data (songs have different
        lengths). To remedy that songs should be padded and masked for the LSTM to ignore.
        Additionally, the model itself should be split into two: predicting note and length.
        """
        # data = np.array([x[1] for x in midi_input])
        # return data[:data.shape[0]-1, :], data[1:, :]

        return notes_sequences, notes_predictions

    @staticmethod
    def get_progress_metadata() -> ProgressMetadata:
        return ProgressMetadata(x_label='Epoch', y_label='Training loss', legends=['LSTM model'])

    def model_summary(self) -> str:
        stringlist = []
        self.model.summary(print_fn=lambda x: stringlist.append(x))
        return "\n".join(stringlist)

    def save(self, path: Path) -> None:
        self.model.save(path, save_format='h5')

    def load(self, path: Path) -> None:
        self.model = load_model(path)

    def generate(self, path: Path, seed: int | None = None) -> None:
        raise NotImplementedError


if __name__ == '__main__':
    download_bach_dataset(Path('data'))

    model = MusicLstm(128)

    model.train_on_files(
        list(Path('data/bach/chorales').glob("*.mid")), 10, lambda x: None)
