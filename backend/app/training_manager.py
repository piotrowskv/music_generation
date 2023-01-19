import shutil
import tempfile
import uuid
from pathlib import Path
from typing import AsyncIterable

from models.music_model import MusicModel, TrainingProgress

from app.db import TrainingProgressRepository, TrainingSessionsRepository
from app.db.repositories.training_progress import ProgressList


class TrainingManager:
    _progress_repo: TrainingProgressRepository
    _sessions_repo: TrainingSessionsRepository

    def __init__(self, progress_repo: TrainingProgressRepository, sessions_repo: TrainingSessionsRepository):
        self._progress_repo = progress_repo
        self._sessions_repo = sessions_repo

    def add_model(self, session_id: str, model: MusicModel, midi_bytes: list[bytes]) -> None:
        """
        Adds a model to track for progress. Will block until the model is fully trained.
        Progress is emitted to `TrainingProgressRepository` and once the training is finished
        it is persisted in `TrainingSessionsRepository`.
        """

        progress: ProgressList = []

        def on_progress(event: TrainingProgress) -> None:
            progress.append(event.series)
            self._progress_repo.publish_progress(session_id, event)

        # midi package does not support in-memory midi. Midi has to be
        # materialized into files in the real file system.
        dir = Path(tempfile.mkdtemp())
        try:
            files: list[Path] = []
            for b in midi_bytes:
                p = dir.joinpath(f'{uuid.uuid4()}.mid')
                with open(p, 'wb') as f:
                    f.write(b)
                files.append(p)

            model.train_on_files(files, 10, on_progress)

            self._sessions_repo.save_training_progress(session_id, progress)
        except Exception as ex:
            msg = str(ex)
            self._progress_repo.publish_error(session_id, msg)
            self._sessions_repo.mark_training_as_failed(session_id, msg)
        finally:
            shutil.rmtree(dir)

    async def subscribe(self, session_id: str) -> AsyncIterable[ProgressList]:
        return self._progress_repo.subscribe(session_id)
