# Fase 1: Project Scaffolding

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Ninguna | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Establecer la estructura base del proyecto OnyxLog TUI Client
- Configurar pyproject.toml con todas las dependencias necesarias
- Crear la estructura de directorios src/ con paquetes Python
- Configurar ruff para linting y formateo
- Crear infraestructura de tests funcional (conftest.py con fixtures)
- Verificar que pytest, ruff check y ruff format pasan sin errores

## Entregables

1. `pyproject.toml` con dependencias y configuracion de ruff
2. Estructura de directorios `src/` con `__init__.py` en cada paquete
3. `tests/conftest.py` con fixtures base
4. `tests/test_smoke.py` que verifica que los imports funcionan
5. `IA/PHASES/overview.md` y `IA/STATE.md` iniciales

## Componentes a Implementar

### 1. pyproject.toml
- Metadata del proyecto (name, version, description, requires-python)
- Dependencias: textual, rich, httpx, aiosqlite, pydantic, pydantic-settings, typer
- Dev dependencies: pytest, pytest-asyncio, pytest-cov, ruff
- Configuracion de ruff (line-length 88, target Python 3.11+)
- Entry point: onyxlog-tui = "src.app:main"

### 2. Estructura de directorios
- `src/__init__.py`
- `src/api/__init__.py`
- `src/models/__init__.py`
- `src/screens/__init__.py`
- `tests/__init__.py`

### 3. Infraestructura de tests
- `tests/conftest.py` con fixtures base (tmp_path, mock settings)
- `tests/test_smoke.py` con test de import basico

## Tests a Implementar

**Archivos**: `tests/test_smoke.py`

1. Test que `import src` funciona
2. Test que `import src.api` funciona
3. Test que `import src.models` funciona
4. Test que `import src.screens` funciona
5. Test que pytest se ejecuta sin errores

## Criterios de Completitud

- [ ] `pip install -e ".[dev]"` instala todas las dependencias
- [ ] `pytest tests/ -v` pasa sin errores
- [ ] `ruff check src/ tests/` no reporta errores
- [ ] `ruff format src/ tests/` formatea sin cambios
- [ ] Todos los paquetes son importables

**Progreso**: 0/6 (0%)

## Tareas

### T1: Crear pyproject.toml con dependencias y configuracion ruff
- **Descripcion**: Crear pyproject.toml con metadata del proyecto, dependencias de produccion (textual, rich, httpx, aiosqlite, pydantic, pydantic-settings, typer) y desarrollo (pytest, pytest-asyncio, pytest-cov, ruff). Incluir configuracion de ruff con line-length=88 y target-version="py311".
- **Archivos**: `pyproject.toml`
- **Dependencias**: Ninguna
- **Criterios**: `pip install -e ".[dev]"` instala todas las dependencias; `ruff check --select I,F` pasa sin errores
- **Estimacion**: S

### T2: Crear estructura de directorios src/ con __init__.py
- **Descripcion**: Crear la estructura de directorios del proyecto con archivos __init__.py vacios en cada paquete: src/, src/api/, src/models/, src/screens/. Tambien crear tests/ con __init__.py.
- **Archivos**: `src/__init__.py`, `src/api/__init__.py`, `src/models/__init__.py`, `src/screens/__init__.py`, `tests/__init__.py`
- **Dependencias**: Ninguna
- **Criterios**: Todos los paquetes son importables (`import src.api`, `import src.models`, `import src.screens`)
- **Estimacion**: S

### T3: Crear tests/conftest.py con fixtures base y test_smoke.py
- **Descripcion**: Crear conftest.py con fixtures base (tmp_path para SQLite temporal, mock Settings) y test_smoke.py con tests de import basico que verifiquen que la estructura de paquetes funciona.
- **Archivos**: `tests/conftest.py`, `tests/test_smoke.py`
- **Dependencias**: T1, T2
- **Criterios**: `pytest tests/ -v` pasa sin errores; los 5 tests de smoke pasan
- **Estimacion**: S

### T4: Crear IA/PHASES/overview.md y IA/STATE.md iniciales
- **Descripcion**: Crear los archivos de seguimiento del proyecto: overview.md con la tabla de fases y STATE.md con el estado inicial del proyecto (Fase 1 como actual, sin componentes implementados).
- **Archivos**: `IA/PHASES/overview.md`, `IA/STATE.md`
- **Dependencias**: Ninguna
- **Criterios**: Los archivos existen y contienen la estructura base correcta
- **Estimacion**: S

### T5: Actualizar README.md con instrucciones de setup
- **Descripcion**: Crear README.md con descripcion del proyecto, instrucciones de instalacion (`pip install -e ".[dev]"`), comandos de ejecucion (`onyxlog-tui`), tests (`pytest tests/ -v`) y lint (`ruff check src/ tests/`).
- **Archivos**: `README.md`
- **Dependencias**: T1
- **Criterios**: README.md existe y contiene instrucciones de setup, tests y lint
- **Estimacion**: S

### T6: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md para reflejar que la Fase 1 esta completada: estructura de proyecto creada, dependencias instaladas, tests pasando.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T5
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1, T2, T4 (paralelo — sin dependencias entre si)
2. T3 (depende de T1 y T2)
3. T5 (depende de T1)
4. T6 (depende de T5)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | Versiones incompatibles de dependencias | Fijar versiones compatibles en pyproject.toml |
| T3 | Fixtures pueden necesitar ajustes al agregar modulos reales | Mantener fixtures minimas y extensibles |

## Comandos de Verificacion

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check src/ tests/
ruff format src/ tests/ --check
```

## Notas de Implementacion

- Este es un proyecto greenfield: no existe codigo fuente previo
- La estructura sigue la arquitectura definida en AGENTS.md
- Se usa `src/` como layout (no `onyxlog_tui/` flat) para facilitar imports
- Las dependencias de desarrollo van en `[project.optional-dependencies]` con grupo `dev`

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
