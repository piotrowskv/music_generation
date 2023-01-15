import sqlite3
from pathlib import Path

from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis

from app.db.repositories.training_progress import TrainingProgressRepository
from app.db.repositories.training_sessions import TrainingSessionsRepository
from app.env import Env


def create_database(directory: Path) -> tuple[TrainingSessionsRepository, TrainingProgressRepository]:
    assert not directory.exists() or directory.is_dir(
    ), "Database path has to be a folder or not exist"

    directory.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(directory.joinpath("db.sqlite"), check_same_thread=False)

    training_sessions = TrainingSessionsRepository(conn)

    sr = SyncRedis(host=Env.redis_hostname,
                   port=Env.redis_port, retry_on_timeout=True, decode_responses=True)
    ar: AsyncRedis = AsyncRedis(host=Env.redis_hostname,
                                port=Env.redis_port, retry_on_timeout=True, decode_responses=True)

    training_progress = TrainingProgressRepository(sr, ar)

    return training_sessions, training_progress
