# Fase 3: Pydantic Schemas

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 2 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Definir todos los modelos Pydantic que el TUI necesita para interactuar con la API de OnyxLog
- Crear schemas de request y response para Auth, Applications, Logs, API Keys
- Incluir modelos de paginacion y errores
- Proveer tipos compartidos para los modulos api/ y screens/

## Entregables

1. `src/models/schemas.py` con todos los modelos Pydantic
2. Tests completos de serializacion, validacion y edge cases

## Componentes a Implementar

### 1. src/models/schemas.py — Auth schemas
- `UserCreate(username: str, email: str, password: str)`
- `UserRead(id: UUID, username: str, email: str, role: str, created_at: datetime)`
- `UserWithKey(user: UserRead, api_key: str)`
- `LoginRequest(username: str, password: str)`

### 2. src/models/schemas.py — Application schemas
- `AppCreate(name: str, app_id: str, description: str | None, environment: str)`
- `AppRead(id: UUID, name: str, app_id: str, description: str | None, environment: str, is_active: bool, created_at: datetime)`
- `AppUpdate(name: str | None, description: str | None, environment: str | None)`

### 3. src/models/schemas.py — Log schemas
- `LogLevel(str, Enum)` — DEBUG, INFO, WARNING, ERROR, CRITICAL
- `LogRead(id: UUID, timestamp: datetime, level: str, app_id: str, message: str, metadata: dict | None)`
- `LogCreate(app_id: str, level: str, message: str, metadata: dict | None)`
- `LogQuery(app_id: str | None, level: str | None, start_time: datetime | None, end_time: datetime | None, search: str | None, limit: int = 100, offset: int = 0)`

### 4. src/models/schemas.py — API Key schemas
- `ApiKeyRead(id: str, name: str, key_type: str, role: str | None, user_id: str | None, app_id: str | None, created_at: datetime, is_active: bool)`
- `ApiKeyCreate(name: str, key_type: str, role: str | None)`
- `ApiKeyCreateResponse(id: str, name: str, key: str, key_type: str)`

### 5. src/models/schemas.py — Shared schemas
- `PaginatedResponse(items: list, total: int, limit: int, offset: int)`
- `ErrorResponse(error_code: str, message: str, details: dict | None)`
- `HealthResponse(status: str, version: str)`
- `StatsOverview(total_logs: int, total_applications: int, active_applications: int, recent_logs_24h: int)`

## Tests a Implementar

**Archivos**: `tests/test_schemas.py`

1. Test UserCreate serializacion y validacion
2. Test UserRead con from_attributes
3. Test AppCreate/AppRead/AppUpdate serializacion
4. Test LogRead/LogCreate/LogQuery con filtros opcionales
5. Test ApiKeyRead/ApiKeyCreate/ApiKeyCreateResponse
6. Test PaginatedResponse con lista generica
7. Test ErrorResponse con details opcionales
8. Test LogLevel enum valores
9. Test edge cases: campos None, strings vacios, tipos incorrectos

## Criterios de Completitud

- [ ] Todos los modelos Pydantic se instancian y serializan correctamente
- [ ] La validacion rechaza datos invalidos
- [ ] Los campos opcionales funcionan con None
- [ ] `pytest tests/test_schemas.py -v` pasa sin errores

**Progreso**: 0/4 (0%)

## Tareas

### T1: Implementar src/models/schemas.py con todos los modelos Pydantic
- **Descripcion**: Crear src/models/schemas.py con todos los modelos Pydantic necesarios para el TUI: Auth (UserCreate, UserRead, UserWithKey, LoginRequest), Applications (AppCreate, AppRead, AppUpdate), Logs (LogLevel, LogRead, LogCreate, LogQuery), API Keys (ApiKeyRead, ApiKeyCreate, ApiKeyCreateResponse), y compartidos (PaginatedResponse, ErrorResponse, HealthResponse, StatsOverview). Usar `from __future__ import annotations` y `model_config = ConfigDict(from_attributes=True)`.
- **Archivos**: `src/models/schemas.py`
- **Dependencias**: Fase 2 completada
- **Criterios**: Todos los modelos se instancian; serializacion/deserializacion funciona; validacion rechaza datos invalidos
- **Estimacion**: M

### T2: Implementar tests/test_schemas.py
- **Descripcion**: Crear tests completos para todos los modelos Pydantic: serializacion, validacion, edge cases (campos None, strings vacios, tipos incorrectos), enum LogLevel, PaginatedResponse generico.
- **Archivos**: `tests/test_schemas.py`
- **Dependencias**: T1
- **Criterios**: Todos los tests pasan; cobertura >90% de schemas.py
- **Estimacion**: S

### T3: Actualizar README.md con seccion de modelos
- **Descripcion**: Agregar seccion al README.md listando los modelos Pydantic disponibles y su proposito.
- **Archivos**: `README.md`
- **Dependencias**: T2
- **Criterios**: README.md incluye referencia a los modelos Pydantic
- **Estimacion**: S

### T4: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 3 completada: modelos Pydantic implementados.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T3
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (schemas.py)
2. T2 (tests — depende de T1)
3. T3 (README — depende de T2)
4. T4 (STATE — depende de T3)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | Los schemas pueden no coincidir con la API real del backend | Seguir la referencia en AGENTS.md y ajustar si hay diferencias |

## Comandos de Verificacion

```bash
pytest tests/test_schemas.py -v
ruff check src/models/schemas.py
```

## Notas de Implementacion

- Todos los modelos usan `from __future__ import annotations`
- Los modelos de lectura usan `model_config = ConfigDict(from_attributes=True)` para compatibilidad con respuestas JSON
- Los UUID se representan como strings en la serializacion
- Los campos opcionales usan `str | None = None` (Python 3.11+ syntax)

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
