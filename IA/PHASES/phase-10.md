# Fase 10: Applications API

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 9 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar el modulo de API para gestion de aplicaciones
- Crear funciones para CRUD de aplicaciones y gestion de API keys de aplicaciones
- Proveer la base para la pantalla de Applications

## Entregables

1. `src/api/applications.py` con CRUD de aplicaciones y API keys
2. Tests completos con mock_client

## Componentes a Implementar

### 1. src/api/applications.py — Application CRUD
- `async list_applications(client) -> list[AppRead]` — GET /api/v1/applications
- `async create_application(client, app: AppCreate) -> AppRead` — POST /api/v1/applications
- `async get_application(client, app_id: str) -> AppRead` — GET /api/v1/applications/{id}
- `async update_application(client, app_id: str, app: AppUpdate) -> AppRead` — PUT /api/v1/applications/{id}
- `async delete_application(client, app_id: str) -> None` — DELETE /api/v1/applications/{id}

### 2. src/api/applications.py — Application API Keys
- `async list_app_keys(client, app_id: str) -> list[ApiKeyRead]` — GET /api/v1/applications/{id}/keys
- `async create_app_key(client, app_id: str, key: ApiKeyCreate) -> ApiKeyCreateResponse` — POST /api/v1/applications/{id}/keys

## Tests a Implementar

**Archivos**: `tests/test_applications_api.py`

1. Test list_applications retorna lista de AppRead
2. Test list_applications con paginacion
3. Test create_application exitoso
4. Test create_application con app_id duplicado → DUPLICATE_ENTRY
5. Test get_application exitoso
6. Test get_application con id inexistente → NOT_FOUND
7. Test update_application exitoso
8. Test update_application con id inexistente → NOT_FOUND
9. Test delete_application exitoso
10. Test delete_application con id inexistente → NOT_FOUND
11. Test list_app_keys retorna lista de ApiKeyRead
12. Test create_app_key exitoso
13. Test create_app_key con nombre duplicado → DUPLICATE_ENTRY

## Criterios de Completitud

- [ ] CRUD de aplicaciones funciona correctamente
- [ ] Gestion de API keys de aplicaciones funciona
- [ ] Errores se mapean a ApiClientError
- [ ] `pytest tests/test_applications_api.py -v` pasa sin errores

**Progreso**: 0/5 (0%)

## Tareas

### T1: Implementar src/api/applications.py con CRUD de aplicaciones
- **Descripcion**: Crear src/api/applications.py con funciones async para CRUD de aplicaciones: list_applications(), create_application(), get_application(), update_application(), delete_application(). Todas usan OnyxLogClient._request() con autenticacion (X-API-Key header).
- **Archivos**: `src/api/applications.py`
- **Dependencias**: Fase 9 completada
- **Criterios**: Todas las funciones CRUD funcionan; errores se mapean a ApiClientError
- **Estimacion**: M

### T2: Implementar gestion de API keys de aplicaciones
- **Descripcion**: Agregar a src/api/applications.py las funciones list_app_keys() y create_app_key() para gestionar API keys de aplicaciones.
- **Archivos**: `src/api/applications.py`
- **Dependencias**: T1
- **Criterios**: list_app_keys() y create_app_key() funcionan correctamente
- **Estimacion**: S

### T3: Implementar tests/test_applications_api.py con mock_client
- **Descripcion**: Crear tests completos para applications.py usando httpx.MockTransport. Tests de: CRUD completo, paginacion, API keys, errores (NOT_FOUND, DUPLICATE_ENTRY, INVALID_API_KEY).
- **Archivos**: `tests/test_applications_api.py`
- **Dependencias**: T2
- **Criterios**: Todos los tests pasan; cobertura >90% de applications.py
- **Estimacion**: M

### T4: Actualizar README.md con seccion de Applications API
- **Descripcion**: Agregar seccion al README.md documentando las funciones de applications.py y los endpoints usados.
- **Archivos**: `README.md`
- **Dependencias**: T3
- **Criterios**: README.md incluye documentacion de Applications API
- **Estimacion**: S

### T5: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 10 completada: modulo de Applications API implementado.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T4
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (CRUD de aplicaciones)
2. T2 (API keys — depende de T1)
3. T3 (tests — depende de T2)
4. T4 (README — depende de T3)
5. T5 (STATE — depende de T4)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | La API puede cambiar los nombres de campos | Usar Pydantic con from_attributes=True para flexibilidad |

## Comandos de Verificacion

```bash
pytest tests/test_applications_api.py -v
ruff check src/api/applications.py
```

## Notas de Implementacion

- Todas las funciones requieren autenticacion (User API Key)
- Los endpoints usan /api/v1/applications como base
- list_applications() soporta parametros de paginacion (limit, offset)
- create_app_key() retorna la key completa (solo se muestra una vez)

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
