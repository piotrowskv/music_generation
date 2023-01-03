import sqlite3
from pathlib import Path

from app.db.repositories.training_sessions import TrainingSessionsRepository


def create_database(directory: Path) -> tuple[TrainingSessionsRepository]:
    assert not directory.exists() or directory.is_dir(
    ), "Database path has to be a folder or not exist"

    directory.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(directory.joinpath("db.sqlite"))

    training_sessions = TrainingSessionsRepository(conn)

    return (training_sessions,)
