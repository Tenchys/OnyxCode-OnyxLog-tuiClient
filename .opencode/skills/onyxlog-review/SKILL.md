---
name: onyxlog-review
description: Criterios de revision de codigo para OnyxLog. Evalua arquitectura, seguridad, data layer, API, testing, readiness para produccion, performance y convenciones. Genera informe con veredicto de despliegue.
metadata:
  audience: reviewers
  workflow: onyxlog
---

## Categorias de Revision

Se evaluan 8 categorias. Cada hallazgo se clasifica con una severidad:

| Severidad | Significado | Accion |
|-----------|-------------|--------|
| **BLOCKER** | Impide despliegue a produccion | Debe corregirse antes de cualquier merge |
| **CRITICAL** | Riesgo alto en produccion | Debe corregirse antes de deploy |
| **WARNING** | Problema potencial | Recomendado corregir, no bloquea |
| **INFO** | Observacion menor | Sugerencia de mejora |

---

### 1. Arquitectura

Verifica la estructura de capas y direccion de dependencias.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| ARCH-01 | BLOCKER | Las rutas NO contienen logica de negocio, solo delegan al servicio |
| ARCH-02 | CRITICAL | Los servicios NO importan de `api/`, solo de `models/`, `schemas/`, `core/` |
| ARCH-03 | CRITICAL | Los modelos NO dependen de schemas ni servicios |
| ARCH-04 | CRITICAL | Los schemas NO dependen de modelos (usan `from_attributes=True`) |
| ARCH-05 | WARNING | Cada capa esta en su directorio correcto (`api/`, `core/`, `models/`, `schemas/`, `services/`, `utils/`) |
| ARCH-06 | WARNING | No hay imports circulares entre modulos |
| ARCH-07 | INFO | Archivos no exceden ~300 lineas (considerar refactor) |

Patrones de deteccion:
- Buscar `from src.api` en archivos de `services/`
- Buscar `from src.services` en archivos de `models/`
- Buscar logica de negocio (queries SQLAlchemy, calculos) directamente en route handlers
- Buscar `from src.models` en archivos de `schemas/`

---

### 2. Seguridad

Verifica vulnerabilidades que comprometan el sistema en produccion.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| SEC-01 | BLOCKER | No hay secrets hardcodeados (API keys, passwords, tokens, SECRET_KEY literales) |
| SEC-02 | BLOCKER | No hay queries SQL raw sin parametrizar (`text()` con concatenacion) |
| SEC-03 | BLOCKER | Todos los endpoints protegidos requieren `Depends(get_current_user)` |
| SEC-04 | CRITICAL | Validacion de `custom_data` con profundidad maxima 1 |
| SEC-05 | CRITICAL | API Keys no se logean ni se exponen en respuestas completas |
| SEC-06 | CRITICAL | CORS configurado con origenes explicitos (no `*`) para produccion |
| SEC-07 | WARNING | Middleware de autenticacion valida API Key antes de procesar request |
| SEC-08 | WARNING | Rate limiting implementado o planificado |
| SEC-09 | WARNING | No se exponen stack traces internos en respuestas de error 500 |
| SEC-10 | INFO | Headers de seguridad HTTP presentes (X-Content-Type-Options, etc.) |

Patrones de deteccion:
- Buscar strings que parezcan API keys: `sk_`, `key_`, `secret`, `password` asignados como literales
- Buscar `text(` con f-strings o concatenacion (SQL injection)
- Buscar `@router` sin `Depends(get_current_user)` en endpoints que no son publicos
- Buscar `custom_data` sin `@field_validator` de profundidad
- Buscar `CORSMiddleware` con `allow_origins=["*"]`
- Buscar `print(api_key)` o `logger.*(api_key)` o `logger.*(password)`

---

### 3. Data Layer

