# Fase 6: Auth API Module

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 5 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar el modulo de autenticacion con la API de OnyxLog
- Crear funciones para registro y login de usuarios
- Integrar con OnyxLogClient para manejar errores de autenticacion
- Proveer la base para el flujo de login del TUI

## Entregables

1. `src/api/auth.py` con register() y login()
2. Tests completos con mock_client

## Componentes a Implementar

### 1. src/api/auth.py — register()
- `async register(client: OnyxLogClient, username: str, email: str, password: str) -> UserWithKey`
- POST /api/v1/auth/register con body `{"username": "...", "email": "...", "password": "..."}`
- No requiere autenticacion
- Retorna UserWithKey con user y api_key

### 2. src/api/auth.py — login()
- `async login(client: OnyxLogClient, username: str, password: str) -> UserWithKey`
- POST /api/v1/auth/login con body `{"username": "...", "password": "..."}`
- No requiere autenticacion
- Retorna UserWithKey con user y api_key

## Tests a Implementar

**Archivos**: `tests/test_auth.py`

1. Test register exitoso — retorna UserWithKey
2. Test login exitoso — retorna UserWithKey
3. Test register con username duplicado → ApiClientError(DUPLICATE_ENTRY)
4. Test login con credenciales invalidas → ApiClientError(INVALID_CREDENTIALS)
5. Test register con datos invalidos → ApiClientError(VALIDATION_ERROR)
6. Test login con servidor no disponible → ApiClientError(CONNECTION_ERROR)

## Criterios de Completitud

- [ ] register() envia POST /api/v1/auth/register correctamente
- [ ] login() envia POST /api/v1/auth/login correctamente
- [ ] Los errores de autenticacion se mapean a ApiClientError
- [ ] `pytest tests/test_auth.py -v` pasa sin errores

**Progreso**: 0/4 (0%)

## Tareas

### T1: Implementar src/api/auth.py con register() y login()
- **Descripcion**: Crear src/api/auth.py con funciones async register() y login() que usen OnyxLogClient._request() para hacer POST a /api/v1/auth/register y /api/v1/auth/login respectivamente. Ambas retornan UserWithKey. Manejar errores con ApiClientError.
- **Archivos**: `src/api/auth.py`
- **Dependencias**: Fase 5 completada
- **Criterios**: register() y login() funcionan correctamente; errores se mapean a ApiClientError
- **Estimacion**: S

### T2: Implementar tests/test_auth.py con mock_client
- **Descripcion**: Crear tests para auth.py usando httpx.MockTransport para simular respuestas del servidor. Tests de: registro exitoso, login exitoso, username duplicado, credenciales invalidas, datos invalidos, servidor no disponible.
- **Archivos**: `tests/test_auth.py`
- **Dependencias**: T1
- **Criterios**: Todos los tests pasan; cobertura >90% de auth.py
- **Estimacion**: S

### T3: Actualizar README.md con seccion de autenticacion
- **Descripcion**: Agregar seccion al README.md documentando el flujo de autenticacion (register, login) y los endpoints usados.
- **Archivos**: `README.md`
- **Dependencias**: T2
- **Criterios**: README.md incluye documentacion de autenticacion
- **Estimacion**: S

### T4: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 6 completada: modulo de autenticacion implementado.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T3
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (auth.py)
2. T2 (tests — depende de T1)
3. T3 (README — depende de T2)
4. T4 (STATE — depende de T3)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | La respuesta del servidor puede tener campos adicionales | Usar Pydantic para parsear solo los campos necesarios |

## Comandos de Verificacion

```bash
pytest tests/test_auth.py -v
ruff check src/api/auth.py
```

## Notas de Implementacion

- register() y login() son funciones modulo, no metodos de clase
- Reciben OnyxLogClient como primer parametro (inyeccion de dependencia)
- No requieren autenticacion (no envian X-API-Key header)
- Los errores del servidor se convierten en ApiClientError automaticamente por OnyxLogClient._request()

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
