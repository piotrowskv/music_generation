import datetime
import uuid
from dataclasses import dataclass
from sqlite3 import Connection

from fastapi import UploadFile


@dataclass(frozen=True)
class TrainingSessionData:
    model_id: str
    created_at: datetime.datetime
    training_file_names: list[str]


@dataclass(frozen=True)
class TrainingData:
    model_id: str
    midi: list[bytes]


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

    async def get_session(self, session_id: str) -> TrainingSessionData | None:
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
            create_date = datetime.datetime.strptime(
                r[1], '%Y-%m-%d %H:%M:%S')
            filenames.append(r[2])

        if len(filenames) == 0:
            return None

        return TrainingSessionData(model_id, create_date, filenames)

    async def get_training_data(self, session_id: str) -> TrainingData | None:
        """
        Finds a training session and returns training data for it.
        Returns None if the session was not found.
        """

        model_id: str
        midi: list[bytes] = []

        for r in self._conn.execute(f"""
            SELECT s.model_id, f.midi_file FROM {self.SESSIONS_TABLE_NAME} AS s
            INNER JOIN {self.FILES_TABLE_NAME} AS f ON s.session_id=f.session_id
            WHERE s.session_id=?
            """, (session_id,)):
            model_id = r[0]
            midi.append(r[1])

        if len(midi) == 0:
            return None

        return TrainingData(model_id, midi)
