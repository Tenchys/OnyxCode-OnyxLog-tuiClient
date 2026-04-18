# AGENTS.md — OnyxLog TUI Client

Cliente TUI para OnyxLog construido con Python, Textual y Rich.

## Stack

- **Lenguaje**: Python 3.11+
- **TUI**: Textual (framework) + Rich (formateo/tablas)
- **HTTP**: httpx (async)
- **DB local**: SQLite via aiosqlite
- **Validacion**: Pydantic v2
- **Testing**: pytest + pytest-asyncio

## Arquitectura

```
src/
├── app.py              # Textual App principal y ciclo de vida
├── config.py           # Configuracion ONYXLOG_URL, DB path, etc.
├── db.py               # SQLite local (aiosqlite) para API keys
├── api/
│   ├── client.py       # httpx.AsyncClient base, auth, headers, errores
│   ├── auth.py         # POST /auth/register, /auth/login
│   ├── applications.py # CRUD /applications, /applications/{id}/keys
│   └── logs.py         # GET/POST /logs, /logs/query, streaming SSE
├── models/
│   └── schemas.py      # Pydantic models (User, App, Log, ApiKey)
└── screens/
    ├── login.py         # Registro + Login
    ├── dashboard.py     # Dashboard principal con navegacion
    ├── applications.py # Listar/crear/editar aplicaciones
    ├── logs.py          # Visor de logs con filtros
    └── settings.py      # Configuracion del servidor
```

## Reglas Obligatorias

1. **Todos los endpoints van bajo `/api/v1`** y usan header `X-API-Key`.
2. **Las API keys se almacenan SOLO en SQLite local**, nunca en archivos de texto plano.
3. **Usar httpx.AsyncClient** para todas las llamadas HTTP (no requests).
4. **Pantallas Textual** heredan de `Screen` y se instalan via `app.push_screen()`.
5. **No usar `time.sleep()`** ni llamadas bloqueantes en el hilo principal — usar `asyncio.sleep()` o `app.run_worker()`.
6. **Formato commits**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`).
7. **Runs de test**: `pytest tests/ -v`
8. **Lint**: `ruff check src/ tests/` y `ruff format src/ tests/`

## Configuracion del Servidor

Se configura en este orden de prioridad:
1. Flag CLI: `onyxlog-tui --url http://...`
2. Variable de entorno: `ONYXLOG_URL`
3. Archivo: `~/.onyxlog/config.toml` con clave `server.url`

Default: `http://localhost:8000`

El archivo config se crea automaticamente en el primer uso.

## Base de Datos Local (SQLite)

Tabla unica para API keys:

```sql
CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    key TEXT NOT NULL,
    key_type TEXT NOT NULL,   -- 'user' | 'application'
    role TEXT,                 -- 'admin' | 'viewer' (solo user)
    user_id TEXT,
    app_id TEXT,
    server_url TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER DEFAULT 1
);
```

## API de OnyxLog — Referencia Rapida

Ver **`docs/api-reference.md`** para detalles completos con ejemplos curl.

| Categoria | Endpoint | Metodo | Auth |
|-----------|----------|--------|------|
| Auth | `/api/v1/auth/register` | POST | Ninguna |
| Auth | `/api/v1/auth/login` | POST | Ninguna |
| Auth | `/api/v1/auth/viewers` | POST | User API Key |
| Auth | `/api/v1/auth/keys` | GET/POST | User API Key |
| Auth | `/api/v1/auth/keys/{id}` | DELETE | User API Key |
| Apps | `/api/v1/applications` | GET/POST | User API Key |
| Apps | `/api/v1/applications/{id}` | GET/PUT/DELETE | User API Key |
| Apps | `/api/v1/applications/{id}/keys` | GET/POST | User API Key |
| Logs | `/api/v1/logs` | GET/POST | App API Key |
| Logs | `/api/v1/logs/query` | POST | App API Key |
| Logs | `/api/v1/logs/export` | POST | App API Key |
| Logs | `/api/v1/logs/stream` | GET (SSE) | User API Key |
| Logs | `/api/v1/logs/{id}` | GET | App API Key |
| Stats | `/api/v1/stats/summary` | GET | App API Key |
| Stats | `/api/v1/stats/overview` | GET | User/App API Key |
| Stats | `/api/v1/stats/custom` | POST | App API Key |
| Metrics | `/api/v1/metrics/summary` | GET | User API Key |
| Metrics | `/api/v1/metrics/trends` | GET | User API Key |
| Alerts | `/api/v1/alerts` | GET/POST | User API Key |
| Alerts | `/api/v1/alerts/{id}` | GET/PUT/DELETE | User API Key |
| Alerts | `/api/v1/alerts/active` | GET | User API Key |
| Health | `/health` | GET | Ninguna |

