import shutil
import tempfile
import uuid
from pathlib import Path
from typing import AsyncIterator

from models.music_model import MusicModel, TrainingProgress

from app.db import TrainingProgressRepository


class TrainingManager:
    _progress_repo: TrainingProgressRepository

    def __init__(self, progress_repo: TrainingProgressRepository):
        self._progress_repo = progress_repo

    def add_model(self, session_id: str, model: MusicModel, midi_bytes: list[bytes]) -> None:
        """
        Adds a model to track for progress. Will block until the model is fully trained.
        """

        # midi package does not support in-memory midi. Midi has to be
        # materialized into files in the real file system.
        dir = Path(tempfile.mkdtemp())

        files: list[Path] = []
        for b in midi_bytes:
            p = dir.joinpath(f'{uuid.uuid4()}.mid')
            with open(p, 'wb') as f:
                f.write(b)
            files.append(p)

        model.train_on_files(
            files, 10, lambda progress: self._progress_repo.publish_progress(session_id, progress))

        shutil.rmtree(dir)

    async def subscribe(self, session_id: str) -> AsyncIterator[TrainingProgress]:
        return self._progress_repo.subscribe(session_id)
