---
name: onyxlog-tui-review
description: Criterios de revision de codigo para OnyxLog TUI Client. Evalua arquitectura Textual, seguridad, API client, DB local, testing, convenciones y readiness para release. Genera informe con veredicto.
metadata:
  audience: reviewers
  workflow: onyxlog-tui
---

## Categorias de Revision

Se evaluan 8 categorias. Cada hallazgo se clasifica con una severidad:

| Severidad | Significado | Accion |
|-----------|-------------|--------|
| **BLOCKER** | Impide release | Debe corregirse antes de cualquier merge |
| **CRITICAL** | Riesgo alto | Debe corregirse antes de release |
| **WARNING** | Problema potencial | Recomendado corregir, no bloquea |
| **INFO** | Observacion menor | Sugerencia de mejora |

---

### 1. Arquitectura Textual

Verifica la estructura de capas y la separacion de responsabilidades.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| ARC-01 | BLOCKER | Las pantallas NO contienen logica HTTP directa, delegan al cliente API |
| ARC-02 | CRITICAL | El cliente API (`OnyxLogClient`) NO contiene logica de UI |
| ARC-03 | CRITICAL | Los modelos Pydantic NO dependen de pantallas ni del cliente API |
| ARC-04 | CRITICAL | `db.py` NO depende de pantallas ni del cliente API |
| ARC-05 | CRITICAL | `config.py` NO depende de ningun otro modulo interno |
| ARC-06 | WARNING | Cada pantalla esta en su propio archivo bajo `src/screens/` |
| ARC-07 | WARNING | No hay imports circulares entre modulos |
| ARC-08 | INFO | Archivos no exceden ~300 lineas (considerar refactor) |
| ARC-09 | WARNING | `.opencode/agents/` y `.opencode/skills/` no contienen referencias backend heredadas |

Patrones de deteccion:
- Buscar `httpx.` o `await client._request` directamente en archivos de `screens/`
- Buscar `from src.screens` en archivos de `api/` o `models/`
- Buscar `from src.api` en archivos de `models/` o `db.py`
- Buscar logica de negocio (parseo, calculos complejos) directamente en compose() o action handlers
- Buscar referencias backend heredadas (`FastAPI`, `SQLAlchemy`, `PostgreSQL`, `Alembic`, `routes/`, `services/`) en `.opencode/agents/` y `.opencode/skills/`

Flujo correcto:

```
Screen → OnyxLogClient.endpoint() → httpx request → OnyxLog server → response → Screen.update_ui()
```

---

### 2. Seguridad

Verifica vulnerabilidades que comprometan al usuario o sus credenciales.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| SEC-01 | BLOCKER | API keys nunca se almacenan en texto plano ni en archivos de config |
| SEC-02 | BLOCKER | No hay secrets hardcodeados (API keys, passwords, tokens) |
| SEC-03 | CRITICAL | API keys nunca se logean ni se exponen en pantalla completa |
| SEC-04 | CRITICAL | Passwords nunca se almacenan localmente |
| SEC-05 | CRITICAL | Conexiones HTTP usan timeout configurado (no infinito) |
| SEC-06 | WARNING | API keys se almacenan solo en SQLite con permisos restrictivos |
| SEC-07 | WARNING | Errores de `INVALID_API_KEY` limpian la sesion y redirigen a login |
| SEC-08 | WARNING | No se exponen stack traces internos al usuario |
| SEC-09 | INFO | Config file con permisos 600 o 700 |

Patrones de deteccion:
- Buscar strings que parezcan API keys: `sk_`, `key_`, `secret`, `password` asignados como literales
- Buscar `print(api_key)` o `logger.*(api_key)`
- Buscar almacenamiento en archivos json/yaml/toml (debe ser SQLite)
- Buscar `httpx.AsyncClient()` sin `timeout`

---

### 3. API Client

Verifica el cliente HTTP y manejo de errores.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| API-01 | CRITICAL | Toda llamada HTTP usa `httpx.AsyncClient`, nunca `requests` |
| API-02 | CRITICAL | Todas las rutas usan prefijo `/api/v1` |
| API-03 | CRITICAL | Toda request autenticada incluye header `X-API-Key` |
| API-04 | CRITICAL | Errores HTTP se mapean a `ApiClientError` con `error_code` y `status_code` |
| API-05 | CRITICAL | Connection errors y timeouts se manejan con `ApiClientError` especifico |
| API-06 | WARNING | Metodos del cliente API tienen type hints completos |
| API-07 | WARNING | Cliente API se inicializa en `app.py` y se comparte via `self.app.client` |
| API-08 | INFO | SSL verification no se deshabilita en produccion |

Patrones de deteccion:
- Buscar `import requests` (prohibido)
- Buscar `requests.get`, `requests.post` (prohibido)
- Buscar `httpx.get()` sin usar `OnyxLogClient._request()`
- Buscar endpoints sin `/api/v1` prefijo
- Buscar requests sin header `X-API-Key` en endpoints protegidos

Codigos de error a verificar:

