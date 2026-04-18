---
name: onyxlog-coding
description: Directrices generales de codigo para OnyxLog (FastAPI + SQLAlchemy + PostgreSQL). Incluye estilo Python, estructura de capas, convenciones de naming y manejo de errores.
metadata:
  audience: developers
  workflow: onyxlog
---

## Estilo Python

- Usar `from __future__ import annotations` en todos los archivos
- Type hints obligatorios en firmas de funciones y metodos
- Sin comentarios en el codigo salvo docstrings en funciones publicas del API
- Formatear con `black` (line length 88) y ordenar imports con `isort`
- Type checking con `mypy --strict`

## Estructura de capas

```
src/
  api/          -> routes + dependencies + middleware
  core/         -> config + database + security
  models/       -> Modelos SQLAlchemy (tablas)
  schemas/      -> Schemas Pydantic (validacion)
  services/     -> Logica de negocio
  utils/        -> Helpers y validadores
```

Flujo de datos: **Route -> Dependency -> Service -> Model/Schema**

- Las rutas NO contienen logica de negocio, solo delegan al servicio
- Los servicios NO importan de `api/`, solo de `models/`, `schemas/`, `core/`
- Los modelos NO dependen de schemas ni servicios
- Los schemas NO dependen de modelos (usan `from_attributes=True`)

## Convenciones de naming

| Capa       | Archivo           | Clase/Funcion         |
|------------|-------------------|-----------------------|
| models/    | `user.py`         | `User` (singular)     |
| schemas/   | `log.py`          | `LogCreate`, `LogRead`, `LogQuery` |
| services/  | `log_service.py`  | `LogService` (clase) o funciones `create_log`, `query_logs` |
| routes/    | `logs.py`         | Router con prefijo `/logs` |
| utils/     | `validators.py`   | `validate_custom_data_depth` |

## Manejo de errores

Toda respuesta de error usa la misma estructura JSON:

```python
from fastapi import HTTPException

raise HTTPException(
    status_code=404,
    detail={
        "message": "Application not found",
        "error_code": "APP_NOT_FOUND"
    }
)
```

Codigos de error estandar:

| Codigo HTTP | error_code          | Uso                           |
|-------------|---------------------|-------------------------------|
| 400         | VALIDATION_ERROR    | Datos invalidos               |
| 401         | AUTH_REQUIRED       | API Key faltante              |
| 403         | INVALID_API_KEY     | API Key invalida o revocada   |
| 404         | NOT_FOUND           | Recurso no encontrado         |
| 409         | ALREADY_EXISTS      | Recurso duplicado             |
| 422         | INVALID_CUSTOM_DATA | custom_data no pasa validacion|
| 429         | RATE_LIMITED        | Rate limit excedido           |
| 500         | INTERNAL_ERROR      | Error inesperado              |

## custom_data

- Profundidad maxima: **1** (solo key-value en la raiz)
- Valores permitidos: string, number, boolean, null, array plano de primitivos
- NO se permiten objetos anidados como valores
- Tamano maximo por registro: 4 KB
- Validacion en el schema Pydantic, no en el modelo

## Configuracion

- Usar `pydantic-settings` con `BaseSettings` en `src/core/config.py`
- Variables de entorno con prefijo `ONYXLOG_` (ej: `ONYXLOG_DATABASE_URL`)
- Archivo `.env` para desarrollo, nunca commiteado
- Ejemplo en `.env.example`

## Snippet: Archivo minimo por capa

**Modelo** (`src/models/example.py`):
```python
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from src.models.base import Base


class Example(Base):
    __tablename__ = "examples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Schema** (`src/schemas/example.py`):
```python
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExampleCreate(BaseModel):
    name: str


class ExampleRead(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Servicio** (`src/services/example_service.py`):
```python
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.example import Example
from src.schemas.example import ExampleCreate


async def create_example(db: AsyncSession, data: ExampleCreate) -> Example:
    example = Example(name=data.name)
    db.add(example)
    await db.commit()
    await db.refresh(example)
    return example
```

**Ruta** (`src/api/routes/examples.py`):
```python
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.schemas.example import ExampleCreate, ExampleRead
from src.services.example_service import create_example

router = APIRouter(prefix="/examples", tags=["examples"])


@router.post("", response_model=ExampleRead, status_code=201)
async def create(
    data: ExampleCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_example(db, data)
```
