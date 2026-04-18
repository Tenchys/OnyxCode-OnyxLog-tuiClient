# Fase 5: Local SQLite Database

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 4 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar el modulo de base de datos local SQLite con aiosqlite
- Crear la tabla api_keys y las operaciones CRUD
- Proveer funciones para almacenar, recuperar y gestionar API keys localmente
- Garantizar que las API keys nunca se almacenan en texto plano en archivos de configuracion

## Entregables

1. `src/db.py` con init_db(), store_key(), get_active_key(), list_keys(), delete_key(), deactivate_key()
2. Tests completos con SQLite real en tmp_path (sin mocks)

## Componentes a Implementar

### 1. src/db.py — Database initialization
- `init_db(db_path: str | None = None)` — crea la tabla api_keys si no existe
- Usa el schema definido en AGENTS.md (id, name, key, key_type, role, user_id, app_id, server_url, created_at, is_active)
- Crea el directorio padre si no existe

### 2. src/db.py — CRUD operations
- `store_key(id, name, key, key_type, server_url, role=None, user_id=None, app_id=None, db_path=None)` — inserta una nueva API key
- `get_active_key(server_url, db_path=None)` — retorna la API key activa para un servidor dado
- `list_keys(server_url=None, db_path=None)` — lista todas las keys, opcionalmente filtradas por servidor
- `delete_key(id, db_path=None)` — elimina una API key por id
- `deactivate_key(id, db_path=None)` — marca una API key como inactiva (is_active=0)

### 3. src/db.py — Helper functions
- `_get_db_path(db_path)` — resuelve el path de la DB (usa Settings.db_path si no se proporciona)
- Todas las funciones aceptan `db_path` opcional para testing

## Tests a Implementar

**Archivos**: `tests/test_db.py`

1. Test init_db crea la tabla api_keys
2. Test store_key inserta una key correctamente
3. Test store_key con key_type='user' y role='admin'
4. Test store_key con key_type='application' y app_id
5. Test get_active_key retorna la key activa para un servidor
6. Test get_active_key retorna None si no hay keys
7. Test get_active_key ignora keys inactivas
8. Test list_keys retorna todas las keys
9. Test list_keys filtra por server_url
10. Test delete_key elimina una key por id
11. Test delete_key con id inexistente no falla
12. Test deactivate_key marca key como inactiva
13. Test store_key crea el directorio si no existe

## Criterios de Completitud

- [ ] init_db() crea la tabla correctamente
- [ ] store_key() inserta y get_active_key() recupera
- [ ] list_keys() filtra por server_url
- [ ] delete_key() y deactivate_key() funcionan
- [ ] Los tests usan SQLite real en tmp_path (sin mocks)
- [ ] `pytest tests/test_db.py -v` pasa sin errores

**Progreso**: 0/4 (0%)

## Tareas

### T1: Implementar src/db.py con init_db y CRUD operations
- **Descripcion**: Crear src/db.py con init_db() (crea tabla api_keys), store_key(), get_active_key(), list_keys(), delete_key(), deactivate_key(). Todas las funciones son async y usan aiosqlite. Aceptar db_path opcional para testing. Crear directorio padre si no existe.
- **Archivos**: `src/db.py`
- **Dependencias**: Fase 4 completada
- **Criterios**: Todas las funciones CRUD funcionan; init_db crea la tabla; store_key/get_active_key funcionan correctamente
- **Estimacion**: M

### T2: Implementar tests/test_db.py con SQLite real en tmp_path
- **Descripcion**: Crear tests completos usando SQLite real en tmp_path (sin mocks). Tests de init_db, store_key, get_active_key, list_keys, delete_key, deactivate_key. Usar fixture de tmp_path para DB aislada.
- **Archivos**: `tests/test_db.py`
- **Dependencias**: T1
- **Criterios**: Todos los tests pasan; cobertura >90% de db.py; se usa SQLite real (no mocks)
- **Estimacion**: M

### T3: Actualizar README.md con seccion de base de datos local
- **Descripcion**: Agregar seccion al README.md documentando la base de datos local SQLite, la tabla api_keys y las operaciones disponibles.
- **Archivos**: `README.md`
- **Dependencias**: T2
- **Criterios**: README.md incluye documentacion de la DB local
- **Estimacion**: S

### T4: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 5 completada: modulo de base de datos local implementado.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T3
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (db.py)
2. T2 (tests — depende de T1)
3. T3 (README — depende de T2)
4. T4 (STATE — depende de T3)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | aiosqlite puede tener diferencias de API con sqlite3 sincrono | Usar aiosqlite directamente, no wrapper |
| T2 | Tests pueden ser lentos si no se limpia la DB entre tests | Usar tmp_path para DB aislada por test |

## Comandos de Verificacion

```bash
pytest tests/test_db.py -v
ruff check src/db.py
```

## Notas de Implementacion

- Todas las funciones son async (aiosqlite)
- Se usa `async with aiosqlite.connect(db_path) as db` en cada funcion (sin conexion persistente)
- El path por defecto viene de Settings.db_path (~/.onyxlog/keys.db)
- El directorio ~/.onyxlog/ se crea automaticamente si no existe
- Las API keys se almacenan tal cual (el servidor las genera, el TUI solo las guarda)

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
