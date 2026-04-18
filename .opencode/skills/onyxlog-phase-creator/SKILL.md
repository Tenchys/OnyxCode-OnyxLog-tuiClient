---
name: onyxlog-phase-creator
description: Metodologia para crear nuevas fases de OnyxLog. Genera el contenido de phase-N.md, actualizaciones para overview.md y STATE.md siguiendo el formato y convenciones de las fases existentes.
metadata:
  audience: developers
  workflow: onyxlog
---

## Tipos de Fase

Todo lo que se agrega a OnyxLog se organiza en fases. Hay 5 tipos:

| Tipo | Descripcion | Contexto a leer | Codigo a analizar |
|------|-------------|-----------------|-------------------|
| **feature** | Nueva funcionalidad (endpoints, modelos, servicios) | `endpoints-reference.md` + `models-reference.md` + `schemas-reference.md` | `src/models/`, `src/api/routes/`, `src/schemas/`, `src/services/` |
| **fix** | Correccion de bugs o problemas existentes | Archivo(s) con el bug + `architecture.md` | Archivo(s) afectado(s) + tests existentes |
| **enhancement** | Mejora de funcionalidad existente | Contexto del feature a mejorar | Archivos del feature + tests existentes |
| **infra** | Cambios de infraestructura (Docker, CI/CD, deploy) | `config-reference.md` + `architecture.md` | `src/core/`, `docker/`, `alembic/` |
| **refactor** | Reestructuracion de codigo existente | `architecture.md` | Directorio(s) afectado(s) + tests existentes |

## Flujo de Creacion de Fase

### 1. Recopilar contexto

1. Leer `IA/STATE.md` para estado actual y numero de siguiente fase
2. Leer `IA/PHASES/overview.md` para reglas generales de fases
3. Leer la ultima fase completada (`IA/PHASES/phase-N.md` donde N es la ultima fase) como referencia de formato
4. Leer los archivos de `IA/CONTEXT/` segun el tipo de fase (ver tabla arriba)
5. Siempre leer `IA/CONTEXT/architecture.md` para estructura del proyecto

### 2. Analizar codigo fuente

Segun el tipo de fase, leer el codigo fuente relevante para:

- Identificar modelos existentes en `src/models/` (para no duplicar)
- Identificar endpoints existentes en `src/api/routes/` (para no duplicar)
- Identificar schemas existentes en `src/schemas/` (para no duplicar)
- Identificar servicios existentes en `src/services/` (para no duplicar)
- Verificar migraciones existentes en `alembic/versions/`
- Verificar tests existentes en `tests/`

### 3. Verificar estado del codigo

Antes de crear la fase, validar:

- `git log --oneline -5` para ver ultimos cambios
- `pytest tests/ --tb=short -q 2>&1 | tail -5` para verificar que los tests pasan
- Verificar que la migracion mas reciente en `alembic/versions/` coincide con STATE.md
- Si hay discrepancias, incluirlas como notas en la fase

### 4. Numerar la fase

- Numero de fase = ultima fase existente + 1
- Si STATE.md dice "Fase 5 completada", la siguiente es Fase 6
- El archivo se llama `phase-6.md`

### 5. Definir tareas

Reglas de granularidad:

- Cada tarea debe ser implementable en **1-2 horas maximo**
- Cada tarea debe producir un **commit atomico** independiente
- Maximo **15 tareas por fase**
- Si una fase necesita mas de 15 tareas, agrupar en subtareas dentro de tareas principales
- Cada tarea debe tener **criterios de aceptacion** verificables

Para cada tarea, definir:

1. **ID**: T1, T2, T3... (orden secuencial de implementacion)
2. **Titulo**: Descripcion corta e imperativa
3. **Descripcion**: Que hacer y por que (2-3 lineas)
4. **Archivos**: Lista de archivos a crear o modificar (con ruta completa)
5. **Dependencias**: IDs de tareas que deben completarse antes
6. **Criterios de aceptacion**: Que validar para considerar la tarea completada
7. **Estimacion**: S, M o L (S=30min, M=1h, L=2h)

Orden de tareas:

- Orden topologico respetando dependencias
- Las tareas sin dependencias entre si se pueden implementar en paralelo
- Priorizar primero las tareas que desbloquean a otras
- Los tests de cada componente van en la misma tarea que el componente
- Las migraciones Alembic van en la misma tarea que el modelo que crean
- Incluir siempre una tarea de actualizar README.md como penultima tarea
- Incluir siempre una tarea de actualizar IA/STATE.md como ultima tarea

### 6. Identificar riesgos

Para cada tarea, evaluar si tiene:

- Riesgo de breaking change en la API existente
- Necesidad de migracion de base de datos
- Dependencia de servicios externos (Redis, Docker, etc.)
- Impacto en performance

