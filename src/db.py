from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import aiosqlite

from src.config import Settings


async def _get_db_path(db_path: str | None = None) -> str:
    if db_path is not None:
        return db_path
    return str(Path(Settings().db_path).expanduser().resolve())


async def init_db(db_path: str | None = None) -> None:
    resolved_path = await _get_db_path(db_path)
    Path(resolved_path).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(resolved_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                key TEXT NOT NULL,
                key_type TEXT NOT NULL,
                role TEXT,
                user_id TEXT,
                app_id TEXT,
                server_url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
            """
        )
        await db.commit()


async def store_key(
    id: str | None,
    name: str,
    key: str,
    key_type: str,
    server_url: str,
    role: str | None = None,
    user_id: str | None = None,
    app_id: str | None = None,
    db_path: str | None = None,
) -> None:
    resolved_path = await _get_db_path(db_path)
    Path(resolved_path).parent.mkdir(parents=True, exist_ok=True)
    key_id = id or str(uuid4())
    created_at = datetime.now(UTC).isoformat()
    async with aiosqlite.connect(resolved_path) as db:
        await db.execute(
            """
            INSERT INTO api_keys
            (id, name, key, key_type, role, user_id, app_id, server_url, created_at,
             is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                key = excluded.key,
                key_type = excluded.key_type,
                role = excluded.role,
                user_id = excluded.user_id,
                app_id = excluded.app_id,
                server_url = excluded.server_url,
                created_at = excluded.created_at,
                is_active = 1
            """,
            (
                key_id,
                name,
                key,
                key_type,
                role,
                user_id,
                app_id,
                server_url,
                created_at,
            ),
        )
        await db.commit()


async def get_active_key(server_url: str, db_path: str | None = None) -> dict | None:
    resolved_path = await _get_db_path(db_path)
    async with aiosqlite.connect(resolved_path) as db:
        db.row_factory = aiosqlite.Row
        cols = (
            "id, name, key, key_type, role, user_id, app_id, "
            "server_url, created_at, is_active"
        )
        async with db.execute(
            f"SELECT {cols} FROM api_keys "
            f"WHERE server_url = ? AND is_active = 1 LIMIT 1",
            (server_url,),
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return dict(row)


async def list_keys(
    server_url: str | None = None, db_path: str | None = None
) -> list[dict]:
    resolved_path = await _get_db_path(db_path)
    async with aiosqlite.connect(resolved_path) as db:
        db.row_factory = aiosqlite.Row
        cols = (
            "id, name, key, key_type, role, user_id, app_id, "
            "server_url, created_at, is_active"
        )
        if server_url is not None:
            async with db.execute(
                f"SELECT {cols} FROM api_keys "
                f"WHERE server_url = ? ORDER BY created_at DESC",
                (server_url,),
            ) as cursor:
                rows = await cursor.fetchall()
        else:
            async with db.execute(
                f"SELECT {cols} FROM api_keys ORDER BY created_at DESC"
            ) as cursor:
                rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def delete_key(id: str, db_path: str | None = None) -> None:
    resolved_path = await _get_db_path(db_path)
    async with aiosqlite.connect(resolved_path) as db:
        await db.execute("DELETE FROM api_keys WHERE id = ?", (id,))
        await db.commit()


async def deactivate_key(id: str, db_path: str | None = None) -> None:
    resolved_path = await _get_db_path(db_path)
    async with aiosqlite.connect(resolved_path) as db:
        await db.execute("UPDATE api_keys SET is_active = 0 WHERE id = ?", (id,))
        await db.commit()