Verifica modelos, schemas, migraciones y validaciones.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| DAT-01 | CRITICAL | Todos los modelos heredan de `BaseModel` (incluye `id`, `created_at`, `updated_at`) |
| DAT-02 | CRITICAL | Foreign keys usan `UUID(as_uuid=True)` |
| DAT-03 | CRITICAL | Relaciones con `back_populates` en ambos lados |
| DAT-04 | CRITICAL | Indices compuestos y GIN definidos en `__table_args__`, no con `index=True` suelto |
| DAT-05 | CRITICAL | Schema `Create` sin `id` ni timestamps |
| DAT-06 | CRITICAL | Schema `Read` con `model_config = ConfigDict(from_attributes=True)` |
| DAT-07 | CRITICAL | Schema `Update` con campos opcionales |
| DAT-08 | CRITICAL | `custom_data` validado con `validate_custom_data_depth` |
| DAT-09 | WARNING | Migracion Alembic creada si se modifico un modelo |
| DAT-10 | WARNING | Columnas con longitud definida (`String(100)`, no `String` sin limite) |
| DAT-11 | INFO | Enums de BD usan `name=` descriptivo (`log_level_enum`, `environment_enum`) |

Patrones de deteccion:
- Buscar `class.*\(Base\):` en vez de `class.*\(BaseModel\):`
- Buscar `Column(UUID` sin `as_uuid=True`
- Buscar `relationship(` sin `back_populates`
- Buscar `index=True` en Column para campos que deberian tener indice compuesto
- Buscar schemas `Create` con campos `id` o `created_at`
- Buscar schemas `Read` sin `from_attributes`

---

### 4. API Patterns

Verifica endpoints, respuestas, versionado y autenticacion.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| API-01 | CRITICAL | Toda respuesta de error usa estructura `{"message": ..., "error_code": ...}` |
| API-02 | CRITICAL | Endpoints usan `response_model` explicito |
| API-03 | CRITICAL | Rutas bajo prefijo `/api/v1` |
| API-04 | CRITICAL | Status codes correctos (201 para creacion, 204 para delete, 200 para get/list) |
| API-05 | WARNING | Respuestas paginadas usan `PaginatedResponse[T]` |
| API-06 | WARNING | Routers registrados en `routes/__init__.py` e incluidos en `main.py` |
| API-07 | WARNING | Nuevos routers usan `APIRouter(prefix="/<recurso>", tags=["<recurso>"])` |
| API-08 | INFO | Endpoints documentados con `summary` o `description` en decorador |

Patrones de deteccion:
- Buscar `HTTPException` sin `detail={"message": ..., "error_code": ...}`
- Buscar `@router` sin `response_model=`
- Buscar rutas sin prefijo `/api/v1`
- Buscar `status_code=200` en endpoints POST (deberia ser 201)
- Buscar respuestas de lista sin `PaginatedResponse`

Codigos de error estandar a verificar:

| HTTP | error_code | Uso |
|------|------------|-----|
| 400 | VALIDATION_ERROR | Datos invalidos |
| 401 | AUTH_REQUIRED | API Key faltante |
| 403 | INVALID_API_KEY | API Key invalida o revocada |
| 404 | NOT_FOUND | Recurso no encontrado |
| 409 | ALREADY_EXISTS | Recurso duplicado |
| 422 | INVALID_CUSTOM_DATA | custom_data no pasa validacion |
| 429 | RATE_LIMITED | Rate limit excedido |
| 500 | INTERNAL_ERROR | Error inesperado |

---

### 5. Testing

Verifica calidad y cobertura de tests.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| TST-01 | CRITICAL | Cobertura >= 80% |
| TST-02 | CRITICAL | Tests de endpoints (integracion) priorizados sobre unitarios de servicios |
| TST-03 | WARNING | Tests siguen patron AAA (Arrange, Act, Assert) |
| TST-04 | WARNING | Tests async usan `@pytest.mark.asyncio` |
| TST-05 | WARNING | Fixtures async usan `@pytest_asyncio.fixture` |
| TST-06 | WARNING | NO hacer mock del ORM/SQLAlchemy (usar DB de test real) |
| TST-07 | WARNING | DB session con rollback por test para aislamiento |
| TST-08 | WARNING | Nombres descriptivos: `test_<accion>_<escenario>` |
| TST-09 | WARNING | Se testean happy path, error paths y edge cases |
| TST-10 | INFO | Archivo de test por modulo: `test_logs.py` para `routes/logs.py` |
| TST-11 | INFO | Clase `TestXxx` por entidad |

