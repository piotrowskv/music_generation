from pathlib import Path
from typing import Any

import numpy as np
from keras.callbacks import ModelCheckpoint
from keras.layers import LSTM, Activation, BatchNormalization, Dense, Dropout
from keras.models import Sequential, load_model
from midi.decode import get_sequence_of_notes

from models.loss_callback import LossCallback

from ..music_model import MusicModel, ProgressCallback, ProgressMetadata

SEQUENCE_LENGTH = 100


class MusicLstm(MusicModel):
    model: Sequential

    def __init__(self, input_shape: int):
        self.model = Sequential()
        self.model.add(LSTM(
            256,
            input_shape=(SEQUENCE_LENGTH, input_shape),
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

        self.model.add(Dense(128))
        self.model.add(Activation('sigmoid'))

        self.model.compile(
            loss='mean_squared_error',
            optimizer='rmsprop'
        )

    def train(self, epochs: int, xtrain: Any, ytrain: Any, progress_callback: ProgressCallback, checkpoint_path: Path | None = None) -> None:
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
            batch_size=256,
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
        midi_input = get_sequence_of_notes(str(midi_file), True, True, False)

        notes_sequences = []
        notes_predictions = []

        for i in range(len(midi_input) - SEQUENCE_LENGTH):
            notes_sequence = [x[1] for x in midi_input[i:i+SEQUENCE_LENGTH]]

            notes_sequences.append(notes_sequence)
            notes_predictions.append(midi_input[i+SEQUENCE_LENGTH][1])

        return np.array(notes_sequences), np.array(notes_predictions)

        """
        TODO: ideally, data should be as below. LSTM is supposed to predict
        sequences, where a single sequence is the whole song. SEQUENCE_LENGTH
        should not exist. This introduces non-uniform data (songs have different
        lengths). To remedy that songs should be padded and masked for the LSTM to ignore.
        Additionally, the model itself should be split into two: predicting note and length.
        """
        # data = np.array([x[1] for x in midi_input])
        # return data[:data.shape[0]-1, :], data[1:, :]

    def get_progress_metadata(self) -> ProgressMetadata:
        return ProgressMetadata(x_label='Epoch', y_label='Training loss', legends=['LSTM model'])

    def model_summary(self) -> str:
        stringlist = []
        self.model.summary(print_fn=lambda x: stringlist.append(x))
        return "\n".join(stringlist)

    def save(self, path: Path) -> None:
        self.model.save(path)

    def load(self, path: Path) -> None:
        self.model = load_model(path)


if __name__ == '__main__':
    model = MusicLstm(128)

    model.train_on_files(
        list(Path('./data').glob("*.mid")), 10, lambda x: None)
