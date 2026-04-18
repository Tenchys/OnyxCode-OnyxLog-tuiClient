---
name: onyxlog-testing
description: Convenciones de testing para OnyxLog. Fixtures pytest, patron de tests, pytest-asyncio, cobertura y mocks.
metadata:
  audience: developers
  workflow: onyxlog
---

## Fixtures base (conftest.py)

```python
from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.database import Base
from src.main import app
from src.models.user import User
from src.models.application import Application
from src.core.security import generate_api_key


TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/onyxlog_test"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncSession:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncClient:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    api_key = generate_api_key()
    user = User(
        username=f"test_{uuid4().hex[:8]}",
        email=f"test_{uuid4().hex[:8]}@test.com",
        api_key=api_key,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict[str, str]:
    return {"X-API-Key": test_user.api_key}


@pytest_asyncio.fixture
async def test_application(db_session: AsyncSession, test_user: User) -> Application:
    app = Application(
        name=f"TestApp_{uuid4().hex[:8]}",
        app_id=f"app-{uuid4().hex[:8]}",
        environment="development",
        owner_id=test_user.id,
        is_active=True,
    )
    db_session.add(app)
    await db_session.commit()
    await db_session.refresh(app)
    return app
```

## Patron de test

- Un archivo por modulo: `test_logs.py` para `routes/logs.py`
- Clase `TestXxx` por entidad
- Metodos descriptivos: `test_create_log_success`, `test_create_log_missing_api_key`
- Estructura AAA: Arrange, Act, Assert

```python
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestLogCreation:
    async def test_create_log_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        test_application,
    ):
        payload = {
            "level": "ERROR",
            "message": "Database connection timeout",
            "app_id": test_application.app_id,
            "environment": "development",
            "timestamp": "2024-01-15T10:30:00Z",
            "custom_data": {"user_id": "123", "retry_count": 3},
        }
        response = await async_client.post("/api/v1/logs", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["level"] == "ERROR"
        assert data["message"] == "Database connection timeout"
        assert data["custom_data"]["user_id"] == "123"

    async def test_create_log_missing_api_key(self, async_client: AsyncClient, test_application):
        payload = {
            "level": "INFO",
            "message": "Test",
            "app_id": test_application.app_id,
            "environment": "development",
            "timestamp": "2024-01-15T10:30:00Z",
        }
        response = await async_client.post("/api/v1/logs", json=payload)

        assert response.status_code == 401

    async def test_create_log_nested_custom_data_rejected(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        test_application,
    ):
        payload = {
            "level": "INFO",
            "message": "Test",
            "app_id": test_application.app_id,
            "environment": "development",
            "timestamp": "2024-01-15T10:30:00Z",
            "custom_data": {"nested": {"key": "value"}},
        }
        response = await async_client.post("/api/v1/logs", json=payload, headers=auth_headers)

        assert response.status_code == 422
```

## pytest-asyncio

- Todos los tests async llevan `@pytest.mark.asyncio`
- Fixtures async usan `@pytest_asyncio.fixture`
- `event_loop` con `scope="session"` para compartir entre tests
- DB session con rollback por test para aislamiento

## Cobertura

- Minimo 80% de cobertura
- Testear: happy path, error paths, edge cases
- Priorizar tests de endpoints (integration) sobre tests unitarios de servicios
- Comando: `pytest tests/ -v --cov=src --cov-report=term-missing`

## DB de test vs Mocks

- Usar DB de test real (PostgreSQL) para tests de integracion
- NO hacer mock del ORM/SQLAlchemy
- Mock solo para servicios externos (Redis, email, etc.)
- DB de test con nombre `onyxlog_test`, separada de desarrollo

## Snippet: Test de query avanzada

```python
@pytest.mark.asyncio
class TestLogQueries:
    async def test_query_by_level_and_app(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        test_application,
    ):
        params = {
            "levels": ["ERROR", "WARN"],
            "app_ids": [test_application.app_id],
            "page": 1,
            "page_size": 50,
        }
        response = await async_client.get("/api/v1/logs", params=params, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
```
