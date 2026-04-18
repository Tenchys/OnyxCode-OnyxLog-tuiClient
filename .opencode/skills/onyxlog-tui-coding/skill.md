---
name: onyxlog-tui-coding
description: Directrices generales de codigo para el OnyxLog TUI Client (Python + Textual + Rich + httpx + aiosqlite). Estilo, estructura de capas, convenciones de naming y manejo de errores.
metadata:
  audience: developers
  workflow: onyxlog-tui
---

## Estilo Python

- Usar `from __future__ import annotations` en todos los archivos
- Type hints obligatorios en firmas de funciones y metodos
- Sin comentarios en el codigo salvo docstrings en funciones publicas del TUI
- Formatear con `ruff format` (usar defaults de ruff)
- Lint con `ruff check src/ tests/`
- Line length maximo: 88 caracteres

## Estructura de capas

```
src/
  app.py              # Textual App principal, ciclo de vida, composicion raiz
  config.py           # Configuracion (pydantic-settings, ONYXLOG_URL, DB path)
  db.py               # SQLite local (aiosqlite) para API keys
  api/
    client.py         # httpx.AsyncClient base, auth headers, manejo de errores
    auth.py           # POST /auth/register, /auth/login
    applications.py   # CRUD /applications, /applications/{id}/keys
    logs.py           # GET/POST /logs, /logs/query, streaming SSE
  models/
    schemas.py        # Pydantic models (User, App, Log, ApiKey)
  screens/
    login.py          # Registro + Login
    dashboard.py      # Dashboard principal con navegacion
    applications.py   # Listar/crear/editar aplicaciones
    logs.py           # Visor de logs con filtros
    settings.py       # Configuracion del servidor
```

Flujo de datos: **Screen → API Client → OnyxLog Server → Response → Screen**

- Las pantallas NO contienen logica HTTP directa, delegan al cliente API
- El cliente API (`OnyxLogClient`) NO contiene logica de UI
- Los modelos Pydantic NO dependen de pantallas ni del cliente API
- `db.py` NO depende de pantallas ni del cliente API
- `config.py` NO depende de ningun otro modulo interno

## Convenciones de naming

| Capa       | Archivo           | Clase/Funcion                     |
|------------|-------------------|-----------------------------------|
| screens/   | `login.py`        | `LoginScreen(App)`                |
| screens/   | `dashboard.py`   | `DashboardScreen(App)`            |
| screens/   | `logs.py`         | `LogsScreen(App)`                 |
| api/       | `client.py`       | `OnyxLogClient` (clase)           |
| api/       | `auth.py`         | `register()`, `login()`           |
| models/    | `schemas.py`      | `User`, `App`, `Log`, `ApiKey`    |
| db.py      | -                 | `init_db()`, `store_key()`, `get_active_key()` |
| config.py  | -                 | `Settings(BaseSettings)`           |

## Manejo de errores

Errores de API se mapean a `ApiClientError`:

```python
from __future__ import annotations

class ApiClientError(Exception):
    def __init__(self, error_code: str, status_code: int, message: str):
        self.error_code = error_code
        self.status_code = status_code
        self.message = message
        super().__init__(f"[{status_code}] {error_code}: {message}")
```

Uso en pantallas:

```python
try:
    result = await client.login(username, password)
except ApiClientError as e:
    self.notify(e.message, severity="error")
    return
```

Codigos de error del servidor OnyxLog:

| HTTP | error_code      | Significado                     |
|------|-----------------|---------------------------------|
| 401  | INVALID_CREDENTIALS | Login fallido                |
| 403  | INVALID_API_KEY     | API key invalida/revocada    |
| 403  | ADMIN_REQUIRED      | Requiere rol admin           |
| 404  | *_NOT_FOUND         | Recurso no encontrado        |
| 409  | DUPLICATE_ENTRY     | Username/email/app_id duplicado |
| 422  | VALIDATION_ERROR    | Datos invalidos              |
| 429  | RATE_LIMITED        | Rate limit excedido          |

## Configuracion

- Usar `pydantic-settings` con `BaseSettings` en `src/config.py`
- Variables de entorno con prefijo `ONYXLOG_` (ej: `ONYXLOG_URL`)
- Archivo config: `~/.onyxlog/config.toml`
- Prioridad: CLI flag > env var > config file > default
- Default: `http://localhost:8000`

## Snippet: Pantalla minima

```python
from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static


class ExampleScreen(Screen):
    BINDINGS = [("q", "quit", "Quit"), ("r", "refresh", "Refresh")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Contenido aqui")
        yield Footer()

    async def on_mount(self) -> None:
        self.run_worker(self._load_data())

    async def _load_data(self) -> None:
        client = self.app.client
        try:
            data = await client.get_example()
            self.notify("Datos cargados", severity="information")
        except ApiClientError as e:
            self.notify(e.message, severity="error")

    def action_refresh(self) -> None:
        self.run_worker(self._load_data())
```

## Snippet: Modelo Pydantic

```python
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AppCreate(BaseModel):
    name: str
    app_id: str
    description: str | None = None
    environment: str


class AppRead(BaseModel):
    id: UUID
    name: str
    app_id: str
    description: str | None
    environment: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

## Snippet: Funcion de DB local

```python
from __future__ import annotations

import aiosqlite

DB_PATH = "~/.onyxlog/keys.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
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
        """)
        await db.commit()


async def store_key(
    id: str, name: str, key: str, key_type: str,
    server_url: str, role: str | None = None,
    user_id: str | None = None, app_id: str | None = None,
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO api_keys (id, name, key, key_type, role, user_id, app_id, server_url, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (id, name, key, key_type, role, user_id, app_id, server_url),
        )
        await db.commit()
```