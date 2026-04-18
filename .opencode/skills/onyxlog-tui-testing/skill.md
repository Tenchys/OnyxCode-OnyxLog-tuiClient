---
name: onyxlog-tui-testing
description: Convenciones de testing para el OnyxLog TUI Client. Fixtures pytest, patron de tests, pytest-asyncio, cobertura y mocks httpx.
metadata:
  audience: developers
  workflow: onyxlog-tui
---

## Fixtures base (conftest.py)

```python
from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
import httpx

from src.app import OnyxLogApp
from src.db import init_db, store_key
from src.api.client import OnyxLogClient


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_connection(tmp_path):
    db_path = str(tmp_path / "test_keys.db")
    conn = await aiosqlite.connect(db_path)
    await init_db(conn)
    yield conn
    await conn.close()


@pytest_asyncio.fixture
def mock_client():
    client = MagicMock(spec=OnyxLogClient)
    client._api_key = "test-key-12345"
    client.set_api_key = MagicMock()
    client.clear_api_key = MagicMock()
    return client


@pytest_asyncio.fixture
def app_instance(mock_client):
    app = OnyxLogApp()
    app.client = mock_client
    return app
```

## Mock de respuestas HTTP con httpx

```python
import httpx
import pytest


@pytest.fixture
def httpx_mock_client():
    def _mock_response(status_code: int, json_data: dict | None = None):
        return httpx.Response(status_code=status_code, json=json_data or {})

    return _mock_response


class MockTransport(httpx.AsyncBaseTransport):
    def __init__(self, responses: dict[str, httpx.Response]):
        self.responses = responses

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        key = f"{request.method} {request.url.path}"
        return self.responses.get(key, httpx.Response(404, json={"error_code": "NOT_FOUND", "message": "Not found"}))


@pytest_asyncio.fixture
async def real_client():
    mock_responses = {
        "POST /api/v1/auth/login": httpx.Response(200, json={
            "user": {"id": "user-1", "username": "testuser", "role": "admin"},
            "api_key": "test-api-key-12345",
        }),
    }
    transport = MockTransport(mock_responses)
    client = OnyxLogClient(base_url="http://test")
    client._client = httpx.AsyncClient(transport=transport)
    yield client
    await client.close()
```

## Patron de test

- Un archivo por modulo: `test_auth.py` para `api/auth.py`
- Clase `TestXxx` por entidad
- Metodos descriptivos: `test_login_success`, `test_login_invalid_credentials`
- Estructura AAA: Arrange, Act, Assert

```python
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.api.auth import login
from src.api.client import ApiClientError


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, mock_client):
        mock_client._request = AsyncMock(return_value={
            "user": {"id": "user-1", "username": "testuser", "role": "admin", "is_active": True},
            "api_key": "test-key-12345",
        })

        result = await login(mock_client, "testuser", "password123")

        mock_client._request.assert_called_once_with(
            "POST", "/auth/login", json={"username": "testuser", "password": "password123"}
        )
        assert result.api_key == "test-key-12345"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_client):
        mock_client._request = AsyncMock(side_effect=ApiClientError("INVALID_CREDENTIALS", 401, "Invalid credentials"))

        with pytest.raises(ApiClientError) as exc_info:
            await login(mock_client, "wrong", "wrong")

        assert exc_info.value.error_code == "INVALID_CREDENTIALS"
```

## Test de base de datos local (SQLite)

```python
import aiosqlite
import pytest

from src.db import init_db, store_key, get_active_key


class TestDatabase:
    @pytest.mark.asyncio
    async def test_store_and_retrieve_key(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        async with aiosqlite.connect(db_path) as db:
            await init_db(db)
            await store_key(db, "key-1", "Test Key", "abc123", "user", "http://localhost:8000", role="admin", user_id="user-1")

            key = await get_active_key(db, "http://localhost:8000")
            assert key is not None
            assert key["key"] == "abc123"
            assert key["key_type"] == "user"
```

## Test de pantallas Textual (pilot)

```python
from textual.app import App
from textual.widgets import Input, Button


class TestLoginScreen:
    @pytest.mark.asyncio
    async def test_login_screen_shows_inputs(self, app_instance):
        async with app_instance.run_test() as pilot:
            await pilot.push_screen(LoginScreen())
            assert app_instance.query_one("#username-input", Input) is not None
            assert app_instance.query_one("#password-input", Input) is not None
            assert app_instance.query_one("#login-btn", Button) is not None

    @pytest.mark.asyncio
    async def test_login_flow_success(self, app_instance):
        mock_client = app_instance.client
        mock_client._request = AsyncMock(return_value={
            "user": {"id": "u1", "username": "test", "role": "admin"},
            "api_key": "key-123",
        })

        async with app_instance.run_test() as pilot:
            await pilot.push_screen(LoginScreen())
            await pilot.press("t", "e", "s", "t")  # type username
            await pilot.press("tab")
            await pilot.press("p", "a", "s", "s")  # type password
            await pilot.click("#login-btn")

            # Verify navigation happened
            assert isinstance(app_instance.screen, DashboardScreen)
```

## pytest-asyncio

- Todos los tests async llevan `@pytest.mark.asyncio`
- Fixtures async usan `@pytest_asyncio.fixture`
- `event_loop` con `scope="session"` para compartir entre tests
- DB de test usa SQLite en `:memory:` o `tmp_path` (no PostgreSQL)

## Cobertura

- Minimo 80% de cobertura
- Testear: happy path, error paths, edge cases
- Priorizar tests de API client y DB local sobre tests de UI
- Tests de UI con `app.run_test()` de Textual (pilot)
- Comando: `pytest tests/ -v --cov=src --cov-report=term-missing`

## DB de test vs Mocks

- Usar SQLite `:memory:` o `tmp_path` para tests de DB local
- NO hacer mock de aiosqlite — usar DB real en memoria
- Mock solo para el servidor HTTP remoto (httpx transport mock)
- La base de datos de test es volatil, se recrea por test

## Snippet: Test de error de conexion

```python
class TestApiClientErrors:
    @pytest.mark.asyncio
    async def test_connection_error(self):
        client = OnyxLogClient(base_url="http://nonexistent-host:9999")
        client._client = httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(), base_url="http://nonexistent-host:9999")
        try:
            await client._request("GET", "/health")
            pytest.fail("Should have raised ApiClientError")
        except ApiClientError as e:
            assert e.error_code == "CONNECTION_ERROR"
        finally:
            await client.close()
```