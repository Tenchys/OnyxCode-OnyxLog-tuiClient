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

## Comandos Clave

```bash
pip install -e ".[dev]"              # Instalar con deps de dev
onyxlog-tui                          # Ejecutar el TUI
onyxlog-tui --url http://host:8000   # Con URL custom
pytest tests/ -v                      # Tests
ruff check src/ tests/               # Lint
ruff format src/ tests/              # Formatear
```

## Navegacion de Contexto

| Para saber... | Leer |
|---------------|------|
| API endpoints y codigos de error | `IA/context/api-reference.md` |
| Schema de DB local | `IA/context/db-schema.md` |
| Flujo de autenticacion | `IA/context/auth-flow.md` |
| Configuracion del servidor | `IA/context/server-config.md` |
| API completa con ejemplos curl | `docs/api-reference.md` |
| Esquemas Pydantic | `src/models/schemas.py` |
| Configuracion del servidor (codigo) | `src/config.py` |
| Esquema de base de datos (codigo) | `src/db.py` |
| Patrones Textual UI | `src/screens/` |

## Reglas de Subagentes

1. **Cuando el usuario mencione un subagente con `@onyxlog-<nombre>` o diga "usa el subagente X", SIEMPRE delegar la tarea al subagente correspondiente via la herramienta `task` con `subagent_type`.**
2. **NUNCA cargar el skill manualmente y ejecutar los pasos uno mismo cuando se pidio usar un subagente.**
3. Usar siempre la tabla de mapeo siguiente para evitar confusiones entre el nombre visible, `subagent_type` y el skill asociado:

| Nombre visible | `subagent_type` | Skill asociado | Uso |
|---|---|---|---|
| `onyxlog-tui-builder` | `onyxlog-tui-builder` | `onyxlog-tui-builder` | Implementar features del TUI Client |
| `onyxlog-committer` | `onyxlog-committer` | `onyxlog-commit` | Crear commits semanticos y PRs |
| `onyxlog-doc-writer` | `onyxlog-doc-writer` | `onyxlog-docs` | Generar o actualizar documentacion |
| `onyxlog-phase-creator` | `onyxlog-phase-creator` | `onyxlog-phase-creator` | Crear contenido de fases |
| `onyxlog-phase-writer` | `onyxlog-phase-writer` | `onyxlog-phase-writer` | Escribir fases en el filesystem |
| `onyxlog-planner` | `onyxlog-planner` | `onyxlog-planner` | Planificar implementacion de fases |
| `onyxlog-reviewer` | `onyxlog-reviewer` | `onyxlog-review` | Revision de codigo |
| `onyxcode-fixer` | `onyxcode-fixer` | `onyxcode-fixer` | Revisar y corregir inconsistencias entre phase/tarea y codigo |
| `onyxlog-tui-review` | `onyxlog-tui-review` | `onyxlog-tui-review` | Revision de codigo del TUI Client |

4. Si el nombre visible y el skill asociado difieren, seguir la columna `subagent_type` para la delegacion y usar el skill indicado solo como referencia de contexto.
