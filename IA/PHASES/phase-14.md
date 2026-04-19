# Fase 14: Settings + Health Check

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 11, Fase 13 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar la pantalla de configuracion del TUI
- Crear indicador visual de health check (conectado/desconectado)
- Mostrar lista de API keys guardadas con opcion de eliminar
- Implementar flujo de logout (limpiar key + desactivar + ir a login)

## Entregables

1. `src/screens/settings.py` con SettingsScreen
2. Indicador visual de health check
3. Lista de API keys guardadas con opcion de eliminar
4. Flujo de logout completo
5. Tests con Textual pilot

## Componentes a Implementar

### 1. src/screens/settings.py — SettingsScreen
- Hereda de `Screen`
- Seccion de configuracion del servidor: URL actual, campo para cambiar URL, boton "Save"
- Seccion de health check: indicador visual (verde=conectado, rojo=desconectado)
- Seccion de API keys guardadas: lista con nombre, tipo, fecha, boton eliminar
- Seccion de cuenta: boton "Logout"

### 2. Health check indicator
- Al montar, llamar a health_check() del client
- Si responde OK: mostrar indicador verde "Connected"
- Si falla: mostrar indicador rojo "Disconnected"
- Boton "Check" para re-verificar

### 3. API keys list
- Cargar lista de keys con db.list_keys()
- Mostrar: nombre, tipo (user/application), fecha de creacion
- Boton eliminar al lado de cada key → db.delete_key()
- Al eliminar la key activa, hacer logout

### 4. Logout flow
- Boton "Logout" que ejecuta: client.clear_api_key() → db.deactivate_key() → app.pop_screen() hasta LoginScreen
- Confirmacion antes de logout

## Tests a Implementar

**Archivos**: `tests/test_settings_screen.py`

1. Test SettingsScreen se monta correctamente
2. Test seccion de URL del servidor se muestra
3. Test cambiar URL y guardar funciona
4. Test health check indicator muestra "Connected" cuando el servidor responde
5. Test health check indicator muestra "Disconnected" cuando el servidor no responde
6. Test lista de API keys se muestra
7. Test eliminar API key funciona
8. Test logout limpia key y navega a LoginScreen
9. Test logout con confirmacion

## Criterios de Completitud

- [ ] SettingsScreen se monta y muestra todas las secciones
- [ ] El indicador de health check funciona correctamente
- [ ] La lista de API keys se muestra y permite eliminar
- [ ] El flujo de logout funciona correctamente
- [ ] `pytest tests/test_settings_screen.py -v` pasa sin errores

**Progreso**: 0/7 (0%)

## Tareas

### T1: Implementar src/screens/settings.py con SettingsScreen
- **Descripcion**: Crear src/screens/settings.py con SettingsScreen(Screen) que contenga secciones: configuracion del servidor (URL actual, campo para cambiar, boton Save), health check (indicador visual), API keys guardadas (lista con boton eliminar), cuenta (boton Logout).
- **Archivos**: `src/screens/settings.py`
- **Dependencias**: Fase 11 y Fase 13 completadas
- **Criterios**: SettingsScreen se monta; todas las secciones se muestran; layout es correcto
- **Estimacion**: M

### T2: Implementar indicador visual de health check
- **Descripcion**: Agregar indicador de health check que llame a client.health_check() al montar. Mostrar "Connected" en verde si OK, "Disconnected" en rojo si falla. Boton "Check" para re-verificar. Usar run_worker() para la llamada async.
- **Archivos**: `src/screens/settings.py`
- **Dependencias**: T1
- **Criterios**: Indicador muestra estado correcto; boton Check funciona; colores verde/rojo se aplican
- **Estimacion**: S

### T3: Implementar lista de API keys guardadas
- **Descripcion**: Agregar seccion que muestre las API keys guardadas con db.list_keys(). Mostrar nombre, tipo, fecha de creacion. Boton eliminar al lado de cada key que llame a db.delete_key(). Si se elimina la key activa, hacer logout.
- **Archivos**: `src/screens/settings.py`
- **Dependencias**: T2
- **Criterios**: Lista se carga al montar; eliminar key funciona; si se elimina la key activa se hace logout
- **Estimacion**: S

### T4: Implementar flujo de logout
- **Descripcion**: Implementar boton "Logout" que ejecute: client.clear_api_key() → db.deactivate_key() → app.pop_screen() hasta LoginScreen. Agregar confirmacion antes de logout con dialogo modal.
- **Archivos**: `src/screens/settings.py`
- **Dependencias**: T3
- **Criterios**: Logout limpia la key; desactiva en DB; navega a LoginScreen; tiene confirmacion
- **Estimacion**: S

### T5: Implementar tests/test_settings_screen.py con Textual pilot
- **Descripcion**: Crear tests para SettingsScreen usando Textual pilot. Tests de: montaje, secciones, health check, lista de keys, eliminar key, logout, confirmacion.
- **Archivos**: `tests/test_settings_screen.py`
- **Dependencias**: T4
- **Criterios**: Todos los tests pasan; cobertura >80% de settings.py
- **Estimacion**: M

### T6: Actualizar README.md con seccion de Settings
- **Descripcion**: Agregar seccion al README.md documentando SettingsScreen, health check, API keys y logout.
- **Archivos**: `README.md`
- **Dependencias**: T5
- **Criterios**: README.md incluye documentacion de Settings Screen
- **Estimacion**: S

### T7: Actualizar estado y seguimiento del proyecto
- **Descripcion**: Actualizar IA/PHASES/overview.md e IA/STATE.md con la Fase 14 completada: pantalla de settings implementada.
- **Archivos**: `IA/PHASES/overview.md`, `IA/STATE.md`
- **Dependencias**: T6
- **Criterios**: overview.md y STATE.md reflejan el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (SettingsScreen UI)
2. T2 (health check — depende de T1)
3. T3 (API keys list — depende de T2)
4. T4 (logout — depende de T3)
5. T5 (tests — depende de T4)
6. T6 (README — depende de T5)
7. T7 (STATE — depende de T6)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T2 | health_check puede tardar si el servidor no responde | Usar timeout corto (5s) y mostrar "Checking..." mientras espera |
| T3 | Eliminar la key activa puede dejar la app en estado inconsistente | Forzar logout si se elimina la key activa |

## Comandos de Verificacion

```bash
pytest tests/test_settings_screen.py -v
ruff check src/screens/settings.py
```

## Notas de Implementacion

- SettingsScreen hereda de Screen
- El indicador de health check usa Rich para colorear (green/red)
- La lista de API keys usa DataTable o ListView
- Logout usa app.install_screen() para volver a LoginScreen
- La confirmacion de logout usa un dialogo modal

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
