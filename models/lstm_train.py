import os

from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Activation, BatchNormalization
from keras.callbacks import ModelCheckpoint
from midi.midi import get_sequence_of_notes, Mode

SEQUENCE_LENGTH = 100


def get_sequences(raw_input):
    notes_sequences = []
    lengths_sequences = []
    notes_predictions = []
    lengths_predictions = []

    for i in range(SEQUENCE_LENGTH, len(raw_input)):
        notes_sequence = []
        lengths_sequence = []

        for index in range(i - SEQUENCE_LENGTH, i):
            notes_sequence.append(raw_input[index][1])
            lengths_sequence.append(raw_input[index][0])
        notes_sequences.append(notes_sequence)
        lengths_sequences.append(lengths_sequence)

        notes_predictions.append(raw_input[i][1])
        lengths_predictions.append(raw_input[i][0])

    return notes_sequences, lengths_sequences, notes_predictions, lengths_predictions


def get_network(input_size):
    model = Sequential()
    model.add(LSTM(
        512,
        batch_input_shape=input_size,    # should be set up differently?
        recurrent_dropout=0.3,
        return_sequences=True
    ))
    model.add(LSTM(
        512,
        return_sequences=True,
        recurrent_dropout=0.3
    ))
    model.add(LSTM(512))
    model.add(BatchNormalization())
    model.add(Dropout(0.3))
    model.add(Dense(256))
    model.add(Activation('relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.3))
    model.add(Dense(128))
    model.add(Activation('softmax'))
    model.compile(
        loss='categorical_crossentropy',
        optimizer='rmsprop'
    )

    return model


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
        epochs=25,
        batch_size=len(lstm_input),  # should be set up differently?
        callbacks=callbacks_list
    )


if __name__ == '__main__':
    notes_input = []
    lengths_input = []
    notes_output = []
    lengths_output = []

    for name in os.listdir('../data'):  # or '../sequences' if .npy files loaded
        path = os.path.join('../data', name)

        try:
            # midi_input = np.load(path, allow_pickle=True)  # if .npy files loaded
            midi_input = get_sequence_of_notes(path, Mode.BOOLEANS, True, False)
            notes_sequences, lengths_sequences, notes_predictions, lengths_predictions = get_sequences(midi_input)
            notes_input.extend(notes_sequences)
            lengths_input.extend(lengths_sequences)
            notes_output.extend(notes_predictions)
            lengths_output.extend(lengths_predictions)
            # print(f'        loaded {name}')

        except Exception as ex:
            pass
            # print(f'failed to load {name}')

    input_size = (len(notes_input), 100, 128)
    model = get_network(input_size)
    train_network(model, notes_input, notes_output)
