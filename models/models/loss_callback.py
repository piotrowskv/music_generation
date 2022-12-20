from typing import Callable

import keras


class LossCallback(keras.callbacks.Callback):
    """
    A keras callback tracking training loss.
    """

    callback: Callable[[int, float], None]

    def __init__(self, callback: Callable[[int, float], None]):
        super(LossCallback, self).__init__()
        self.callback = callback

    def on_epoch_end(self, epoch: int, logs: dict[str, any] | None = None):
        self.callback(epoch, logs['loss'])
