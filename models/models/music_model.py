from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeAlias


@dataclass(frozen=True)
class ProgressMetadata:
    x_label: str
    y_label: str
    legends: list[str]


SeriesProgress: TypeAlias = list[tuple[float, float]]


@dataclass(frozen=True)
class TrainingProgress:
    finished: bool
    series: SeriesProgress


CompleteProgressCallback: TypeAlias = Callable[[TrainingProgress], None]

# This callback is called with the progress of a model training.
# Called with a list of chart series together with (x, y) coords
ProgressCallback: TypeAlias = Callable[[SeriesProgress], None]


class MusicModel(ABC):
    """
    An abstract model for a music generation model.
    """

    @abstractmethod
    def train(self, epochs: int, xtrain: Any, ytrain: Any, progress_callback: ProgressCallback, checkpoint_path: Path | None = None) -> None:
        """
        Trains the model with processed by `prepare_data` x/y train data. When `checkpoint_path` is provided, model
        should save progress to the pointed path. 
        """
        raise NotImplementedError

    def train_on_files(self, midi_files: list[Path], epochs: int, progress_callback: CompleteProgressCallback, checkpoint_path: Path | None = None) -> None:
        """
        Trains the model on a given set of files.
        """

        dataset = [self.prepare_data(f) for f in midi_files]
        xtrain, ytrain = self.create_dataset(dataset)

        self.train(
            epochs,
            xtrain,
            ytrain,
            lambda x: progress_callback(
                TrainingProgress(finished=False, series=x)),
            checkpoint_path)

        progress_callback(TrainingProgress(finished=True, series=[]))

    @abstractmethod
    def get_progress_metadata(self) -> ProgressMetadata:
        """
        Returns information needed to describe the progress data.
        """
        raise NotImplementedError

    @abstractmethod
    def create_dataset(self, dataset: list[tuple[Any, Any]]) -> tuple[Any, Any]:
        """
        Merges results of multiple `prepare_data` into model's input/output.
        """
        raise NotImplementedError

    @abstractmethod
    def prepare_data(self, midi_file: Path) -> tuple[Any, Any]:
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
    def save(self, path: Path) -> None:
        """
        Saves the current model into `path`.
        """
        raise NotImplementedError

    @abstractmethod
    def load(self, path: Path) -> None:
        """
        Loads the model from `path`.
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, path: Path, seed: int | list[int] | None = None) -> None:
        """
        Generates a sample and saves it as a .mid file as `path`.
        """
        raise NotImplementedError
