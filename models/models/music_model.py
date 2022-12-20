from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

import keras

from models.loss_callback import LossCallback


class MusicModel(ABC):
    """
    An abstract model for a music generation model.
    """

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def train(self, epochs: int, xtrain: any, ytrain: any, loss_callback: keras.callbacks.Callback, checkpoint_path: Path | None = None):
        """
        Trains the model with processed by `prepare_data` x/y train data. When `checkpoint_path` is provided, model
        should save progress to the pointed path. 
        """
        raise NotImplementedError

    def train_on_files(self, midi_files: list[Path], epochs: int, loss_progress: Callable[[int, float], None], checkpoint_path: Path | None = None):
        """
        Trains the model on a given set of files.
        """

        dataset = [self.prepare_data(f) for f in midi_files]
        xtrain, ytrain = self.create_dataset(dataset)

        self.train(epochs, xtrain, ytrain, LossCallback(
            loss_progress), checkpoint_path)

    @abstractmethod
    def create_dataset(self, dataset: list[tuple[any, any]]) -> tuple[any, any]:
        """
        Merges results of multiple `prepare_data` into model's input/output.
        """
        raise NotImplementedError

    @abstractmethod
    def prepare_data(self, midi_file: Path) -> tuple[any, any]:
        """
        Given a path to a midi file returns prepared input/output.
        """
        raise NotImplementedError

    @abstractmethod
    def model_summary(self) -> str:
        """
        A textual representation of the model.
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, path: Path):
        """
        Saves the current model into `path`.
        """
        raise NotImplementedError

    @abstractmethod
    def load(self, path: Path):
        """
        Loads the model from `path`.
        """
        raise NotImplementedError
