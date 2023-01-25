from pathlib import Path
from typing import Any

import numpy as np
from keras import Model
from keras.callbacks import ModelCheckpoint
from keras.layers import (LSTM, Activation, BatchNormalization, Dense, Dropout,
                          Flatten, Input, LeakyReLU, Multiply, Permute,
                          RepeatVector)
from keras.models import load_model
from midi.bach import download_clean_dataset
from midi.decode import get_sequence_of_notes
from midi.encode import get_file_from_standard_features

from models.loss_callback import LossCallback

from ..music_model import MusicModel, ProgressCallback, ProgressMetadata


class MusicLstm(MusicModel):
    model: Model
    sequence_length: int

    _NOTES_SPAN: int = 128

    def __init__(self, sequence_length: int = 25, metrics: list[Any] = []) -> None:
        self.sequence_length = sequence_length

        self.model = self._define_model()

        self.model.compile(
            loss='mean_squared_error',
            optimizer='rmsprop',
            metrics=metrics
        )

    def _define_model(self) -> Model:
        input = Input((self.sequence_length, self._NOTES_SPAN))
        x = LSTM(1024, return_sequences=True)(input)
        x = LeakyReLU()(x)
        x = BatchNormalization()(x)
        x = Dropout(0.3)(x)

        # attention = Dense(1, activation='tanh')(x)
        # attention = Flatten()(attention)
        # attention = Activation('softmax')(attention)
        # attention = RepeatVector(1024)(attention)
        # attention = Permute((2, 1))(attention)

        # multiplied = Multiply()((x, attention))
        # sent_representation = Dense(512)(multiplied)
        sent_representation = Dense(512)(x)

        x = Dense(512)(sent_representation)
        x = LeakyReLU()(x)
        x = BatchNormalization()(x)
        x = Dropout(0.22)(x)

        x = LSTM(512, return_sequences=True)(x)
        x = LeakyReLU()(x)
        x = BatchNormalization()(x)
        x = Dropout(0.22)(x)

        # attention = Dense(1, activation='tanh')(x)
        # attention = Flatten()(attention)
        # attention = Activation('softmax')(attention)
        # attention = RepeatVector(512)(attention)
        # attention = Permute((2, 1))(attention)

        sent_representation = Dense(256)(x)
        # multiplied = Multiply()([x, attention])
        # sent_representation = Dense(256)(multiplied)

        x = Dense(256)(sent_representation)
        x = LeakyReLU()(x)
        x = BatchNormalization()(x)
        x = Dropout(0.22)(x)

        x = LSTM(128)(x)
        x = LeakyReLU()(x)
        x = BatchNormalization()(x)
        x = Dropout(0.22)(x)

        x = Dense(self._NOTES_SPAN, activation='sigmoid')(x)

        return Model(input, x)

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
    ds = Path('data')
    download_clean_dataset(ds)

    model = MusicLstm(sequence_length=20)
    # plot_model(model.model, show_layer_names=False, show_shapes=True, dpi=300)
    print(model.model_summary())
    # model.load(Path('saved_models/big_seq20_onetrack_noattention'))

    # files = list(ds.joinpath('midi_dataset/3_tracks').glob("bwv???.mid"))

    # print(files[0])
    # model.prepare_data(files[0])
    # model.train_on_files([files[0]], 10, lambda x: None)
    # model.train_on_files(files, 10, lambda x: None)

    # np.random.seed(2)
    # gen = []
    # x, y = model.prepare_data(files[0])
    # x: np.array = x[0:1, :, :]

    # for _ in range(100):
    #     o = model.model(x)[0]
    #     thresh = np.random.random(len(o))
    #     o = o > thresh
    #     gen.append(o)
    #     a = np.array(o, dtype='float').reshape((1, 1, 128))
    #     x = np.concatenate((x[:, 1:, :], a), axis=1)

    # lens = [(8 if i % 2 else 8) for (i, x) in enumerate(gen)]
    # get_file_from_standard_features(np.array(gen), 1000000, Path(
    #     'out_midis/big_seq20_onetrack_noattention.mid'), False, True, False, lens)

    # model.save(Path('saved_models/big_seq20_onetrack_noattention'))
