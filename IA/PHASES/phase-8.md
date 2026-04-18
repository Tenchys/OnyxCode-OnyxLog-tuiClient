# Fase 8: App Shell (OnyxLogApp)

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 7 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar la aplicacion Textual principal (OnyxLogApp)
- Crear el ciclo de vida de la app: compose, mount (init client + db), shutdown (close client)
- Implementar auto-login si existe una API key valida guardada
- Crear estilos base (styles.tcss)

## Entregables

1. `src/app.py` con OnyxLogApp
2. `src/styles.tcss` con estilos base
3. Auto-login al iniciar si hay API key valida guardada
4. Tests del ciclo de vida de la app

## Componentes a Implementar

### 1. src/app.py — OnyxLogApp
- Clase `OnyxLogApp(App)` con CSS_PATH que apunte a styles.tcss
- `compose()` — retorna Header y contenido inicial (LoginScreen)
- `on_mount()` — inicializa OnyxLogClient y db (init_db)
- `on_shutdown()` — cierra OnyxLogClient
- Propiedad `client` — acceso al OnyxLogClient
- Propiedad `db` — acceso a funciones de db
- Metodo `do_login(api_key, user_data)` — set_api_key + store_key + push_screen(DashboardScreen)

### 2. src/app.py — Auto-login
- En `on_mount()`, despues de init_db, verificar si hay una API key activa
- Si hay key activa: client.set_api_key(key) → health_check() → si OK, push_screen(DashboardScreen)
- Si no hay key o health_check falla: mostrar LoginScreen

### 3. src/styles.tcss — Base styles
- Estilos base para la aplicacion: colores, fuentes, espaciado
- Estilos para pantallas de login y dashboard
- Estilos para DataTable, Input, Button

## Tests a Implementar

**Archivos**: `tests/test_app.py`

1. Test OnyxLogApp se instancia correctamente
2. Test compose retorna Header y LoginScreen
3. Test on_mount inicializa client y db
4. Test on_shutdown cierra client
5. Test auto-login con API key valida (navega a DashboardScreen)
6. Test auto-login sin API key (muestra LoginScreen)
7. Test auto-login con API key invalida (muestra LoginScreen)
8. Test do_login almacena key y navega a DashboardScreen

## Criterios de Completitud

- [ ] OnyxLogApp se instancia y monta correctamente
- [ ] El ciclo de vida (mount, shutdown) funciona
- [ ] Auto-login funciona con API key valida
- [ ] Sin API key, muestra LoginScreen
- [ ] API key invalida, muestra LoginScreen
- [ ] `pytest tests/test_app.py -v` pasa sin errores

**Progreso**: 0/6 (0%)

## Tareas

### T1: Implementar src/app.py con OnyxLogApp
- **Descripcion**: Crear src/app.py con OnyxLogApp(App) que tenga compose() (Header + LoginScreen), on_mount() (init OnyxLogClient + init_db), on_shutdown() (close client), propiedades client y db, y metodo do_login(api_key, user_data).
- **Archivos**: `src/app.py`
- **Dependencias**: Fase 7 completada
- **Criterios**: OnyxLogApp se instancia; compose retorna Header + LoginScreen; on_mount inicializa client y db; on_shutdown cierra client
- **Estimacion**: M

### T2: Crear src/styles.tcss con estilos base
- **Descripcion**: Crear src/styles.tcss con estilos base para la aplicacion: colores del tema, fuentes, espaciado, estilos para pantallas, DataTable, Input, Button. Usar variables CSS de Textual.
- **Archivos**: `src/styles.tcss`
- **Dependencias**: T1
- **Criterios**: styles.tcss existe y contiene estilos base; la app se renderiza correctamente
- **Estimacion**: S

### T3: Implementar auto-login en OnyxLogApp
- **Descripcion**: Implementar logica de auto-login en on_mount(): verificar si hay API key activa en SQLite → si hay, set_api_key() + health_check() → si OK, push_screen(DashboardScreen) → si no hay key o falla, mostrar LoginScreen.
- **Archivos**: `src/app.py`
- **Dependencias**: T2
- **Criterios**: Auto-login funciona con key valida; sin key muestra LoginScreen; key invalida muestra LoginScreen
- **Estimacion**: S

### T4: Implementar tests/test_app.py con Textual pilot
- **Descripcion**: Crear tests para OnyxLogApp usando Textual pilot. Tests de: instanciacion, compose, mount/shutdown, auto-login con key valida, auto-login sin key, auto-login con key invalida, do_login.
- **Archivos**: `tests/test_app.py`
- **Dependencias**: T3
- **Criterios**: Todos los tests pasan; cobertura >80% de app.py
- **Estimacion**: M

### T5: Actualizar README.md con seccion de app shell
- **Descripcion**: Agregar seccion al README.md documentando OnyxLogApp, el ciclo de vida y el auto-login.
- **Archivos**: `README.md`
- **Dependencias**: T4
- **Criterios**: README.md incluye documentacion de la app
- **Estimacion**: S

### T6: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 8 completada: app shell implementado.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T5
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (OnyxLogApp)
2. T2 (styles.tcss — depende de T1)
3. T3 (auto-login — depende de T2)
4. T4 (tests — depende de T3)
5. T5 (README — depende de T4)
6. T6 (STATE — depende de T5)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | Import circular entre app.py y screens/ | Usar import diferido en compose() |
| T3 | health_check puede fallar si el servidor no esta disponible | Manejar error y mostrar LoginScreen |

## Comandos de Verificacion

```bash
pytest tests/test_app.py -v
ruff check src/app.py
```

## Notas de Implementacion

- OnyxLogApp hereda de textual.app.App
- CSS_PATH apunta a styles.tcss
- Los imports de screens se hacen de forma diferida para evitar import circular
- on_mount() es async y usa run_worker() para llamadas async
- on_shutdown() cierra el httpx.AsyncClient

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
