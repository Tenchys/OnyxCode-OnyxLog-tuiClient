---
name: onyxlog-data-layer
description: Patrones de datos para OnyxLog. Modelos SQLAlchemy, schemas Pydantic, JSONB, indices y migraciones Alembic.
metadata:
  audience: developers
  workflow: onyxlog
---

## Modelo base

Todos los modelos heredan de `src/models/base.py`:

```python
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
```

## Crear un modelo nuevo

```python
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.models.base import Base, BaseModel


class Log(BaseModel):
    __tablename__ = "logs"

    level = Column(Enum("DEBUG", "INFO", "WARN", "ERROR", name="log_level_enum"), nullable=False)
    message = Column(Text, nullable=False)
    app_id = Column(String(50), nullable=False, index=True)
    environment = Column(Enum("development", "testing", "production", name="environment_enum"))
    timestamp = Column(DateTime, nullable=False, index=True)
    custom_data = Column(JSONB)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)

    user = relationship("User", back_populates="logs")
    application = relationship("Application", back_populates="logs")

    __table_args__ = (
        Index("ix_logs_timestamp_level", "timestamp", "level"),
        Index("ix_logs_app_env", "app_id", "environment"),
        Index("ix_logs_custom_data", "custom_data", postgresql_using="gin"),
    )
```

Reglas para modelos:
- Heredar de `BaseModel` (ya incluye `id`, `created_at`, `updated_at`)
- `id` siempre UUID con `as_uuid=True`
- Foreign keys usan `UUID(as_uuid=True)`
- Relaciones con `back_populates` en ambos lados
- Indices compuestos y GIN en `__table_args__`

## Schemas Pydantic

Separacion estricta por proposito:

```python
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LogCreate(BaseModel):
    level: Literal["DEBUG", "INFO", "WARN", "ERROR"]
    message: str
    app_id: str
    environment: Literal["development", "testing", "production"]
    timestamp: datetime
    custom_data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Datos personalizados JSON, profundidad maxima 1"
    )


class LogRead(BaseModel):
    id: UUID
    level: str
    message: str
    app_id: str
    environment: Optional[str]
    timestamp: datetime
    custom_data: Optional[dict[str, Any]]
    user_id: UUID
    application_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LogQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    levels: Optional[list[Literal["DEBUG", "INFO", "WARN", "ERROR"]]] = None
    app_ids: Optional[list[str]] = None
    environments: Optional[list[Literal["development", "testing", "production"]]] = None
    message_contains: Optional[str] = None
    custom_data_query: Optional[dict[str, Any]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)
    sort_by: Literal["timestamp", "level", "created_at"] = "timestamp"
    sort_order: Literal["asc", "desc"] = "desc"
```

Reglas para schemas:
- `Create` para datos de entrada (sin `id`, sin timestamps)
- `Read` para datos de salida (con `from_attributes=True`)
- `Update` con campos opcionales para PATCH
- `Query` para parametros de busqueda/filtrado
- Siempre `from __future__ import annotations` para usar tipos modernos

## Validacion de custom_data

Validador que asegura profundidad 1:

```python
from __future__ import annotations

from typing import Any


def validate_custom_data_depth(data: dict[str, Any] | None, max_depth: int = 1) -> dict[str, Any] | None:
    if data is None:
        return data

    for key, value in data.items():
        if isinstance(value, dict):
            raise ValueError(f"Nested objects not allowed in custom_data (key: {key})")
        if isinstance(value, list):
            for item in value:
                if isinstance(item, (dict, list)):
                    raise ValueError(f"Nested structures not allowed in custom_data arrays (key: {key})")

    return data
```

Uso en schema:
```python
from pydantic import field_validator

class LogCreate(BaseModel):
    custom_data: Optional[dict[str, Any]] = None

    @field_validator("custom_data")
    @classmethod
    def validate_custom_data(cls, v):
        return validate_custom_data_depth(v)
```

## Indices

Tipos de indices segun uso:

| Tipo             | Uso                                    | Ejemplo                          |
|------------------|----------------------------------------|----------------------------------|
| Simple           | Busqueda por campo unico               | `app_id`, `timestamp`           |
| Compuesto        | Queries que filtran por multiples campos | `(timestamp, level)`           |
| GIN              | Busqueda dentro de JSONB               | `custom_data` con `postgresql_using="gin"` |

Siempre definir indices en `__table_args__`, no con `index=True` en Column para indices compuestos.

## Migraciones Alembic

```bash
# Crear migracion
alembic revision --autogenerate -m "add_logs_table"

# Aplicar
alembic upgrade head

# Revertir
alembic downgrade -1
```

Reglas:
- Mensaje descriptivo en ingles o espanol consistente
- Siempre revisar el autogenerate antes de aplicar
- No modificar migraciones ya aplicadas