Patrones de deteccion:
- Buscar tests sin `assert`
- Buscar `mock.*AsyncSession` o `mock.*session` (no se debe mockear el ORM)
- Buscar tests async sin `@pytest.mark.asyncio`
- Buscar `Mock` o `MagicMock` para dependencias internas del proyecto
- Verificar que `conftest.py` tiene las fixtures base (engine, db_session, async_client, test_user, auth_headers, test_application)

---

### 6. Produccion Readiness

Verifica si el sistema esta listo para desplegarse a produccion.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| PRD-01 | BLOCKER | No hay archivos `.env` commiteados (solo `.env.example`) |
| PRD-02 | BLOCKER | Health checks implementados (`/health`, `/ready`, `/live`) |
| PRD-03 | CRITICAL | Docker optimizado (multi-stage, non-root user, .dockerignore) |
| PRD-04 | CRITICAL | Rate limiting activo por API Key y por IP |
| PRD-05 | CRITICAL | Variables de entorno con prefijo `ONYXLOG_` en configuracion |
| PRD-06 | WARNING | Logging estructurado para produccion (no `print()`) |
| PRD-07 | WARNING | CI/CD pipeline configurado (tests, lint, build automaticos) |
| PRD-08 | WARNING | Scripts de backup/restore para base de datos |
| PRD-09 | INFO | Documentacion OpenAPI completa y accesible |
| PRD-10 | INFO | Variables de entorno documentadas en `.env.example` y README |

Patrones de deteccion:
- Buscar `.env` en `git status` o sin `.env` en `.gitignore`
- Buscar `print(` en codigo de produccion (no tests)
- Buscar `BaseSettings` sin env_prefix `ONYXLOG_`
- Verificar existencia de `Dockerfile` con `FROM` multi-stage
- Verificar existencia de `.dockerignore`

---

### 7. Performance

Verifica optimizaciones para carga en produccion.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| PRF-01 | CRITICAL | Columna JSONB `custom_data` tiene indice GIN |
| PRF-02 | WARNING | Indices compuestos para queries frecuentes (`timestamp+level`, `app_id+environment`) |
| PRF-03 | WARNING | Paginacion usa `offset/limit` o cursor (no carga todos los registros) |
| PRF-04 | WARNING | No hay queries N+1 (eager loading donde sea necesario) |
| PRF-05 | WARNING | Connection pooling configurado (`pool_size`, `max_overflow`) |
| PRF-06 | INFO | Queries optimizadas con `EXPLAIN ANALYZE` verificadas |
| PRF-07 | INFO | `select()` especifico en vez de `select('*')` o cargas innecesarias |

Patrones de deteccion:
- Buscar `Column(JSONB)` sin indice GIN en `__table_args__`
- Buscar `session.execute(select(Model))` sin `limit` o `offset` en servicios
- Buscar `lazy=True` (default) en relationships accedidas frecuentemente
- Buscar `pool_size` en configuracion de database

---

### 8. Convenciones

Verifica estilo Python y convenciones del proyecto.

| Regla | Severidad | Criterio |
|-------|-----------|----------|
| CON-01 | WARNING | `from __future__ import annotations` en todos los archivos |
| CON-02 | WARNING | Type hints en todas las firmas de funciones y metodos |
| CON-03 | WARNING | Sin comentarios en codigo salvo docstrings publicos |
| CON-04 | INFO | Formato con `black` (line length 88) |
| CON-05 | INFO | Imports ordenados con `isort` |
| CON-06 | INFO | Naming correcto por capa (ver tabla) |
| CON-07 | INFO | `pydantic-settings` con `BaseSettings` en `core/config.py` |

Tabla de naming:

| Capa | Archivo | Clase/Funcion |
|------|---------|---------------|
| models/ | `user.py` | `User` (singular) |
| schemas/ | `log.py` | `LogCreate`, `LogRead`, `LogQuery` |
| services/ | `log_service.py` | `LogService` (clase) o funciones `create_log`, `query_logs` |
| routes/ | `logs.py` | Router con prefijo `/logs` |
| utils/ | `validators.py` | `validate_custom_data_depth` |

