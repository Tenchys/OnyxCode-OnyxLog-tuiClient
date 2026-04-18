# Fase 12: Logs API

**Estado**: Completada | **Progreso**: 100% | **Fechas**: 2026-04-17 a 2026-04-18
**Dependencias**: Fase 9 | **Ultima actualizacion**: 2026-04-18

## Objetivos

- Implementar el modulo de API para consulta de logs
- Crear funciones para obtener logs, buscar por ID y consultar con filtros
- Proveer la base para la pantalla de Logs

## Entregables

1. `src/api/logs.py` con get_logs(), get_log_by_id(), query_logs()
2. Tests completos con mock_client

## Componentes Implementados

### 1. src/api/logs.py — Log retrieval
- `async get_logs(client, limit: int = 100, offset: int = 0) -> PaginatedResponse[LogRead]` — GET /api/v1/logs
- `async get_log_by_id(client, log_id: str) -> LogRead` — GET /api/v1/logs/{id}
- `async query_logs(client, query: LogQuery) -> PaginatedResponse[LogRead]` — POST /api/v1/logs/query

### 2. src/api/logs.py — Query parameters
- LogQuery soporta filtros: app_id, level, start_time, end_time, search, limit, offset
- get_logs() soporta paginacion con limit y offset
- query_logs() permite busquedas avanzadas con filtros combinados

## Tests Implementados

**Archivos**: `tests/test_logs_api.py`

1. Test get_logs retorna lista paginada de LogRead
2. Test get_logs con paginacion (limit, offset)
3. Test get_log_by_id retorna LogRead
4. Test get_log_by_id con id inexistente → NOT_FOUND
5. Test query_logs con filtro de level
6. Test query_logs con filtro de app_id
7. Test query_logs con filtro de timeframe
8. Test query_logs con busqueda de texto
9. Test query_logs con filtros combinados
10. Test query_logs con resultado vacio
11. Test error de conexion

## Criterios de Completitud

- [x] get_logs() funciona con paginacion
- [x] get_log_by_id() funciona correctamente
- [x] query_logs() funciona con todos los filtros
- [x] Errores se mapean a ApiClientError
- [x] `pytest tests/test_logs_api.py -v` pasa sin errores

**Progreso**: 4/4 (100%)

## Tareas

### T1: Implementar src/api/logs.py con get_logs, get_log_by_id, query_logs
- **Descripcion**: Crear src/api/logs.py con funciones async get_logs(), get_log_by_id(), query_logs(). get_logs() usa GET /api/v1/logs con paginacion. get_log_by_id() usa GET /api/v1/logs/{id}. query_logs() usa POST /api/v1/logs/query con LogQuery como body. Todas usan OnyxLogClient._request() con autenticacion (App API Key).
- **Archivos**: `src/api/logs.py`
- **Dependencias**: Fase 9 completada
- **Criterios**: Todas las funciones funcionan; paginacion funciona; filtros funcionan; errores se mapean a ApiClientError
- **Estimacion**: M

### T2: Implementar tests/test_logs_api.py con mock_client
- **Descripcion**: Crear tests completos para logs.py usando httpx.MockTransport. Tests de: get_logs con paginacion, get_log_by_id, query_logs con filtros (level, app_id, timeframe, search), filtros combinados, resultado vacio, errores.
- **Archivos**: `tests/test_logs_api.py`
- **Dependencias**: T1
- **Criterios**: Todos los tests pasan; cobertura >90% de logs.py
- **Estimacion**: S

### T3: Actualizar README.md con seccion de Logs API
- **Descripcion**: Agregar seccion al README.md documentando las funciones de logs.py y los endpoints usados.
- **Archivos**: `README.md`
- **Dependencias**: T2
- **Criterios**: README.md incluye documentacion de Logs API
- **Estimacion**: S

### T4: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 12 completada: modulo de Logs API implementado.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T3
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (logs.py)
2. T2 (tests — depende de T1)
3. T3 (README — depende de T2)
4. T4 (STATE — depende de T3)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | El endpoint de query puede tener parametros diferentes | Verificar con la referencia de API en AGENTS.md |

## Comandos de Verificacion

```bash
pytest tests/test_logs_api.py -v
ruff check src/api/logs.py
```

## Notas de Implementacion

- get_logs() y query_logs() usan App API Key (no User API Key)
- get_log_by_id() usa App API Key
- LogQuery permite filtros opcionales (todos los campos son None por defecto)
- PaginatedResponse es generica: PaginatedResponse[LogRead]

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
- **2026-04-18**: Fase completada; API, tests y documentacion sincronizados
