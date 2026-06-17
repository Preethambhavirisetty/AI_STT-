import asyncio
import uuid
from datetime import datetime, timezone

from app.services.db import connect, hash_api_key, rows_to_dicts

_lock = asyncio.Lock()


async def create_user(name: str, api_key: str, is_admin: bool = False) -> dict:
    user = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "api_key_hash": hash_api_key(api_key),
        "is_admin": int(is_admin),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    async with _lock:
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO users (id, name, api_key_hash, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user["id"],
                    user["name"],
                    user["api_key_hash"],
                    user["is_admin"],
                    user["created_at"],
                ),
            )
    return {
        "id": user["id"],
        "name": user["name"],
        "is_admin": bool(user["is_admin"]),
        "created_at": user["created_at"],
    }


async def get_user_by_api_key(api_key: str) -> dict | None:
    async with _lock:
        with connect() as conn:
            row = conn.execute(
                """
                SELECT id, name, is_admin, created_at
                FROM users
                WHERE api_key_hash = ?
                """,
                (hash_api_key(api_key),),
            ).fetchone()
            if not row:
                return None
            user = dict(row)
            user["is_admin"] = bool(user["is_admin"])
            return user


async def list_users() -> list[dict]:
    async with _lock:
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT id, name, is_admin, created_at
                FROM users
                ORDER BY created_at DESC
                """
            ).fetchall()
            users = rows_to_dicts(rows)
            for user in users:
                user["is_admin"] = bool(user["is_admin"])
            return users
