from __future__ import annotations

import aiosqlite
import pytest

from src.db import (
    deactivate_key,
    delete_key,
    get_active_key,
    init_db,
    list_keys,
    store_key,
)


@pytest.mark.asyncio
async def test_init_db_creates_table(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='api_keys'"
        ) as cursor:
            row = await cursor.fetchone()
        assert row is not None
        assert row[0] == "api_keys"


@pytest.mark.asyncio
async def test_store_key_inserts_correctly(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-1",
        name="Test Key",
        key="abc123",
        key_type="user",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    result = await get_active_key("http://localhost:8000", db_path)
    assert result is not None
    assert result["id"] == "key-1"
    assert result["name"] == "Test Key"
    assert result["key"] == "abc123"
    assert result["key_type"] == "user"


@pytest.mark.asyncio
async def test_store_key_with_user_type_and_admin_role(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-admin",
        name="Admin Key",
        key="admin-key-456",
        key_type="user",
        role="admin",
        user_id="user-1",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    result = await get_active_key("http://localhost:8000", db_path)
    assert result is not None
    assert result["key_type"] == "user"
    assert result["role"] == "admin"
    assert result["user_id"] == "user-1"


@pytest.mark.asyncio
async def test_store_key_with_application_type_and_app_id(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-app",
        name="App Key",
        key="app-key-789",
        key_type="application",
        app_id="app-123",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    result = await get_active_key("http://localhost:8000", db_path)
    assert result is not None
    assert result["key_type"] == "application"
    assert result["app_id"] == "app-123"
    assert result["role"] is None


@pytest.mark.asyncio
async def test_get_active_key_returns_active_key(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-1",
        name="First Key",
        key="key-1-value",
        key_type="user",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    await store_key(
        id="key-2",
        name="Second Key",
        key="key-2-value",
        key_type="user",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    result = await get_active_key("http://localhost:8000", db_path)
    assert result is not None
    assert result["id"] in ("key-1", "key-2")


@pytest.mark.asyncio
async def test_get_active_key_returns_none_when_no_keys(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    result = await get_active_key("http://localhost:8000", db_path)
    assert result is None


@pytest.mark.asyncio
async def test_get_active_key_ignores_inactive_keys(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-active",
        name="Active Key",
        key="active-key",
        key_type="user",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    await store_key(
        id="key-inactive",
        name="Inactive Key",
        key="inactive-key",
        key_type="user",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    await deactivate_key("key-inactive", db_path)
    result = await get_active_key("http://localhost:8000", db_path)
    assert result is not None
    assert result["id"] == "key-active"


@pytest.mark.asyncio
async def test_list_keys_returns_all_keys(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-1",
        name="Key 1",
        key="key-1-value",
        key_type="user",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    await store_key(
        id="key-2",
        name="Key 2",
        key="key-2-value",
        key_type="application",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    results = await list_keys(db_path=db_path)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_list_keys_filters_by_server_url(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-server1",
        name="Server1 Key",
        key="server1-key",
        key_type="user",
        server_url="http://server1:8000",
        db_path=db_path,
    )
    await store_key(
        id="key-server2",
        name="Server2 Key",
        key="server2-key",
        key_type="user",
        server_url="http://server2:8000",
        db_path=db_path,
    )
    results = await list_keys(server_url="http://server1:8000", db_path=db_path)
    assert len(results) == 1
    assert results[0]["id"] == "key-server1"


@pytest.mark.asyncio
async def test_delete_key_deletes_by_id(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-to-delete",
        name="To Delete",
        key="delete-me",
        key_type="user",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    await delete_key("key-to-delete", db_path)
    result = await get_active_key("http://localhost:8000", db_path)
    assert result is None


@pytest.mark.asyncio
async def test_delete_key_with_nonexistent_id(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-1",
        name="Key 1",
        key="key-1-value",
        key_type="user",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    await delete_key("nonexistent-id", db_path)
    results = await list_keys(db_path=db_path)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_deactivate_key_marks_inactive(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-to-deactivate",
        name="To Deactivate",
        key="deactivate-me",
        key_type="user",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    await deactivate_key("key-to-deactivate", db_path)
    result = await get_active_key("http://localhost:8000", db_path)
    assert result is None
    results = await list_keys(db_path=db_path)
    assert len(results) == 1
    assert results[0]["is_active"] == 0


@pytest.mark.asyncio
async def test_store_key_creates_directory_if_not_exists(tmp_path):
    db_path = str(tmp_path / "subdir" / "nested" / "test.db")
    await init_db(db_path)
    await store_key(
        id="key-1",
        name="Test Key",
        key="abc123",
        key_type="user",
        server_url="http://localhost:8000",
        db_path=db_path,
    )
    result = await get_active_key("http://localhost:8000", db_path)
    assert result is not None
    assert result["key"] == "abc123"
