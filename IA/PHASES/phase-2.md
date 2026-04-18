# Fase 2: Configuration Module

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 1 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar el modulo de configuracion con pydantic-settings
- Soportar prioridad: CLI > env ONYXLOG_* > config file > defaults
- Crear el sistema de lectura/escritura de config.toml
- Proveer Settings reutilizable por todos los modulos del TUI

## Entregables

1. `src/config.py` con clase Settings (pydantic-settings)
2. Soporte para config file `~/.onyxlog/config.toml`
3. Tests completos de configuracion (defaults, env vars, config file)

## Componentes a Implementar

### 1. src/config.py — Settings
- Clase `Settings(BaseSettings)` con campos: `onyxlog_url`, `db_path`, `config_path`
- Defaults: `onyxlog_url=http://localhost:8000`, `db_path=~/.onyxlog/keys.db`, `config_path=~/.onyxlog/config.toml`
- Env prefix: `ONYXLOG_`
- Metodo `save_to_file()` para escribir config.toml
- Metodo de clase `load_from_file()` para leer config.toml
- Propiedad `resolved_url` que aplica prioridad: CLI > env > file > default

### 2. Config file handling
- Crear directorio `~/.onyxlog/` si no existe
- Leer/escribir `config.toml` con seccion `[server]`
- Manejar errores de archivo corrupto o permisos

## Tests a Implementar

**Archivos**: `tests/test_config.py`

1. Test defaults: Settings() usa valores por defecto
2. Test env vars: ONYXLOG_URL overridea el default
3. Test config file: lectura desde config.toml
4. Test save_to_file: escritura de config.toml
5. Test priority: CLI > env > file > default
6. Test directorio creado automaticamente

## Criterios de Completitud

- [ ] `Settings()` retorna valores por defecto
- [ ] `ONYXLOG_URL` env var overridea el default
- [ ] config.toml se lee/escribe correctamente
- [ ] La prioridad CLI > env > file > default funciona
- [ ] `pytest tests/test_config.py -v` pasa sin errores

**Progreso**: 0/5 (0%)

## Tareas

### T1: Implementar src/config.py con Settings y config file handling
- **Descripcion**: Crear src/config.py con clase Settings(BaseSettings) que soporte ONYXLOG_URL, DB_PATH, CONFIG_PATH con defaults. Incluir metodos save_to_file() y load_from_file() para config.toml. Implementar resolucion de prioridad: CLI > env > file > default.
- **Archivos**: `src/config.py`
- **Dependencias**: Fase 1 completada
- **Criterios**: Settings() usa defaults; env vars overridean; config.toml se lee/escribe; prioridad funciona correctamente
- **Estimacion**: S

### T2: Implementar tests/test_config.py
- **Descripcion**: Crear tests completos para el modulo de configuracion: defaults, env vars, config file, prioridad, creacion de directorio.
- **Archivos**: `tests/test_config.py`
- **Dependencias**: T1
- **Criterios**: Todos los tests de config pasan; cobertura >90% de config.py
- **Estimacion**: S

### T3: Actualizar README.md con seccion de configuracion
- **Descripcion**: Agregar seccion al README.md explicando la configuracion del servidor (prioridad, env vars, config file).
- **Archivos**: `README.md`
- **Dependencias**: T2
- **Criterios**: README.md incluye documentacion de configuracion
- **Estimacion**: S

### T4: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 2 completada: modulo de configuracion implementado.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T3
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (config.py)
2. T2 (tests — depende de T1)
3. T3 (README — depende de T2)
4. T4 (STATE — depende de T3)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | pydantic-settings puede tener diferencias entre v1 y v2 | Usar pydantic-settings v2 con BaseSettings |
| T1 | config.toml puede no existir en primer uso | Crear directorio y archivo automaticamente |

## Comandos de Verificacion

```bash
pytest tests/test_config.py -v
ruff check src/config.py
```

## Notas de Implementacion

- Settings usa `model_config = SettingsConfigDict(env_prefix="ONYXLOG_")`
- El config file usa formato TOML con seccion `[server]`
- El path `~/.onyxlog/` se expande con `Path.expanduser()`
- No hay dependencias entre config.py y otros modulos internos

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
