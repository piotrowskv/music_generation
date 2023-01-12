import os
from typing import Any

import numpy as np
from keras.callbacks import ModelCheckpoint
from keras.layers import LSTM, Activation, BatchNormalization, Dense, Dropout
from keras.models import Sequential

SEQUENCE_LENGTH = 100


def train_music21_network(lstm_model: Sequential,
                          lstm_input: Any,
                          lstm_output: Any) -> None:
    filepath = 'weights.hdf5'
    checkpoint = ModelCheckpoint(
        filepath,
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )
    callbacks_list = [checkpoint]
    lstm_model.fit(
        lstm_input,
        lstm_output,
        epochs=200,
        batch_size=128,
        callbacks=callbacks_list
    )


def get_music21_network(input_size: tuple[int, ...]) -> Sequential:
    model = Sequential()
    model.add(LSTM(
        160,
        input_shape=(input_size[1], input_size[2]),
        return_sequences=True,
        recurrent_activation="sigmoid"
        # recurrent_dropout=0.3  - will not run on GPU if not separated
    ))
    model.add(BatchNormalization())
    model.add(Dropout(0.02))

    # model.add(LSTM(
    #     512,
    #     return_sequences=True,
    #     # recurrent_dropout=0.3
    # ))
    # model.add(BatchNormalization())
    # model.add(Dropout(0.3))

    model.add(LSTM(160))
    model.add(BatchNormalization())
    model.add(Dropout(0.02))

    # model.add(Dense(80))
    # model.add(BatchNormalization())
    # model.add(Dropout(0.02))
    #
    # model.add(Dense(40))
    # model.add(BatchNormalization())
    # model.add(Dropout(0.02))

    model.add(Dense(40))
    model.add(Activation('relu'))     # model.add(Activation('relu' | 'tanh'))
    model.add(BatchNormalization())

    model.add(Dense(input_size[2]))
    model.add(Activation('sigmoid'))  # softmax
    model.compile(
        loss='categorical_crossentropy',
        optimizer='rmsprop'
    )

    return model


def get_music21_sequences(raw_input: Any) -> tuple[list[Any], list[Any]]:
    sequences = []
    predictions = []

    for i in range(SEQUENCE_LENGTH, len(raw_input)):
        notes_sequence = []
        for index in range(i - SEQUENCE_LENGTH, i):
            notes_sequence.append(raw_input[index])

        sequences.append(notes_sequence)
        predictions.append(raw_input[i])

    return sequences, predictions


def run_music21_features() -> None:
    features_input = []
    features_output = []

    for name in os.listdir('../../../sequences'):
        path = os.path.join('../../../sequences', name)

        try:
            midi_input = np.load(path, allow_pickle=True)
            sequences, predictions = get_music21_sequences(midi_input)
            features_input.extend(sequences)
            features_output.extend(predictions)

        except Exception:
            print(f'failed to load {name}')

    ni = np.asarray(features_input)
    no = np.asarray(features_output)

    model = get_music21_network(ni.shape)
    train_music21_network(model, ni, no)


if __name__ == '__main__':
    run_music21_features()
