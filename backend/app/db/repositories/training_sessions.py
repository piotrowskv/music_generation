import datetime
import json
import uuid
from dataclasses import dataclass
from sqlite3 import Connection

from fastapi import UploadFile

from app.db.repositories.training_progress import ProgressList


@dataclass(frozen=True)
class TrainingSessionData:
    model_id: str
    created_at: datetime.datetime
    training_file_names: list[str]


@dataclass(frozen=True)
class TrainingSessionSummary:
    session_id: str
    model_id: str
    created_at: datetime.datetime
    file_count: int
    training_completed: bool


@dataclass(frozen=True)
class TrainingData:
    model_id: str
    midi: list[bytes]
    full_progress_list: ProgressList | None


class TrainingSessionsRepository:
    SESSIONS_TABLE_NAME = "training_sessions"
    FILES_TABLE_NAME = "training_session_files"

    _conn: Connection

    def __init__(self, connection: Connection):
        self._conn = connection

        self._conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.SESSIONS_TABLE_NAME}(
                session_id TEXT NOT NULL PRIMARY KEY,
                model_id TEXT NOT NULL,
                progress_json TEXT,
                error_message TEXT,
                create_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            )""")
        self._conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.FILES_TABLE_NAME}(
                session_id TEXT NOT NULL,
                file_name TEXT NOT NULL,
                midi_file BLOB NOT NULL,
                FOREIGN KEY (session_id)
                   REFERENCES {self.SESSIONS_TABLE_NAME} (session_id)
            )""")

    async def register_session(self, model_id: str, files: list[UploadFile]) -> str:
        """
        Registers a new training session given a model id and files to train on.

        Returns
        ---
        Returns a session_id identifying this session.
        """

        session_id = str(uuid.uuid4())

        self._conn.execute(
            f"INSERT INTO {self.SESSIONS_TABLE_NAME}(model_id, session_id) VALUES(?, ?)",
            (model_id, session_id))

        insert_files = [(session_id, file.filename, await file.read()) for file in files]
        self._conn.executemany(
            f"INSERT INTO {self.FILES_TABLE_NAME}(session_id, file_name, midi_file) VALUES(?, ?, ?)",
            insert_files)

        self._conn.commit()

        return session_id

    def mark_training_as_failed(self, session_id: str, error_message: str) -> None:
        """
        Marks some existing session as failed by saving it's error message.
        """

        self._conn.execute(f"""
            UPDATE {self.SESSIONS_TABLE_NAME}
            SET error_message=?
            WHERE session_id=?
            """, (error_message, session_id))

        self._conn.commit()

    def get_session(self, session_id: str) -> TrainingSessionData | None:
        """
        Finds a training session and returns some information about it.
        Returns None if the session was not found.
        """

        model_id: str
        create_date: datetime.datetime
        filenames: list[str] = []

        for r in self._conn.execute(f"""
            SELECT s.model_id, s.create_date, f.file_name FROM {self.SESSIONS_TABLE_NAME} AS s
            INNER JOIN {self.FILES_TABLE_NAME} AS f ON s.session_id=f.session_id
            WHERE s.session_id=?
            """, (session_id,)):
            model_id = r[0]
            create_date = datetime.datetime.strptime(r[1], '%Y-%m-%d %H:%M:%S')
            filenames.append(r[2])

        if len(filenames) == 0:
            return None

        return TrainingSessionData(model_id, create_date, filenames)

    def get_all_sessions(self, model_id: str | None) -> list[TrainingSessionSummary]:
        """
        Finds all training sessions and returns some information about them.
        If model_id is provided, will filter by it
        """

        sessions: list[TrainingSessionSummary] = []

        for r in self._conn.execute(f"""
            SELECT s.session_id, s.model_id, s.create_date, COUNT(s.session_id), s.progress_json IS NOT NULL
            FROM {self.SESSIONS_TABLE_NAME} AS s
            INNER JOIN {self.FILES_TABLE_NAME} AS f ON s.session_id=f.session_id
            {'WHERE s.model_id=?' if model_id is not None else ''}
            GROUP BY s.session_id
            """, (model_id,) if model_id is not None else ()):
            create_date = datetime.datetime.strptime(r[2], '%Y-%m-%d %H:%M:%S')
            sessions.append(TrainingSessionSummary(r[0], r[1], create_date, r[3], bool(r[4])))

        return sessions

    def get_training_data(self, session_id: str) -> TrainingData | None:
        """
        Finds a training session and returns training data for it.
        Returns None if the session was not found.
        """

        model_id: str
        midi: list[bytes] = []
        progress_list_json: str | None

        for r in self._conn.execute(f"""
            SELECT s.model_id, s.progress_json, f.midi_file FROM {self.SESSIONS_TABLE_NAME} AS s
            INNER JOIN {self.FILES_TABLE_NAME} AS f ON s.session_id=f.session_id
            WHERE s.session_id=?
            """, (session_id,)):
            model_id = r[0]
            progress_list_json = r[1]
            midi.append(r[2])

        if len(midi) == 0:
            return None

        return TrainingData(model_id, midi, None if progress_list_json is None else json.loads(progress_list_json))

    def save_training_progress(self, session_id: str, progresses: ProgressList) -> None:
        """
        Saves finished progress list of a training session.
        """
        self._conn.execute(f"""
            UPDATE {self.SESSIONS_TABLE_NAME}
            SET progress_json=?
            WHERE session_id=?
            """, (json.dumps(progresses), session_id))

        self._conn.commit()
