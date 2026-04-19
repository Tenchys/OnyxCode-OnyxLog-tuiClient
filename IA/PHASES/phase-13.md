# Fase 13: Logs Screen

**Estado**: Completada | **Progreso**: 100% | **Fechas**: 2026-04-17
**Dependencias**: Fase 12 | **Ultima actualizacion**: 2026-04-19

## Objetivos

- Implementar la pantalla de visor de logs del TUI
- Crear DataTable con columnas: timestamp, level, app, message
- Implementar coloracion por nivel (ERROR=red, WARN=yellow, INFO=green, DEBUG=dim)
- Crear filtros interactivos (level, app_id, timeframe)
- Agregar key bindings para navegacion rapida

## Entregables

1. `src/screens/logs.py` con LogsScreen y DataTable
2. Coloracion por nivel de log
3. ModalScreen de filtros (level, app_id, timeframe)
4. Key bindings: r→refresh, f→filter, /→search, c→clear
5. Tests con Textual pilot

## Componentes a Implementar

### 1. src/screens/logs.py — LogsScreen
- Hereda de `Screen`
- DataTable con columnas: Timestamp, Level, App, Message
- Carga datos al montar con get_logs() o query_logs()
- Coloracion de filas segun nivel: ERROR=red, WARNING=yellow, INFO=green, DEBUG=dim
- Key bindings: r→refresh, f→filter, /→search, c→clear

### 2. Level coloring
- ERROR → Rich style "bold red"
- WARNING → Rich style "yellow"
- INFO → Rich style "green"
- DEBUG → Rich style "dim"
- CRITICAL → Rich style "bold red reverse"

### 3. FilterModal
- ModalScreen con campos: level (select), app_id (select from list), timeframe (start_time, end_time)
- Boton "Apply" que ejecuta query_logs() con los filtros
- Boton "Clear" que limpia los filtros y recarga get_logs()

## Tests a Implementar

**Archivos**: `tests/test_logs_screen.py`

1. Test LogsScreen se monta correctamente
2. Test DataTable muestra logs al montar
3. Test coloracion por nivel (ERROR=red, WARNING=yellow, INFO=green, DEBUG=dim)
4. Test binding 'r' refresca la tabla
5. Test binding 'f' abre FilterModal
6. Test binding '/' activa busqueda
7. Test binding 'c' limpia filtros
8. Test aplicar filtros funciona
9. Test limpiar filtros funciona
10. Test manejo de error de conexion

## Criterios de Completitud

- [x] LogsScreen se monta y muestra DataTable con logs
- [x] La coloracion por nivel funciona correctamente
- [x] Los filtros funcionan y se aplican a la consulta
- [x] Los key bindings funcionan correctamente
- [x] `pytest tests/test_logs_screen.py -v` pasa sin errores

**Progreso**: 7/7 (100%)

## Tareas

### T1: Implementar src/screens/logs.py con LogsScreen y DataTable
- **Descripcion**: Crear src/screens/logs.py con LogsScreen(Screen) que contenga DataTable con columnas Timestamp, Level, App, Message. Cargar datos al montar con get_logs(). Key bindings: r→refresh, f→filter, /→search, c→clear.
- **Archivos**: `src/screens/logs.py`
- **Dependencias**: Fase 12 completada
- **Criterios**: LogsScreen se monta; DataTable muestra logs; bindings funcionan
- **Estimacion**: M

### T2: Implementar coloracion por nivel de log
- **Descripcion**: Agregar coloracion de filas en DataTable segun el nivel de log: ERROR=bold red, WARNING=yellow, INFO=green, DEBUG=dim, CRITICAL=bold red reverse. Usar Rich styles para la coloracion.
- **Archivos**: `src/screens/logs.py`
- **Dependencias**: T1
- **Criterios**: Cada nivel de log tiene el color correcto; los estilos se aplican a las filas
- **Estimacion**: S

### T3: Implementar FilterModal para filtros interactivos
- **Descripcion**: Crear FilterModal(ModalScreen) con campos: level (Select con opciones DEBUG, INFO, WARNING, ERROR, CRITICAL), app_id (Select con lista de aplicaciones), timeframe (Input para start_time y end_time). Botones Apply y Clear.
- **Archivos**: `src/screens/logs.py`
- **Dependencias**: T2
- **Criterios**: FilterModal se abre y cierra; filtros se aplican correctamente; Clear limpia los filtros
- **Estimacion**: M

### T4: Implementar key bindings y acciones en LogsScreen
- **Descripcion**: Implementar handlers para los bindings: r→refresca tabla, f→abre FilterModal, /→activa busqueda, c→limpia filtros y recarga. La busqueda filtra logs por texto en el mensaje.
- **Archivos**: `src/screens/logs.py`
- **Dependencias**: T3
- **Criterios**: Todos los bindings funcionan; refresh recarga datos; filter abre modal; search filtra; clear limpia
- **Estimacion**: S

### T5: Implementar tests/test_logs_screen.py con Textual pilot
- **Descripcion**: Crear tests para LogsScreen usando Textual pilot. Tests de: montaje, DataTable, coloracion, bindings, filtros, busqueda, manejo de errores.
- **Archivos**: `tests/test_logs_screen.py`
- **Dependencias**: T4
- **Criterios**: Todos los tests pasan; cobertura >80% de logs.py
- **Estimacion**: M

### T6: Actualizar README.md con seccion de Logs Screen
- **Descripcion**: Agregar seccion al README.md documentando LogsScreen, coloracion, filtros y key bindings.
- **Archivos**: `README.md`
- **Dependencias**: T5
- **Criterios**: README.md incluye documentacion de Logs Screen
- **Estimacion**: S

### T7: Actualizar estado y seguimiento del proyecto
- **Descripcion**: Actualizar IA/PHASES/overview.md e IA/STATE.md con la Fase 13 completada: pantalla de logs implementada.
- **Archivos**: `IA/PHASES/overview.md`, `IA/STATE.md`
- **Dependencias**: T6
- **Criterios**: overview.md y STATE.md reflejan el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (LogsScreen + DataTable)
2. T2 (coloracion — depende de T1)
3. T3 (FilterModal — depende de T2)
4. T4 (bindings — depende de T3)
5. T5 (tests — depende de T4)
6. T6 (README — depende de T5)
7. T7 (STATE — depende de T6)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | DataTable puede ser lento con muchos logs | Implementar paginacion y carga bajo demanda |
| T3 | FilterModal puede ser complejo con Select de apps | Cargar lista de apps al abrir el modal |

## Comandos de Verificacion

```bash
pytest tests/test_logs_screen.py -v
ruff check src/screens/logs.py
```

## Notas de Implementacion

- LogsScreen hereda de Screen
- DataTable usa cursor_type="row" para seleccion
- La coloracion se aplica al renderizar cada celda de la columna Level
- FilterModal hereda de ModalScreen
- Las llamadas API usan run_worker() para no bloquear la UI
- La busqueda por texto filtra en el cliente (no en la API)

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
- **2026-04-19**: Fase completada y sincronizada con el estado del proyecto
