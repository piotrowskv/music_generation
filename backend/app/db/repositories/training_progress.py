from dataclasses import asdict, dataclass
from typing import AsyncIterable

from dataclasses_json import dataclass_json
from models.music_model import SeriesProgress, TrainingProgress
from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis


@dataclass_json
@dataclass(frozen=True)
class _TrainingProgress:
    finished: bool
    series: SeriesProgress


class TrainingProgressRepository:
    """
    A live Redis Stream connection for training progress tracking.
    """
    _DATA_KEY = 'data'

    # synchronuous version is used for writes, asynchronuous for reads
    _sr: SyncRedis
    _ar: AsyncRedis

    def __init__(self, sr: SyncRedis, ar: AsyncRedis):
        self._sr = sr
        self._ar = ar

    def publish_progress(self, session_id: str, progress: TrainingProgress) -> None:
        serialized = _TrainingProgress.from_dict(asdict(progress)).to_json()
        self._sr.xadd(session_id, {self._DATA_KEY: serialized})

    async def subscribe(self, session_id: str) -> AsyncIterable[TrainingProgress]:
        last_id = 0
        while True:
            response = await self._ar.xread(
                {session_id: last_id}, count=2, block=500
            )

            if response:
                _, messages = response[0]
                last_id, data = messages[0]

                progress = _TrainingProgress.from_json(data[self._DATA_KEY])
                progress = TrainingProgress(progress.finished, progress.series)

                yield progress

                if progress.finished:
                    return