### 7. Generar contenido

El agente genera 3 bloques de contenido que retorna al usuario. **NUNCA escribe archivos directamente**.

#### Template de `phase-N.md`

```markdown
# Fase N: [Nombre de la Fase]

**Estado**: Pendiente | **Progreso**: 0% | **Fechas**: [fecha actual]
**Dependencias**: [Fases previas o Ninguna] | **Ultima actualizacion**: [fecha actual]

## Objetivos

- [Objetivo 1]
- [Objetivo 2]
...

## Entregables

1. [Entregable 1]
2. [Entregable 2]
...

## Componentes a Implementar

### 1. [Componente]
- [Detalle del componente]
- [Sub-componentes si aplica]

[... mas componentes ...]

## Tests a Implementar

**Archivos**: `tests/test_[modulo].py`

1. [Test 1]
2. [Test 2]
...

## Endpoints Funcionales

1. `METHOD /api/v1/path`: [Descripcion]
[... mas endpoints ...]

## Criterios de Completitud

- [ ] [Criterio 1]
- [ ] [Criterio 2]
...

**Progreso**: 0/[total] (0%)

## Tareas

### T1: [Titulo]
- **Descripcion**: [que hacer y por que]
- **Archivos**: [lista de archivos a crear/modificar]
- **Dependencias**: Ninguna | T{x}
- **Criterios**: [lista verificable]
- **Estimacion**: S | M | L

[... mas tareas ...]

### T{N-1}: Actualizar documentacion
- **Descripcion**: Actualizar README.md con los nuevos endpoints, modelos y configuraciones
- **Archivos**: `README.md`
- **Dependencias**: T{N-2}
- **Criterios**: README.md refleja todos los cambios de la fase
- **Estimacion**: S

### TN: Actualizar estado del proyecto
- **Descripcion**: Actualizar IA/STATE.md con la fase completada, nuevas metricas y componentes
- **Archivos**: `IA/STATE.md`
- **Dependencias**: T{N-1}
- **Criterios**: STATE.md refleja el estado actualizado del proyecto
- **Estimacion**: S

## Orden de Implementacion

1. T1 → T2 → T3 (secuencia)
2. T4 (paralelo con T2-T3)
3. T5 (depende de T3 y T4)
...

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T{x} | [descripcion] | [accion] |

## Comandos de Verificacion

```bash
[comandos especificos para la fase]
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Notas de Implementacion

- [Notas relevantes sobre decisiones de diseno]
- [Discrepancias encontradas entre documentacion y codigo real]

## Historial

- **[fecha]**: Fase creada, planificacion inicial completada
```

#### Actualizacion de `overview.md`

Agregar una nueva fila a la tabla de seguimiento:

```markdown
| N — [Nombre de la Fase] | Pendiente | 0% | [phase-N.md](phase-N.md) |
```

La fila se inserta como ultima fila de la tabla, antes de la seccion "Leyenda de Estados".

#### Actualizacion de `STATE.md`

Reemplazar la seccion de estado para reflejar la nueva fase:

- Cambiar "Fase Actual" al numero y nombre de la nueva fase
- Cambiar "Estado" a "Pendiente"
- Agregar la nueva fase a la tabla de progreso con estado "Pendiente" y progreso "0%"
- Agregar tabla de tareas de la nueva fase (todas con estado "Pendiente")
- Actualizar "Nuevos Componentes" si aplica
- Mantener las metricas de las fases anteriores

### 8. Formato de salida

El agente retorna 3 bloques claramente separados usando estos delimitadores:

```
=== phase-N.md ===
[contenido completo del archivo]

=== overview.md (patch) ===
[Fila nueva para agregar a la tabla de seguimiento]
[Instrucciones de donde insertarla]

=== STATE.md (patch) ===
[Secciones a reemplazar/agregar]
[Instrucciones de que secciones modificar]
```

Cada bloque incluye instrucciones claras sobre donde escribir o insertar el contenido.

## Reglas

- NUNCA escribir archivos directamente, solo generar contenido
- Seguir EXACTAMENTE el formato de las fases 1-5 existentes
- Numerar la fase como ultima fase + 1
- Verificar siempre el estado real del codigo vs la documentacion
- Cada tarea debe ser independiente y commiteable por si sola
- Los tests van en la misma tarea que el codigo que prueban
- Las migraciones Alembic van en la misma tarea que el modelo que crean
- Si una tarea es muy grande, dividirla en dos
- Incluir siempre tarea de actualizar README.md como penultima
- Incluir siempre tarea de actualizar STATE.md como ultima
- El formato de los endpoints debe incluir el verbo HTTP, la ruta y una descripcion corta
- Los criterios de completitud deben ser verificables con comandos o tests
- Los riesgos deben incluir mitigacion concreta