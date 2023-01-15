from dataclasses import asdict, dataclass
from typing import AsyncIterable, TypeAlias

from models.music_model import SeriesProgress, TrainingProgress
from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis

ProgressList: TypeAlias = list[SeriesProgress]


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
        serialized = progress.to_json()
        self._sr.xadd(session_id, {self._DATA_KEY: serialized})

    async def subscribe(self, session_id: str) -> AsyncIterable[ProgressList]:
        last_id = 0
        while True:
            response = await self._ar.xread(
                {session_id: last_id}, block=500
            )

            if response:
                _, messages = response[0]

                out: ProgressList = []
                finished = False

                for msg in messages:
                    last_id, data = msg

                    progress = TrainingProgress.from_json(data[self._DATA_KEY])

                    out.append(progress.series)
                    finished |= progress.finished

                yield out

                if finished:
                    return
