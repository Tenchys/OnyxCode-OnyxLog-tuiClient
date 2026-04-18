# Fase 7: Login Screen

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 6 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar la pantalla de login/registro del TUI
- Crear formulario con campos username, email (opcional), password
- Integrar con auth.register() y auth.login()
- Implementar flujo completo: login → set_api_key → store_key → push_screen(DashboardScreen)
- Manejar errores de autenticacion en la UI

## Entregables

1. `src/screens/login.py` con LoginScreen
2. Flujo de login completo integrado con API client y DB local
3. Manejo de errores en la UI (INVALID_CREDENTIALS, CONNECTION_ERROR, DUPLICATE_ENTRY)
4. Tests con Textual pilot

## Componentes a Implementar

### 1. src/screens/login.py — LoginScreen
- Hereda de `Screen`
- Formulario con campos: username (Input), email (Input, opcional), password (Input, password=True)
- Botones: "Login" y "Register"
- Binding: enter → submit
- Layout centrado con Header y Footer

### 2. Login flow
- Al hacer click en "Login": llama a auth.login(client, username, password)
- Al hacer click en "Register": llama a auth.register(client, username, email, password)
- En exito: client.set_api_key(api_key) → db.store_key(...) → app.push_screen(DashboardScreen)
- En error: muestra notificacion con el mensaje de error

### 3. Error handling
- INVALID_CREDENTIALS → "Invalid username or password"
- DUPLICATE_ENTRY → "Username or email already exists"
- CONNECTION_ERROR → "Cannot connect to server. Check URL and try again."
- VALIDATION_ERROR → "Please check the form fields."
- TIMEOUT → "Server is taking too long to respond."

## Tests a Implementar

**Archivos**: `tests/test_login_screen.py`

1. Test LoginScreen se monta correctamente
2. Test formulario tiene campos username, email, password
3. Test boton Login existe
4. Test boton Register existe
5. Test login exitoso con mock (set_api_key llamado, store_key llamado, push_screen llamado)
6. Test login con credenciales invalidas (muestra error)
7. Test registro exitoso con mock
8. Test registro con username duplicado (muestra error)
9. Test conexion fallida (muestra error de conexion)

## Criterios de Completitud

- [ ] LoginScreen se monta y muestra el formulario
- [ ] Login exitoso navega al Dashboard
- [ ] Registro exitoso navega al Dashboard
- [ ] Errores se muestran como notificaciones
- [ ] API key se almacena en SQLite tras login/registro exitoso
- [ ] `pytest tests/test_login_screen.py -v` pasa sin errores

**Progreso**: 0/6 (0%)

## Tareas

### T1: Implementar src/screens/login.py con LoginScreen
- **Descripcion**: Crear src/screens/login.py con LoginScreen(Screen) que contenga formulario con campos username, email (opcional), password y botones Login/Register. Layout centrado con Header y Footer. Binding enter → submit.
- **Archivos**: `src/screens/login.py`
- **Dependencias**: Fase 6 completada
- **Criterios**: LoginScreen se monta; formulario tiene todos los campos; botones Login y Register existen
- **Estimacion**: M

### T2: Implementar flujo de login/registro en LoginScreen
- **Descripcion**: Implementar los handlers de los botones Login y Register que llamen a auth.login() y auth.register() respectivamente. En exito: client.set_api_key() → db.store_key() → app.push_screen(DashboardScreen). En error: mostrar notificacion con mensaje apropiado.
- **Archivos**: `src/screens/login.py`
- **Dependencias**: T1
- **Criterios**: Login exitoso navega al Dashboard; registro exitoso navega al Dashboard; API key se almacena en SQLite
- **Estimacion**: S

### T3: Implementar manejo de errores en LoginScreen
- **Descripcion**: Implementar mapeo de ApiClientError a mensajes de usuario amigables: INVALID_CREDENTIALS, DUPLICATE_ENTRY, CONNECTION_ERROR, VALIDATION_ERROR, TIMEOUT. Mostrar como notificaciones con severity="error".
- **Archivos**: `src/screens/login.py`
- **Dependencias**: T2
- **Criterios**: Cada tipo de error muestra el mensaje correcto; las notificaciones usan severity="error"
- **Estimacion**: S

### T4: Implementar tests/test_login_screen.py con Textual pilot
- **Descripcion**: Crear tests para LoginScreen usando Textual pilot. Tests de: montaje, formulario, login exitoso, login fallido, registro exitoso, registro fallido, error de conexion. Usar mock para auth.login y auth.register.
- **Archivos**: `tests/test_login_screen.py`
- **Dependencias**: T3
- **Criterios**: Todos los tests pasan; cobertura >80% de login.py
- **Estimacion**: M

### T5: Actualizar README.md con seccion de login
- **Descripcion**: Agregar seccion al README.md documentando el flujo de login/registro y la pantalla LoginScreen.
- **Archivos**: `README.md`
- **Dependencias**: T4
- **Criterios**: README.md incluye documentacion del flujo de login
- **Estimacion**: S

### T6: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la Fase 7 completada: pantalla de login implementada.
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T5
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (LoginScreen UI)
2. T2 (flujo de login — depende de T1)
3. T3 (manejo de errores — depende de T2)
4. T4 (tests — depende de T3)
5. T5 (README — depende de T4)
6. T6 (STATE — depende de T5)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | Textual Screen API puede cambiar entre versiones | Fijar version de textual en pyproject.toml |
| T4 | Textual pilot puede ser dificil de configurar con mocks | Crear helper fixture para app con client mockeado |

## Comandos de Verificacion

```bash
pytest tests/test_login_screen.py -v
ruff check src/screens/login.py
```

## Notas de Implementacion

- LoginScreen hereda de Screen (no de App)
- Los handlers de botones usan run_worker() para llamadas async
- Las notificaciones usan self.notify(message, severity="error")
- DashboardScreen se importa de forma diferida para evitar import circular
- El campo email es opcional (solo requerido para registro)

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
