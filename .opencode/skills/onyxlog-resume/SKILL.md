---
name: onyxlog-resume
description: Skill para retomar la implementacion de OnyxLog. Lee el estado actual y carga el contexto necesario para continuar trabajando.
metadata:
  audience: developers
  workflow: onyxlog
---

## Flujo para Retomar Trabajo

Cuando se necesita retomar o continuar la implementacion de OnyxLog, seguir estos pasos en orden:

### 1. Leer Estado Actual

Leer `IA/STATE.md` para determinar:
- Que fase esta activa
- Cual es la siguiente tarea
- Metricas actuales (cobertura, tests, migraciones)

### 2. Cargar Contexto de la Fase

Leer `IA/PHASES/phase-N.md` donde N es la fase actual:
- Si la fase esta "En progreso": leer la fase actual
- Si la fase esta "Pendiente": leer la fase que se va a iniciar
- Si la fase esta "Completada": no es necesario cargarla

### 3. Cargar Contexto Tecnico (Solo si se necesita)

Leer archivos de `IA/CONTEXT/` segun la tarea:
- `architecture.md` — Estructura del proyecto, stack, flujo de datos
- `models-reference.md` — Modelos SQLAlchemy, relaciones, indices
- `endpoints-reference.md` — Endpoints de la API, rutas, autenticacion
- `schemas-reference.md` — Schemas Pydantic, validaciones, ejemplos
- `config-reference.md` — Variables de entorno, dependencias, comandos
- `workflows-reference.md` — Flujos de trabajo, roles, autenticacion

### 4. Cargar Skills Especificos (Solo si se necesita)

Cargar skills de OnyxLog segun la tarea:
- `onyxlog-coding` — Al implementar codigo nuevo
- `onyxlog-api-patterns` — Al crear o modificar endpoints
- `onyxlog-data-layer` — Al crear o modificar modelos/schemas
- `onyxlog-testing` — Al escribir tests
- `onyxlog-commit` — Al hacer commits
- `onyxlog-review` — Al revisar codigo

### 5. Verificar Estado del Codigo

Antes de implementar, verificar:
- `git status` para ver cambios pendientes
- `git log --oneline -5` para ver ultimos commits
- `pytest tests/ -v --tb=short` para ver si los tests pasan

### 6. Al Completar una Tarea o Fase

Actualizar `IA/STATE.md` con:
- Nueva fase actual si se completo una
- Nuevo progreso
- Nuevas metricas
- Nueva siguiente tarea

### Estructura de Archivos de Contexto

```
IA/
├── STATE.md                    # Estado actual (SIEMPRE se lee)
├── PHASES/
│   ├── overview.md             # Tabla de seguimiento y reglas
│   ├── phase-1.md              # Setup Inicial (completada)
│   ├── phase-2.md              # Auth y API Basica (completada)
│   ├── phase-3.md              # Busqueda Avanzada (completada)
│   ├── phase-4.md              # Produccion (pendiente)
│   └── phase-5.md              # Funcionalidades Avanzadas (bloqueada)
└── CONTEXT/
    ├── architecture.md          # Stack, estructura, flujo de datos
    ├── models-reference.md      # Modelos SQLAlchemy
    ├── endpoints-reference.md   # Endpoints de la API
    ├── schemas-reference.md      # Schemas Pydantic
    ├── config-reference.md      # Variables de entorno y comandos
    └── workflows-reference.md   # Flujos de trabajo y roles
```

### Regla Importante

NUNCA cargar todos los archivos de contexto al mismo tiempo. Solo cargar lo que se necesita para la tarea actual. Esto mantiene el contexto del agente limpio y eficiente.