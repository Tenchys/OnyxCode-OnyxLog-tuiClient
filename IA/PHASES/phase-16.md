# Fase 16: CLI + Final Polish

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 15 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar CLI con typer para ejecutar el TUI
- Configurar entry point en pyproject.toml
- Alcanzar cobertura de tests >80%
- Limpiar codigo con ruff check y ruff format
- Documentacion final (README.md y STATE.md)

## Entregables

1. CLI con typer: onyxlog-tui --url, --version, --debug
2. Entry point en pyproject.toml
3. Cobertura de tests >80%
4. Codigo limpio (ruff check y ruff format sin errores)
5. README.md y STATE.md actualizados

## Componentes a Implementar

### 1. CLI con typer
- `src/cli.py` con app typer
- Comando principal: `onyxlog-tui` (lanza OnyxLogApp)
- Opciones: `--url` (URL del servidor), `--version` (muestra version), `--debug` (modo debug)
- La opcion --url overridea la configuracion (prioridad CLI > env > file > default)
- --debug habilita logging detallado

### 2. Entry point
- En pyproject.toml: `[project.scripts]` → `onyxlog-tui = "src.cli:app"`
- Verificar que `onyxlog-tui` se ejecuta correctamente tras `pip install -e ".[dev]"`

### 3. Cobertura de tests
- Identificar archivos con cobertura <80%
- Agregar tests para alcanzar >80% en cada archivo
- Ejecutar `pytest tests/ --cov=src --cov-report=term-missing` para verificar

### 4. Limpieza de codigo
- Ejecutar `ruff check src/ tests/` y corregir todos los errores
- Ejecutar `ruff format src/ tests/` y verificar que no hay cambios pendientes

## Tests a Implementar

**Archivos**: `tests/test_cli.py` + tests adicionales segun cobertura

1. Test CLI se ejecuta con opciones por defecto
2. Test CLI con --url overridea la configuracion
3. Test CLI con --version muestra la version
4. Test CLI con --debug habilita logging
5. Tests adicionales para alcanzar >80% de cobertura en cada modulo

## Criterios de Completitud

- [ ] `onyxlog-tui` se ejecuta correctamente
- [ ] `onyxlog-tui --url http://...` overridea la configuracion
- [ ] `onyxlog-tui --version` muestra la version
- [ ] `onyxlog-tui --debug` habilita logging
- [ ] Cobertura de tests >80%
- [ ] `ruff check src/ tests/` sin errores
- [ ] `ruff format src/ tests/ --check` sin cambios pendientes
- [ ] `pytest tests/ -v` pasa sin errores

**Progreso**: 0/6 (0%)

## Tareas

### T1: Implementar src/cli.py con typer
- **Descripcion**: Crear src/cli.py con app typer que lance OnyxLogApp. Opciones: --url (overridea ONYXLOG_URL), --version (muestra version), --debug (habilita logging detallado). La opcion --url se pasa a Settings como prioridad CLI.
- **Archivos**: `src/cli.py`
- **Dependencias**: Fase 15 completada
- **Criterios**: CLI se ejecuta; --url overridea config; --version muestra version; --debug habilita logging
- **Estimacion**: S

### T2: Configurar entry point en pyproject.toml
- **Descripcion**: Agregar `[project.scripts]` → `onyxlog-tui = "src.cli:app"` en pyproject.toml. Verificar que `pip install -e ".[dev]"` instala el comando y `onyxlog-tui` se ejecuta.
- **Archivos**: `pyproject.toml`
- **Dependencias**: T1
- **Criterios**: `onyxlog-tui` se ejecuta correctamente tras instalar
- **Estimacion**: S

### T3: Alcanzar cobertura de tests >80%
- **Descripcion**: Ejecutar `pytest tests/ --cov=src --cov-report=term-missing` para identificar archivos con cobertura <80%. Agregar tests adicionales para cada archivo que necesite mas cobertura. Incluir tests de CLI.
- **Archivos**: `tests/test_cli.py`, `tests/` (archivos adicionales segun necesidad)
- **Dependencias**: T2
- **Criterios**: Cobertura total >80%; cada archivo tiene cobertura >80%
- **Estimacion**: M

### T4: Limpiar codigo con ruff
- **Descripcion**: Ejecutar `ruff check src/ tests/` y corregir todos los errores. Ejecutar `ruff format src/ tests/` y verificar que no hay cambios pendientes. Corregir cualquier issue de linting.
- **Archivos**: `src/`, `tests/`
- **Dependencias**: T3
- **Criterios**: `ruff check src/ tests/` sin errores; `ruff format src/ tests/ --check` sin cambios
- **Estimacion**: S

### T5: Actualizar README.md final
- **Descripcion**: Actualizar README.md con documentacion completa: descripcion, instalacion, configuracion, uso, CLI, screens, desarrollo, tests, contribucion. Incluir badges de cobertura y version.
- **Archivos**: `README.md`
- **Dependencias**: T4
- **Criterios**: README.md es completo y profesional; incluye todas las secciones necesarias
- **Estimacion**: S

### T6: Actualizar estado y seguimiento del proyecto
- **Descripcion**: Actualizar IA/PHASES/overview.md e IA/STATE.md con la Fase 16 completada: proyecto completo, CLI implementado, cobertura >80%, codigo limpio.
- **Archivos**: `IA/PHASES/overview.md`, `IA/STATE.md`
- **Dependencias**: T5
- **Criterios**: overview.md y STATE.md reflejan el estado final del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (CLI con typer)
2. T2 (entry point — depende de T1)
3. T3 (cobertura — depende de T2)
4. T4 (ruff — depende de T3)
5. T5 (README — depende de T4)
6. T6 (STATE — depende de T5)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T3 | Algunos modulos pueden ser dificiles de testear al >80% | Priorizar tests criticos y usar mocks para dependencias externas |
| T4 | ruff puede reportar errores en codigo generado | Corregir todos los errores antes de finalizar |

## Comandos de Verificacion

```bash
pip install -e ".[dev]"
onyxlog-tui --version
onyxlog-tui --url http://localhost:8000
pytest tests/ -v --cov=src --cov-report=term-missing
ruff check src/ tests/
ruff format src/ tests/ --check
```

## Notas de Implementacion

- typer se usa para CLI (consistente con el stack del proyecto)
- La opcion --url se pasa a OnyxLogApp via Settings con prioridad CLI
- --debug habilita logging.basicConfig(level=logging.DEBUG)
- El entry point usa la convencion `[project.scripts]` de pyproject.toml
- La cobertura se mide con pytest-cov

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
