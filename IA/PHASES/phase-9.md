# Fase 9: Dashboard Screen

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 8 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar la pantalla principal del TUI (DashboardScreen)
- Crear menu de navegacion con opciones: Applications, Logs, Settings
- Implementar key bindings para navegacion rapida
- Mostrar resumen de estadisticas (stats/overview)
- Proveer punto de entrada a todas las funcionalidades del TUI

## Entregables

1. `src/screens/dashboard.py` con DashboardScreen
2. Key bindings: a→apps, l→logs, s→settings, q→quit, escape→back
3. Stats overview con llamada a /api/v1/stats/overview
4. Tests de navegacion con pilot

## Componentes a Implementar

### 1. src/screens/dashboard.py — DashboardScreen
- Hereda de `Screen`
- Menu de navegacion con opciones: Applications, Logs, Settings
- Cada opcion navega a la pantalla correspondiente via app.push_screen()
- Stats overview mostrando: total de logs, total de aplicaciones, aplicaciones activas, logs recientes (24h)

### 2. Key bindings
- `a` → navegar a ApplicationsScreen
- `l` → navegar a LogsScreen
- `s` → navegar a SettingsScreen
- `q` → salir de la app (app.exit())
- `escape` → volver a la pantalla anterior (app.pop_screen())

### 3. Stats overview
- En on_mount(), llamar a GET /api/v1/stats/overview con la API key configurada
- Mostrar estadisticas en formato de tabla o resumen
- Manejar errores de conexion (mostrar mensaje "Unable to load stats")

## Tests a Implementar

**Archivos**: `tests/test_dashboard_screen.py`

1. Test DashboardScreen se monta correctamente
2. Test menu muestra opciones Applications, Logs, Settings
3. Test binding 'a' navega a ApplicationsScreen
4. Test binding 'l' navega a LogsScreen
5. Test binding 's' navega a SettingsScreen
6. Test binding 'q' sale de la app
7. Test stats overview se carga al montar
8. Test stats overview muestra error si falla la conexion

## Criterios de Completitud

- [ ] DashboardScreen se monta y muestra el menu
- [ ] Los key bindings navegan a las pantallas correctas
- [ ] Stats overview se carga y muestra
- [ ] Errores de conexion se manejan correctamente
- [ ] `pytest tests/test_dashboard_screen.py -v` pasa sin errores

**Progreso**: 0/6 (0%)

## Tareas

### T1: Implementar src/screens/dashboard.py con DashboardScreen y menu
- **Descripcion**: Crear src/screens/dashboard.py con DashboardScreen(Screen) que muestre menu de navegacion con opciones Applications, Logs, Settings. Cada opcion navega a la pantalla correspondiente. Layout con Header, contenido centrado y Footer.
- **Archivos**: `src/screens/dashboard.py`
- **Dependencias**: Fase 8 completada
- **Criterios**: DashboardScreen se monta; menu muestra las 3 opciones; navegacion funciona
- **Estimacion**: M

### T2: Implementar key bindings en DashboardScreen
- **Descripcion**: Agregar BINDINGS a DashboardScreen: a→apps, l→logs, s→settings, q→quit, escape→back. Cada binding ejecuta app.push_screen() o app.exit() segun corresponda.
- **Archivos**: `src/screens/dashboard.py`
- **Dependencias**: T1
- **Criterios**: Todos los bindings funcionan correctamente; navegan a las pantallas correctas
- **Estimacion**: S

### T3: Implementar stats overview en DashboardScreen
- **Descripcion**: Agregar seccion de stats overview que llame a GET /api/v1/stats/overview al montar la pantalla. Mostrar: total_logs, total_applications, active_applications, recent_logs_24h. Manejar errores mostrando mensaje "Unable to load stats".
- **Archivos**: `src/screens/dashboard.py`
- **Dependencias**: T2
- **Criterios**: Stats se cargan y muestran al montar; errores se manejan con mensaje apropiado
- **Estimacion**: M

### T4: Implementar tests/test_dashboard_screen.py con Textual pilot
- **Descripcion**: Crear tests para DashboardScreen usando Textual pilot. Tests de: montaje, menu, bindings (a, l, s, q, escape), stats overview, manejo de errores.
- **Archivos**: `tests/test_dashboard_screen.py`
- **Dependencias**: T3
- **Criterios**: Todos los tests pasan; cobertura >80% de dashboard.py
- **Estimacion**: M

### T5: Actualizar README.md con seccion de dashboard
- **Descripcion**: Agregar seccion al README.md documentando DashboardScreen, key bindings y stats overview.
- **Archivos**: `README.md`
- **Dependencias**: T4
- **Criterios**: README.md incluye documentacion del dashboard
- **Estimacion**: S

### T6: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 9 completada: dashboard implementado.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T5
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (DashboardScreen UI)
2. T2 (bindings — depende de T1)
3. T3 (stats — depende de T2)
4. T4 (tests — depende de T3)
5. T5 (README — depende de T4)
6. T6 (STATE — depende de T5)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T3 | El endpoint stats/overview puede no estar disponible | Mostrar mensaje de error y permitir continuar |
| T4 | Textual pilot puede tener limitaciones para testear navegacion | Usar mocks para las pantallas destino |

## Comandos de Verificacion

```bash
pytest tests/test_dashboard_screen.py -v
ruff check src/screens/dashboard.py
```

## Notas de Implementacion

- DashboardScreen hereda de Screen
- Los imports de screens se hacen de forma diferida
- Stats overview usa run_worker() para llamada async
- Los bindings se definen en BINDINGS class attribute
- El menu puede usar OptionList o botones con Rich

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
