import uuid
from sqlite3 import Connection

from fastapi import UploadFile


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
                midi_file BLOB NOT NULL,
                FOREIGN KEY (session_id)
                   REFERENCES {self.SESSIONS_TABLE_NAME} (session_id)
            )""")

    async def register_session(self, model_id: str, files: list[UploadFile]) -> str:
        """
        Registers a new training session given a model id and files to train on.

        Returns
        ---
        Returns a token identifying this session.
        """

        session_id = str(uuid.uuid4())

        self._conn.execute(
            f"INSERT INTO {self.SESSIONS_TABLE_NAME}(model_id, session_id) VALUES(?, ?)",
            (model_id, session_id))

        insert_files = [(session_id, await file.read()) for file in files]
        self._conn.executemany(
            f"INSERT INTO {self.FILES_TABLE_NAME}(session_id, midi_file) VALUES(?, ?)",
            insert_files)

        self._conn.commit()

        return session_id