### Codigos de Error Estandar

| HTTP | Codigo | Significado |
|------|--------|-------------|
| 401 | INVALID_CREDENTIALS | Login fallido |
| 403 | INVALID_API_KEY | API key invalida/revocada |
| 403 | ADMIN_REQUIRED | Requiere rol admin |
| 404 | *_NOT_FOUND | Recurso no encontrado |
| 409 | DUPLICATE_ENTRY | Username/email/app_id duplicado |
| 422 | VALIDATION_ERROR | Datos invalidos |
| 429 | RATE_LIMITED | Rate limit excedido |

## Navegacion de Contexto

| Para saber... | Leer |
|---------------|------|
| API completa con ejemplos curl | `docs/api-reference.md` |
| Esquemas Pydantic | `src/models/schemas.py` |
| Configuracion del servidor | `src/config.py` |
| Esquema de base de datos | `src/db.py` |
| Patrones Textual UI | `src/screens/` |

## Flujo de Autenticacion

1. **Registro**: POST `/auth/register` → devuelve `user` + `api_key`
2. **Login**: POST `/auth/login` → devuelve `user` + `api_key`
3. **Usar API key**: Header `X-API-Key: <key>` en todas las requests autenticadas
4. **Almacenar localmente**: Se guarda en SQLite con metadatos (server_url, key_type, role)

## Agentes Disponibles

### TUI Client (este proyecto)

| Agente | Descripcion |
|--------|-------------|
| `onyxlog-tui-builder` | Implementa features del TUI cargando skills, leyendo codigo existente y escribiendo codigo/tests |

### Backend OnyxLog (referencia)

| Agente | Descripcion |
|--------|-------------|
| `onyxlog-builder` | Implementa features del backend FastAPI (no usar directamente en TUI) |
| `onyxlog-committer` | Crea commits semanticos y PRs estructurados |
| `onyxlog-doc-writer` | Genera y actualiza documentacion |
| `onyxlog-phase-creator` | Planifica nuevas fases generando phase-N.md |
| `onyxlog-phase-writer` | Valida y escribe archivos de fase |
| `onyxlog-planner` | Crea planes de implementacion detallados |
| `onyxlog-reviewer` | Audita calidad de codigo del backend |

## Skills Disponibles

### TUI Client (este proyecto)

| Skill | Descripcion |
|-------|-------------|
| `onyxlog-tui-coding` | Directrices de codigo: estilo, capas, naming, manejo de errores para TUI |
| `onyxlog-tui-screens` | Patrones Textual: Screen, Compose, Workers, Bindings, Notificaciones, DataTable |
| `onyxlog-tui-api-client` | Patrones httpx: OnyxLogClient, auth headers, manejo de errores, SSE streaming |
| `onyxlog-tui-testing` | Testing: fixtures SQLite, httpx mock, pilot tests, cobertura >80% |
| `onyxlog-tui-commit` | Conventional Commits con scopes TUI, ruff lint/format, deteccion de secrets |
| `onyxlog-tui-review` | Revision en 8 categorias: arquitectura Textual, seguridad, API client, DB local, UI, testing, distribucion, convenciones |

### Backend OnyxLog (referencia, no usar directamente)

| Skill | Descripcion |
|-------|-------------|
| `onyxlog-api-patterns` | Patrones FastAPI (no aplica al TUI) |
| `onyxlog-coding` | Guias backend FastAPI/SQLAlchemy (usar `onyxlog-tui-coding` en su lugar) |
| `onyxlog-commit` | Commits backend (usar `onyxlog-tui-commit` en su lugar) |
| `onyxlog-data-layer` | Modelos SQLAlchemy/Alembic (no aplica, TUI usa aiosqlite) |
| `onyxlog-docs` | Metodologia de documentacion |
| `onyxlog-phase-creator` | Metodologia para crear nuevas fases |
| `onyxlog-phase-writer` | Metodologia para escribir archivos de fase |
| `onyxlog-planner` | Metodologia de planificacion |
| `onyxlog-resume` | Retomar implementacion leyendo estado |
| `onyxlog-review` | Revision backend (usar `onyxlog-tui-review` en su lugar) |
| `onyxlog-testing` | Testing backend PostgreSQL (usar `onyxlog-tui-testing` en su lugar) |

## Comandos Clave

```bash
pip install -e ".[dev]"              # Instalar con deps de dev
onyxlog-tui                          # Ejecutar el TUI
onyxlog-tui --url http://host:8000   # Con URL custom
pytest tests/ -v                      # Tests
ruff check src/ tests/               # Lint
ruff format src/ tests/              # Formatear
```