| HTTP | error_code |
|------|------------|
| 401 | INVALID_CREDENTIALS |
| 403 | INVALID_API_KEY / ADMIN_REQUIRED |
| 404 | *_NOT_FOUND |
| 409 | DUPLICATE_ENTRY |
| 422 | VALIDATION_ERROR |
| 429 | RATE_LIMITED |

---

### 4. Base de Datos Local (SQLite)

Verifica el almacenamiento local de API keys.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| DB-01 | CRITICAL | Tabla `api_keys` con todos los campos requeridos (id, name, key, key_type, role, user_id, app_id, server_url, created_at, is_active) |
| DB-02 | CRITICAL | Schema se crea via `init_db()` con `CREATE TABLE IF NOT EXISTS` |
| DB-03 | CRITICAL | Operaciones DB usan `aiosqlite`, nunca `sqlite3` sincrono |
| DB-04 | CRITICAL | DB path usa `~/.onyxlog/keys.db` con creacion automatica del directorio |
| DB-05 | WARNING | Queries usan parametros (?) no f-strings (SQL injection prevention) |
| DB-06 | WARNING | Funciones DB tienen type hints completos |
| DB-07 | INFO | Se usa `PRAGMA journal_mode=WAL` para mejor rendimiento concurrente |

Patrones de deteccion:
- Buscar `import sqlite3` (prohibido, debe ser aiosqlite)
- Buscar `f"SELECT` o `f"INSERT` en queries (SQL injection)
- Buscar `sqlite3.connect` (prohibido)
- Verificar que `init_db()` crea la tabla completa

---

### 5. Pantallas y UI (Textual)

Verifica patrones de pantallas y widgets.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| TUI-01 | CRITICAL | Pantallas heredan de `Screen` (o `ModalScreen` para dialogos) |
| TUI-02 | CRITICAL | No se usa `time.sleep()` ni llamadas bloqueantes — usar `asyncio.sleep()` o `run_worker()` |
| TUI-03 | CRITICAL | Datos se cargan en workers, nunca en `compose()` directamente |
| TUI-04 | CRITICAL | Errores de API se muestran via `self.notify()` con severidad |
| TUI-05 | WARNING | Pantallas definen `BINDINGS` para atajos de teclado |
| TUI-06 | WARNING | `compose()` solo contiene widgets declarativos, no logica |
| TUI-07 | WARNING | `on_mount()` dispara workers para carga inicial |
| TUI-08 | WARNING | Navegacion usa `app.push_screen()` y `app.pop_screen()` |
| TUI-09 | INFO | Widgets usan `id` para `query_one()` en vez de indexar |
| TUI-10 | INFO | DataTable con `cursor_type="row"` para seleccion |

Patrones de deteccion:
- Buscar `time.sleep(` — BLOCKER
- Buscar `requests.` — BLOCKER (debe ser httpx async)
- Buscar `await` dentro de `compose()` — CRITICAL
- Buscar widgets sin `id` en pantallas complejas
- Buscar `Header()` o `Footer()` sin `compose()` completo

---

### 6. Testing

Verifica calidad y cobertura de tests.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| TST-01 | CRITICAL | Cobertura >= 80% |
| TST-02 | CRITICAL | Tests de API client priorizados sobre tests de UI |
| TST-03 | CRITICAL | DB de test usa SQLite `:memory:` o `tmp_path`, no PostgreSQL |
| TST-04 | WARNING | Tests siguen patron AAA (Arrange, Act, Assert) |
| TST-05 | WARNING | Tests async usan `@pytest.mark.asyncio` |
| TST-06 | WARNING | Fixtures async usan `@pytest_asyncio.fixture` |
| TST-07 | WARNING | NO hacer mock de aiosqlite (usar DB real en memoria) |
| TST-08 | WARNING | Mock solo para el servidor HTTP remoto (httpx transport mock) |
| TST-09 | WARNING | Nombres descriptivos: `test_<accion>_<escenario>` |
| TST-10 | INFO | Archivo de test por modulo: `test_auth.py` para `api/auth.py` |
| TST-11 | INFO | Clase `TestXxx` por entidad |

Patrones de deteccion:
- Buscar tests sin `assert`
- Buscar `Mock` o `MagicMock` para aiosqlite (no se debe mockear)
- Buscar tests async sin `@pytest.mark.asyncio`
- Buscar fixtures de PostgreSQL (no aplica en TUI)
- Verificar que `conftest.py` tiene las fixtures base (mock_client, db_connection, app_instance)

---

### 7. Distribucion y Configuracion

Verifica si el TUI esta listo para distribuirse.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| DIST-01 | BLOCKER | No hay archivos `.env` commiteados (solo `.env.example`) |
| DIST-02 | CRITICAL | `pyproject.toml` con entry_points configurado (`onyxlog-tui`) |
| DIST-03 | CRITICAL | Variables de entorno con prefijo `ONYXLOG_` |
| DIST-04 | WARNING | `ruff` configurado en `pyproject.toml` |
| DIST-05 | WARNING | Dependencias explicitas en `pyproject.toml` con versiones |
| DIST-06 | INFO | Config file se crea automaticamente en primer uso |
| DIST-07 | INFO | CLI args con `--url` para URL del servidor |

