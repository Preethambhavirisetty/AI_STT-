import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Generator, Iterable

from app.core.config import settings


def _db_path() -> Path:
    path = Path(settings.DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def connect() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                api_key_hash TEXT NOT NULL UNIQUE,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'bootstrap',
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id_id
            ON chat_messages(user_id, session_id, id);

            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'bootstrap',
                title TEXT NOT NULL,
                filename TEXT NOT NULL,
                chunk_count INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE INDEX IF NOT EXISTS idx_documents_user_created_at
            ON documents(user_id, created_at);

            CREATE TABLE IF NOT EXISTS rate_limits (
                key TEXT PRIMARY KEY,
                window_start REAL NOT NULL,
                request_count INTEGER NOT NULL
            );
            """
        )
        _ensure_column(conn, "chat_messages", "user_id", "TEXT NOT NULL DEFAULT 'bootstrap'")
        _ensure_column(conn, "documents", "user_id", "TEXT NOT NULL DEFAULT 'bootstrap'")
        _ensure_development_user(conn)
        _ensure_bootstrap_user(conn)


def _ensure_column(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    definition: str,
) -> None:
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})")}
    if column_name not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def _ensure_bootstrap_user(conn: sqlite3.Connection) -> None:
    if not settings.API_KEY:
        return
    conn.execute(
        """
        INSERT INTO users (id, name, api_key_hash, is_admin, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            api_key_hash = excluded.api_key_hash,
            is_admin = excluded.is_admin
        """,
        (
            "bootstrap",
            "Bootstrap Admin",
            hash_api_key(settings.API_KEY),
            1,
            datetime.now(timezone.utc).isoformat(),
        ),
    )


def _ensure_development_user(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        INSERT INTO users (id, name, api_key_hash, is_admin, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO NOTHING
        """,
        (
            "development",
            "Development User",
            "development",
            1,
            datetime.now(timezone.utc).isoformat(),
        ),
    )


def hash_api_key(api_key: str) -> str:
    return sha256(api_key.encode("utf-8")).hexdigest()


def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]
