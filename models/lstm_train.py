import os
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Activation, BatchNormalization
from keras.callbacks import ModelCheckpoint
from midi.midi import get_sequence_of_notes, Mode

SEQUENCE_LENGTH = 100


def train_network(lstm_model, lstm_input, lstm_output):
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
        epochs=200,         # TODO: 200
        batch_size=64,      # TODO: 128
        callbacks=callbacks_list
    )


# def get_hot_sequences(raw_input):
#     notes_sequences = []
#     lengths_sequences = []
#     notes_predictions = []
#     lengths_predictions = []
#
#     for i in range(SEQUENCE_LENGTH, len(raw_input)):
#         notes_sequence = []
#         lengths_sequence = []
#
#         for index in range(i - SEQUENCE_LENGTH, i):
#             notes_sequence.append(raw_input[index][1])
#             lengths_sequence.append(raw_input[index][0])
#         notes_sequences.append(notes_sequence)
#         lengths_sequences.append(lengths_sequence)
#
#         notes_predictions.append(raw_input[i][1])
#         lengths_predictions.append(raw_input[i][0])
#
#     return notes_sequences, lengths_sequences, notes_predictions, lengths_predictions
#
#
# def get_hot_network(input_size):
#     model = Sequential()
#     model.add(LSTM(
#         512,
#         input_shape=(input_size[1], input_size[2]),
#         return_sequences=True,
#         recurrent_activation="sigmoid"
#         # recurrent_dropout=0.3  - will not run on GPU if not separated
#     ))
#     model.add(BatchNormalization())
#     model.add(Dropout(0.02))
#
#     # model.add(LSTM(
#     #     512,
#     #     return_sequences=True,
#     #     # recurrent_dropout=0.3
#     # ))
#     # model.add(BatchNormalization())
#     # model.add(Dropout(0.3))
#
#     model.add(LSTM(512))
#     model.add(BatchNormalization())
#     model.add(Dropout(0.02))
#
#     model.add(Dense(256))
#     model.add(BatchNormalization())
#     model.add(Dropout(0.02))
#
#     model.add(Dense(128))
#     model.add(Activation('relu'))     # model.add(Activation('relu' | 'tanh'))
#     model.add(BatchNormalization())
#     model.add(Dropout(0.02))
#
#     model.add(Dense(64))
#     model.add(Activation('sigmoid'))  # softmax
#     model.compile(
#         loss='categorical_crossentropy',
#         optimizer='rmsprop'
#     )
#
#     return model
#
#
# def run_hot_features():
#     notes_input = []
#     lengths_input = []
#     notes_output = []
#     lengths_output = []
#
#     for name in os.listdir('../data'):  # or '../sequences' if .npy files loaded
#         path = os.path.join('../data', name)
#
#         try:
#             # midi_input = np.load(path, allow_pickle=True)  # if .npy files loadeds
#             midi_input = get_sequence_of_notes(path, Mode.VELOCITIES, False, False)
#             midi_input = midi_input[0]
#             notes_sequences, lengths_sequences, notes_predictions, lengths_predictions = get_hot_sequences(midi_input)
#             notes_input.extend(notes_sequences)
#             lengths_input.extend(lengths_sequences)
#             notes_output.extend(notes_predictions)
#             lengths_output.extend(lengths_predictions)
#             # print(f'        loaded {name}')
#
#         except Exception as ex:
#             # pass
#             print(f'failed to load {name}')
#
#     ni = np.asarray(notes_input)
#     ni = ni[:, :, 23:87]  # 27 - 86 in use, 22 - 86 to round to 64
#     no = np.asarray(notes_output)
#     no = no[:, 23:87]
#
#     # FIND HIGHEST AND LOWEST NOTES
#     # k_min = 128
#     # k_max = 0
#     # for num, s in enumerate(notes_input):
#     #     print(num)
#     #     for keys in s:
#     #         for pos, value in enumerate(keys):
#     #             if value:
#     #                 if pos < k_min:
#     #                     k_min = pos
#     #                 if pos > k_max:
#     #                     k_max = pos
#     #
#     # print()
#     # print(k_min)
#     # print(k_max)
#
#     input_size = (len(ni), SEQUENCE_LENGTH, 64)  # notes_input
#     model = get_hot_network(input_size)
#     train_network(model, ni, no)  # notes_input, notes_output

def get_music21_network(input_size):
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

    # model.add(Dense(10))
    model.add(Dense(5))
    model.add(Activation('sigmoid'))  # softmax
    model.compile(
        loss='categorical_crossentropy',
        optimizer='rmsprop'
    )

    return model


def get_music21_sequences(raw_input):
    sequences = []
    predictions = []

    for i in range(SEQUENCE_LENGTH, len(raw_input)):
        notes_sequence = []
        for index in range(i - SEQUENCE_LENGTH, i):
            notes_sequence.append(raw_input[index])

        sequences.append(notes_sequence)
        predictions.append(raw_input[i])

    return sequences, predictions


def run_music21_features():
    midi_input = np.load('../sequences/chords21.npy', allow_pickle=True)
    midi_input = np.transpose(midi_input)
    sequences, predictions = get_music21_sequences(midi_input)
    ni = np.asarray(sequences)
    no = np.asarray(predictions)
    # input_size = (len(ni), SEQUENCE_LENGTH, 10)
    input_size = (len(ni), SEQUENCE_LENGTH, 5)
    model = get_music21_network(input_size)
    train_network(model, ni, no)


if __name__ == '__main__':
    run_music21_features()