Patrones de deteccion:
- Buscar `.env` en `git status` o sin `.env` en `.gitignore`
- Verificar `[project.scripts]` en `pyproject.toml`
- Buscar `print(` en codigo de produccion (no tests)
- Verificar existencia de `[tool.ruff]` en `pyproject.toml`

---

### 8. Convenciones

Verifica estilo Python y convenciones del proyecto.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| CON-01 | WARNING | `from __future__ import annotations` en todos los archivos |
| CON-02 | WARNING | Type hints en todas las firmas de funciones y metodos |
| CON-03 | WARNING | Sin comentarios en codigo salvo docstrings publicos |
| CON-04 | INFO | Formato con `ruff format` |
| CON-05 | INFO | Imports ordenados con `ruff` |
| CON-06 | INFO | Naming correcto por capa (ver AGENTS.md) |

Tabla de naming TUI:

| Capa | Archivo | Clase/Funcion |
|------|---------|---------------|
| screens/ | `login.py` | `LoginScreen(App)` |
| api/ | `auth.py` | `register()`, `login()` |
| api/ | `client.py` | `OnyxLogClient` (clase) |
| models/ | `schemas.py` | `User`, `App`, `Log`, `ApiKey` |
| db.py | - | `init_db()`, `store_key()`, `get_active_key()` |
| config.py | - | `Settings(BaseSettings)` |

Patrones de deteccion:
- Buscar archivos `.py` sin `from __future__ import annotations`
- Buscar funciones sin type hints: `def func(` sin `: `
- Buscar comentarios con `#` que no sean TODOs legítimos

---

## Formato del Informe

El informe SIEMPRE sigue esta estructura:

```markdown
# Informe de Revision — OnyxLog TUI Client

## Veredicto: [DEPLOY_BLOCKED | DEPLOY_CONDITIONAL | DEPLOY_APPROVED]

## Resumen
- Blockers: X
- Criticals: X
- Warnings: X
- Infos: X

## Archivos Revisados
- `src/screens/login.py`
- `src/api/auth.py`
- ...

---

### BLOCKERS

| # | Regla | Archivo | Linea | Descripcion |
|---|-------|---------|--------|-------------|
| 1 | SEC-01 | src/db.py | 15 | API key almacenada en archivo JSON |

### CRITICALS

| # | Regla | Archivo | Linea | Descripcion | Sugerencia |
|---|-------|---------|--------|-------------|------------|
| 1 | ARC-01 | src/screens/login.py | 42 | Logica HTTP directa en Screen | Mover a api/auth.py |

### WARNINGS

| # | Regla | Archivo | Descripcion |
|---|-------|---------|-------------|
| 1 | CON-01 | src/screens/dashboard.py | Falta `from __future__ import annotations` |

### INFOS

| # | Regla | Archivo | Descripcion |
|---|-------|---------|-------------|
| 1 | CON-04 | src/api/client.py | Linea > 88 caracteres |

---

## Checklist de Release

- [x] API keys almacenadas solo en SQLite
- [x] Sin secrets en codigo fuente
- [x] httpx.AsyncClient para todas las llamadas HTTP
- [ ] Cobertura >= 80%
- [x] Sin time.sleep ni llamadas bloqueantes
- [x] Errores de API con ApiClientError
- [x] ruff check y ruff format pasan
- [ ] pyproject.toml con entry_points
- [x] config.toml auto-creado en primer uso
```

### Reglas del Veredicto

| Condicion | Veredicto |
|-----------|-----------|
| Al menos 1 BLOCKER | DEPLOY_BLOCKED |
| 0 BLOCKERS pero al menos 1 CRITICAL | DEPLOY_CONDITIONAL |
| 0 BLOCKERS y 0 CRITICALS | DEPLOY_APPROVED |

---

## Modos de Revision

### Modo Diff (`--scope diff`)
- Ejecutar `git diff --name-only` para obtener archivos modificados
- Leer solo los archivos cambiados
- Mas rapido, ideal para revision de PRs

### Modo Full (`--scope full`)
- Leer todo el directorio `src/` recursivamente
- Leer `.opencode/agents/` y `.opencode/skills/`
- Auditar todos los archivos del proyecto
- Mas lento pero exhaustivo

### Flujo de Revision

1. Cargar skills `onyxlog-tui-coding`, `onyxlog-tui-screens`, `onyxlog-tui-api-client`, `onyxlog-tui-testing`
2. Determinar scope (diff o full)
3. Si diff: ejecutar `git diff --name-only`, leer archivos cambiados
4. Si full: leer todo `src/` recursivamente y `.opencode/agents/`, `.opencode/skills/`
5. Para cada archivo, evaluar contra las 8 categorias
6. Clasificar cada hallazgo por severidad
7. Compilar informe con veredicto
8. Retornar informe completo

### Prioridad de Revision por Capa

1. `api/` — Cliente HTTP, mayor riesgo de seguridad
2. `db.py` — Almacenamiento de API keys, seguridad
3. `screens/` — UI, experiencia de usuario
4. `models/` — Schemas, validacion
5. `config.py` — Configuracion, valores por defecto
6. `app.py` — Punto de entrada, ciclo de vida
