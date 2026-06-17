import asyncio
from datetime import datetime, timezone

from app.services.db import connect, rows_to_dicts

_lock = asyncio.Lock()


async def register(user_id: str, doc_id: str, title: str, filename: str, chunk_count: int) -> dict:
    record = {
        "id": doc_id,
        "user_id": user_id,
        "title": title,
        "filename": filename,
        "chunk_count": chunk_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    async with _lock:
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (id, user_id, title, filename, chunk_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record["id"],
                    record["user_id"],
                    record["title"],
                    record["filename"],
                    record["chunk_count"],
                    record["created_at"],
                ),
            )
    return record


async def list_docs(user_id: str) -> list[dict]:
    async with _lock:
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, filename, chunk_count, created_at
                FROM documents
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
            return rows_to_dicts(rows)


async def get_doc(user_id: str, doc_id: str) -> dict | None:
    async with _lock:
        with connect() as conn:
            row = conn.execute(
                """
                SELECT id, title, filename, chunk_count, created_at
                FROM documents
                WHERE user_id = ? AND id = ?
                """,
                (user_id, doc_id),
            ).fetchone()
            return dict(row) if row else None


async def remove_doc(user_id: str, doc_id: str) -> bool:
    async with _lock:
        with connect() as conn:
            cursor = conn.execute(
                "DELETE FROM documents WHERE user_id = ? AND id = ?",
                (user_id, doc_id),
            )
            return cursor.rowcount > 0
