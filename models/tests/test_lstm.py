import numpy as np

from models.lstm.model import MusicLstm


def test_lstm_creates_dataset():
    lstm = MusicLstm(5)

    xtrain, ytrain = lstm.create_dataset([
        (
            [[[1, 2, 3], [4, 5, 6]], [[10, 11, 12], [13, 14, 15]]],
            [[8, 8, 8], [9, 9, 9]],
        ),
        (
            [[[-1, -2, -3], [-4, -5, -6]], [[-10, -11, -12], [-13, -14, -15]]],
            [[-8, -8, -8], [-9, -9, -9]],
        ),
    ])

    assert (xtrain == np.array([[[1, 2, 3], [4, 5, 6]], [[10, 11, 12], [13, 14, 15]], [
        [-1, -2, -3], [-4, -5, -6]], [[-10, -11, -12], [-13, -14, -15]]])).any()
    assert (ytrain == np.array(
        [[8, 8, 8], [9, 9, 9], [-8, -8, -8], [-9, -9, -9]])).any()
