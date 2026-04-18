# Fase 4: API Client Base

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 3 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar el cliente HTTP base con httpx.AsyncClient
- Crear el sistema de manejo de errores (ApiClientError)
- Implementar autenticacion via header X-API-Key
- Implementar health check sin autenticacion
- Proveer la base sobre la que los modulos api/ construyen sus llamadas

## Entregables

1. `src/api/client.py` con OnyxLogClient
2. Sistema de errores (ApiClientError, ConnectionError, TimeoutError)
3. Health check funcional
4. Tests completos con MockTransport

## Componentes a Implementar

### 1. src/api/client.py — OnyxLogClient
- Clase `OnyxLogClient` con httpx.AsyncClient interno
- Constructor: `__init__(base_url: str)` — crea AsyncClient con timeout de 30s
- Metodo `_request(method, path, **kwargs)` — metodo base para todas las llamadas
- Metodo `_headers()` — retorna dict con `X-API-Key` si esta configurado
- Metodo `set_api_key(key: str)` — configura la API key para requests autenticadas
- Metodo `clear_api_key()` — elimina la API key configurada
- Metodo `close()` — cierra el AsyncClient
- Propiedad `is_authenticated` — True si hay API key configurado
- Soporte para context manager (`async with`)

### 2. src/api/client.py — ApiClientError
- Clase `ApiClientError(Exception)` con campos: `error_code`, `status_code`, `message`
- Parsing de respuestas de error del servidor OnyxLog (formato `{"error_code": "...", "message": "..."}`)
- Manejo de errores de conexion (httpx.ConnectError → ApiClientError con CONNECTION_ERROR)
- Manejo de timeouts (httpx.TimeoutException → ApiClientError con TIMEOUT)

### 3. src/api/client.py — Health check
- Metodo `health_check() -> HealthResponse` — GET /health (sin /api/v1 prefix, sin auth)
- Retorna HealthResponse con status y version del servidor

## Tests a Implementar

**Archivos**: `tests/test_client.py`

1. Test OnyxLogClient.__init__ con base_url
2. Test _headers() sin API key retorna dict vacio
3. Test _headers() con API key retorna dict con X-API-Key
4. Test set_api_key() y clear_api_key()
5. Test health_check() exitoso (MockTransport con respuesta 200)
6. Test _request() GET exitoso
7. Test _request() POST exitoso con body
8. Test _request() error 401 → ApiClientError(INVALID_CREDENTIALS)
9. Test _request() error 403 → ApiClientError(INVALID_API_KEY)
10. Test _request() error 404 → ApiClientError(NOT_FOUND)
11. Test _request() error 409 → ApiClientError(DUPLICATE_ENTRY)
12. Test _request() error 422 → ApiClientError(VALIDATION_ERROR)
13. Test _request() error 429 → ApiClientError(RATE_LIMITED)
14. Test _request() error 500 → ApiClientError(INTERNAL_ERROR)
15. Test conexion rechazada → ApiClientError(CONNECTION_ERROR)
16. Test timeout → ApiClientError(TIMEOUT)
17. Test context manager (async with)
18. Test is_authenticated property

## Criterios de Completitud

- [ ] OnyxLogClient se instancia y cierra correctamente
- [ ] set_api_key/clear_api_key funcionan
- [ ] _request() maneja respuestas exitosas y de error
- [ ] ApiClientError parsea correctamente los errores del servidor
- [ ] health_check() funciona sin autenticacion
- [ ] Errores de conexion y timeout se manejan correctamente
- [ ] `pytest tests/test_client.py -v` pasa sin errores

**Progreso**: 0/6 (0%)

## Tareas

### T1: Implementar src/api/client.py con OnyxLogClient y ApiClientError
- **Descripcion**: Crear src/api/client.py con la clase OnyxLogClient (httpx.AsyncClient interno, _request(), _headers(), set_api_key(), clear_api_key(), close(), is_authenticated, context manager) y ApiClientError (error_code, status_code, message, parsing de errores del servidor, manejo de ConnectError y Timeout).
- **Archivos**: `src/api/client.py`
- **Dependencias**: Fase 3 completada
- **Criterios**: OnyxLogClient se instancia; set_api_key/clear_api_key funcionan; ApiClientError parsea errores; context manager funciona
- **Estimacion**: M

### T2: Implementar health_check() en OnyxLogClient
- **Descripcion**: Agregar metodo health_check() a OnyxLogClient que haga GET /health (sin /api/v1 prefix, sin auth header) y retorne HealthResponse. El endpoint /health no requiere autenticacion.
- **Archivos**: `src/api/client.py`
- **Dependencias**: T1
- **Criterios**: health_check() retorna HealthResponse con status y version; no envia X-API-Key header
- **Estimacion**: S

### T3: Implementar tests/test_client.py con MockTransport
- **Descripcion**: Crear tests completos usando httpx.MockTransport para simular respuestas del servidor. Tests de: inicializacion, headers, API key, health_check, requests exitosos, errores HTTP (401, 403, 404, 409, 422, 429, 500), errores de conexion, timeout, context manager.
- **Archivos**: `tests/test_client.py`
- **Dependencias**: T2
- **Criterios**: Todos los tests pasan; cobertura >90% de client.py
- **Estimacion**: M

### T4: Actualizar README.md con seccion de API Client
- **Descripcion**: Agregar seccion al README.md documentando OnyxLogClient, ApiClientError y health_check.
- **Archivos**: `README.md`
- **Dependencias**: T3
- **Criterios**: README.md incluye documentacion del API client
- **Estimacion**: S

### T5: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 4 completada: API client base implementado.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T4
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

### T6: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 4 completada: API client base implementado.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T5
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (OnyxLogClient + ApiClientError)
2. T2 (health_check — depende de T1)
3. T3 (tests — depende de T2)
4. T4 (README — depende de T3)
5. T5 (STATE — depende de T4)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | httpx.AsyncClient API puede diferir entre versiones | Fijar httpx>=0.25 en pyproject.toml |
| T3 | MockTransport puede no cubrir todos los edge cases | Usar tambien tests de integracion con servidor mock |

## Comandos de Verificacion

```bash
pytest tests/test_client.py -v
ruff check src/api/client.py
```

## Notas de Implementacion

- OnyxLogClient usa httpx.AsyncClient internamente, no hereda de el
- El path base /api/v1 se agrega automaticamente en _request()
- El endpoint /health es la unica ruta sin /api/v1 prefix
- ApiClientError hereda de Exception y es la unica excepcion que las pantallas deben manejar
- Los errores de conexion (ConnectError) y timeout (TimeoutException) se convierten en ApiClientError con codigos especificos

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
