import asyncio

from app.services.db import connect, rows_to_dicts

_lock = asyncio.Lock()


async def get_history(user_id: str, session_id: str) -> list[dict]:
    async with _lock:
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content
                FROM chat_messages
                WHERE user_id = ? AND session_id = ?
                ORDER BY id ASC
                """,
                (user_id, session_id),
            ).fetchall()
            return rows_to_dicts(rows)


async def append_message(user_id: str, session_id: str, role: str, content: str) -> None:
    async with _lock:
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages (user_id, session_id, role, content)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, session_id, role, content),
            )


async def clear_history(user_id: str, session_id: str) -> None:
    async with _lock:
        with connect() as conn:
            conn.execute(
                "DELETE FROM chat_messages WHERE user_id = ? AND session_id = ?",
                (user_id, session_id),
            )
