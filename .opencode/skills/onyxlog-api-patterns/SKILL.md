---
name: onyxlog-api-patterns
description: Patrones de implementacion FastAPI para OnyxLog. Routes, dependencias, middleware, response models y versionado de API.
metadata:
  audience: developers
  workflow: onyxlog
---

## Crear un route nuevo

1. Crear archivo en `src/api/routes/<recurso_plural>.py`
2. Definir router con `APIRouter(prefix="/<recurso_plural>", tags=["<recurso_plural>"])`
3. Registrar en `src/api/routes/__init__.py` importando el router
4. Incluir en `main.py` con `app.include_router(routes.<recurso>_router, prefix="/api/v1")`

## Dependencias

Todas las dependencias se definen en `src/api/dependencies.py`.

**Database session**:
```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.database import async_session_factory


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
```

**Usuario autenticado** (valida API Key):
```python
from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


async def get_current_user(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.api_key == x_api_key, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=403,
            detail={"message": "Invalid or revoked API key", "error_code": "INVALID_API_KEY"}
        )
    return user
```

**Parametros de paginacion**:
```python
from dataclasses import dataclass


@dataclass
class PaginationParams:
    page: int = 1
    page_size: int = 50


def get_pagination_params(page: int = 1, page_size: int = 50) -> PaginationParams:
    page = max(1, page)
    page_size = max(1, min(1000, page_size))
    return PaginationParams(page=page, page_size=page_size)
```

## Autenticacion

- API Key enviada en header `X-API-Key`
- Middleware en `src/api/middleware.py` valida la key antes de llegar a las rutas
- Rutas publicas: `/api/v1/auth/register`, `/api/v1/auth/login`
- Rutas protegidas: requieren `Depends(get_current_user)`
- El usuario autenticado queda disponible como `request.state.user`

## Response models

**Respuesta paginada generica**:
```python
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)
```

**Respuesta de error**:
```python
class ErrorResponse(BaseModel):
    message: str
    error_code: str
```

## Versionado de API

- Todas las rutas bajo prefijo `/api/v1`
- Router principal en `main.py`:
```python
from fastapi import FastAPI

from src.api.routes import auth_router, logs_router, applications_router, stats_router

app = FastAPI(title="OnyxLog", version="1.0.0")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(logs_router, prefix="/api/v1")
app.include_router(applications_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")
```

## Snippet: Route CRUD completo

```python
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db, get_pagination_params, PaginationParams
from src.models.user import User
from src.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate
from src.services.application_service import (
    create_application,
    delete_application,
    get_application,
    list_applications,
    update_application,
)

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationRead, status_code=201)
async def create(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await create_application(db, user.id, data)


@router.get("", response_model=PaginatedResponse[ApplicationRead])
async def list_all(
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await list_applications(db, user.id, pagination)


@router.get("/{app_id}", response_model=ApplicationRead)
async def get(
    app_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await get_application(db, user.id, app_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail={"message": "Application not found", "error_code": "NOT_FOUND"}
        )
    return result


@router.put("/{app_id}", response_model=ApplicationRead)
async def update(
    app_id: UUID,
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await update_application(db, user.id, app_id, data)


@router.delete("/{app_id}", status_code=204)
async def delete(
    app_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await delete_application(db, user.id, app_id)
```