Patrones de deteccion:
- Buscar archivos `.py` sin `from __future__ import annotations`
- Buscar funciones sin type hints: `def func(` sin `: `
- Buscar comentarios con `#` que no sean TODOs legítimos
- Buscar nombres de modelo en plural (ej: `Users` en vez de `User`)
- Buscar schemas sin sufijo apropiado (`Create`, `Read`, `Update`, `Query`)

---

## Formato del Informe

El informe SIEMPRE sigue esta estructura:

```markdown
# Informe de Revision — OnyxLog

## Veredicto: [DEPLOY_BLOCKED | DEPLOY_CONDITIONAL | DEPLOY_APPROVED]

## Resumen
- Blockers: X
- Criticals: X
- Warnings: X
- Infos: X

## Archivos Revisados
- `src/api/routes/logs.py`
- `src/services/log_service.py`
- ...

---

### BLOCKERS

| # | Regla | Archivo | Linea | Descripcion |
|---|-------|---------|--------|-------------|
| 1 | SEC-01 | src/core/config.py | 15 | SECRET_KEY hardcodeado como literal |

### CRITICALS

| # | Regla | Archivo | Linea | Descripcion | Sugerencia |
|---|-------|---------|--------|-------------|------------|
| 1 | ARCH-01 | src/api/routes/logs.py | 42 | Logica de negocio en route handler | Mover a log_service.py |

### WARNINGS

| # | Regla | Archivo | Descripcion |
|---|-------|---------|-------------|
| 1 | CON-01 | src/schemas/log.py | Falta `from __future__ import annotations` |

### INFOS

| # | Regla | Archivo | Descripcion |
|---|-------|---------|-------------|
| 1 | CON-04 | src/services/auth_service.py | Linea > 88 caracteres (black) |

---

## Checklist de Produccion

- [x] Autenticacion completa en endpoints protegidos
- [x] Sin secrets en codigo fuente
- [ ] Migraciones Alembic al dia
- [ ] Cobertura >= 80%
- [ ] Health checks implementados
- [ ] Rate limiting activo
- [ ] Docker optimizado (multi-stage)
- [ ] Variables de entorno documentadas
- [ ] Logging estructurado (sin print)
- [ ] CORS configurado sin wildcard en produccion

---

## Detalle por Archivo

### src/api/routes/logs.py
- **Blockers**: 0 | **Criticals**: 1 | **Warnings**: 0
- ARCH-01: Logica de query en route handler (linea 42). Mover a LogService.query_logs().

### src/core/config.py
- **Blockers**: 1 | **Criticals**: 0 | **Warnings**: 0
- SEC-01: SECRET_KEY hardcodeado (linea 15). Usar variable de entorno ONYXLOG_SECRET_KEY.
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
- Se enfoca en los cambios introducidos

### Modo Full (`--scope full`)
- Leer todo el directorio `src/`
- Auditar todos los archivos del proyecto
- Mas lento pero exhaustivo
- Ideal para revisiones periodicas o pre-produccion

### Flujo de Revision

1. Cargar skills `onyxlog-coding`, `onyxlog-api-patterns`, `onyxlog-data-layer`, `onyxlog-testing`
2. Determinar scope (diff o full)
3. Si diff: ejecutar `git diff --name-only`, leer archivos cambiados
4. Si full: leer todo `src/` recursivamente
5. Para cada archivo, evaluar contra las 8 categorias
6. Clasificar cada hallazgo por severidad
7. Compilar informe con veredicto
8. Retornar informe completo

### Prioridad de Revision por Capa

Cuando se revisa en modo diff, priorizar en este orden:

1. `services/` — Logica de negocio, mayor riesgo
2. `api/routes/` — Endpoints, superficie de ataque
3. `core/` — Configuracion, seguridad, database
4. `models/` — Estructura de datos
5. `schemas/` — Validacion de entrada
6. `utils/` — Helpers, menor riesgo
