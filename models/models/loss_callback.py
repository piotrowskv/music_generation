from typing import Any

import keras

from models.music_model import ProgressCallback


class LossCallback(keras.callbacks.Callback):
    """
    A keras callback tracking training loss.
    """

    callback: ProgressCallback

    def __init__(self, callback: ProgressCallback):
        super(LossCallback, self).__init__()
        self.callback = callback

    def on_epoch_end(self, epoch: int, logs: dict[str, Any] | None = None) -> None:
        if logs is not None:
            self.callback([(epoch+1, logs['loss'])])
