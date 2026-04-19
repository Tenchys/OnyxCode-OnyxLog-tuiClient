# Fase 15: SSE Streaming (Real-time Logs)

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: 2026-04-17
**Dependencias**: Fase 14 | **Ultima actualizacion**: 2026-04-17

## Objetivos

- Implementar streaming SSE para recibir logs en tiempo real
- Crear funcion stream_logs() en el modulo de API
- Implementar Worker en LogsScreen para consumir el stream
- Agregar toggle para activar/desactivar streaming
- Implementar reconexion automatica

## Entregables

1. `src/api/logs.py` — stream_logs() con httpx SSE
2. Worker en LogsScreen para consumir stream y actualizar DataTable
3. Toggle de stream on/off
4. Reconexion automatica
5. Tests con mock SSE

## Componentes a Implementar

### 1. src/api/logs.py — stream_logs()
- `async stream_logs(client) -> AsyncIterator[LogRead]` — GET /api/v1/logs/stream (SSE)
- Usa httpx para conectar al endpoint SSE
- Parsea eventos SSE (event: log, data: JSON)
- Retorna AsyncIterator que yield LogRead por cada evento
- Maneja reconexion automatica con backoff exponencial

### 2. LogsScreen — StreamWorker
- Worker de Textual que consume stream_logs() y actualiza la DataTable
- Agrega nuevas filas al inicio de la tabla (logs mas recientes primero)
- Limita la tabla a N filas (configurable, default 1000)
- Toggle de stream con binding 't' (stream on/off)

### 3. Reconexion automatica
- Si la conexion SSE se pierde, intentar reconectar con backoff exponencial
- Mostrar indicador de estado: "Streaming" (verde), "Reconnecting..." (amarillo), "Disconnected" (rojo)
- Maximo 5 intentos de reconexion antes de mostrar error

## Tests a Implementar

**Archivos**: `tests/test_streaming.py`

1. Test stream_logs() recibe eventos SSE y yield LogRead
2. Test stream_logs() maneja eventos vacios
3. Test stream_logs() maneja errores de conexion
4. Test stream_logs() reconecta automaticamente
5. Test StreamWorker agrega filas a la DataTable
6. Test StreamWorker limita la tabla a N filas
7. Test toggle stream on/off funciona
8. Test indicador de estado cambia correctamente

## Criterios de Completitud

- [ ] stream_logs() funciona con SSE
- [ ] StreamWorker actualiza la DataTable en tiempo real
- [ ] Toggle de stream funciona
- [ ] Reconexion automatica funciona
- [ ] `pytest tests/test_streaming.py -v` pasa sin errores

**Progreso**: 0/6 (0%)

## Tareas

### T1: Implementar stream_logs() en src/api/logs.py
- **Descripcion**: Agregar funcion async stream_logs(client) -> AsyncIterator[LogRead] a src/api/logs.py. Conecta a GET /api/v1/logs/stream usando httpx SSE. Parsea eventos SSE y yield LogRead por cada evento. Maneja reconexion con backoff exponencial (max 5 intentos).
- **Archivos**: `src/api/logs.py`
- **Dependencias**: Fase 14 completada
- **Criterios**: stream_logs() recibe eventos SSE; yield LogRead; maneja errores; reconecta automaticamente
- **Estimacion**: M

### T2: Implementar StreamWorker en LogsScreen
- **Descripcion**: Agregar StreamWorker a LogsScreen que consuma stream_logs() y actualice la DataTable. Agregar nuevas filas al inicio. Limitar la tabla a 1000 filas. Mostrar indicador de estado: "Streaming", "Reconnecting...", "Disconnected".
- **Archivos**: `src/screens/logs.py`
- **Dependencias**: T1
- **Criterios**: StreamWorker consume stream; actualiza DataTable; indica estado; limita filas
- **Estimacion**: M

### T3: Implementar toggle de stream y reconexion
- **Descripcion**: Agregar binding 't' para toggle stream on/off. Al activar, iniciar StreamWorker. Al desactivar, detener StreamWorker. Reconexion automatica con backoff exponencial (1s, 2s, 4s, 8s, 16s). Maximo 5 intentos.
- **Archivos**: `src/screens/logs.py`
- **Dependencias**: T2
- **Criterios**: Toggle funciona; stream se detiene y reanuda; reconexion funciona con backoff
- **Estimacion**: S

### T4: Implementar tests/test_streaming.py con mock SSE
- **Descripcion**: Crear tests para stream_logs() y StreamWorker usando mock SSE. Tests de: recepcion de eventos, eventos vacios, errores de conexion, reconexion, StreamWorker, toggle, indicador de estado.
- **Archivos**: `tests/test_streaming.py`
- **Dependencias**: T3
- **Criterios**: Todos los tests pasan; cobertura >80% de stream_logs() y StreamWorker
- **Estimacion**: M

### T5: Actualizar README.md con seccion de streaming
- **Descripcion**: Agregar seccion al README.md documentando el streaming SSE, StreamWorker, toggle y reconexion.
- **Archivos**: `README.md`
- **Dependencias**: T4
- **Criterios**: README.md incluye documentacion de streaming
- **Estimacion**: S

### T6: Actualizar estado y seguimiento del proyecto
- **Descripcion**: Actualizar IA/PHASES/overview.md e IA/STATE.md con la Fase 15 completada: streaming SSE implementado.
- **Archivos**: `IA/PHASES/overview.md`, `IA/STATE.md`
- **Dependencias**: T5
- **Criterios**: overview.md y STATE.md reflejan el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 (stream_logs)
2. T2 (StreamWorker — depende de T1)
3. T3 (toggle + reconexion — depende de T2)
4. T4 (tests — depende de T3)
5. T5 (README — depende de T4)
6. T6 (STATE — depende de T5)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T1 | httpx puede no soportar SSE nativamente | Usar httpx con stream=True y parsear SSE manualmente |
| T2 | StreamWorker puede bloquear la UI si no se usa correctamente | Usar run_worker() de Textual para ejecucion en background |
| T3 | Reconexion puede causar loop infinito | Limitar a 5 intentos con backoff exponencial |

## Comandos de Verificacion

```bash
pytest tests/test_streaming.py -v
ruff check src/api/logs.py src/screens/logs.py
```

## Notas de Implementacion

- stream_logs() usa httpx.AsyncClient.stream("GET", "/api/v1/logs/stream")
- SSE se parsea manualmente: cada evento tiene "event: log" y "data: {json}"
- StreamWorker hereda de textual.workers.Worker
- El toggle de stream usa un flag booleano en LogsScreen
- La reconexion usa asyncio.sleep() con backoff exponencial (no time.sleep())

## Historial

- **2026-04-17**: Fase creada, planificacion inicial completada
