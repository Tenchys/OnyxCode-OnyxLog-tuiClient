---
name: onyxlog-planner
description: Metodologia para planificar la implementacion de una fase de OnyxLog. Desglosa fases en tareas atomicas con dependencias, archivos afectados y criterios de aceptacion.
metadata:
  audience: developers
  workflow: onyxlog
---

## Flujo de Planificacion

Cuando se solicita planificar una fase, seguir estos pasos en orden:

### 1. Recopilar contexto

1. Leer `IA/STATE.md` para estado actual
2. Leer `IA/PHASES/phase-N.md` (N = fase a planificar)
3. Leer `IA/PHASES/overview.md` para reglas generales de fases
4. Leer los archivos de `IA/CONTEXT/` relevantes segun el tipo de fase:
   - Fases con endpoints nuevos → `endpoints-reference.md` + `schemas-reference.md`
   - Fases con modelos nuevos → `models-reference.md` + `schemas-reference.md`
   - Fases de infraestructura → `config-reference.md` + `architecture.md`
   - Fases de seguridad → `workflows-reference.md` + `config-reference.md`
   - Si hay duda → leer `architecture.md` siempre

### 2. Verificar estado del codigo

Antes de planificar, validar que el codigo actual coincide con lo documentado:

- `git log --oneline -5` para ver ultimos cambios
- `pytest tests/ --tb=short -q 2>&1 | tail -5` para verificar que los tests pasan
- Verificar que la migracion mas reciente en `alembic/versions/` coincide con STATE.md
- Si hay discrepancias, incluirlas como notas en el plan

### 3. Desglosar en tareas

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

### 4. Ordenar tareas

- Orden topologico respetando dependencias
- Las tareas sin dependencias entre si se pueden implementar en paralelo
- Priorizar primero las tareas que desbloquean a otras
- Los tests de cada componente van en la misma tarea que el componente

### 5. Identificar riesgos

Para cada tarea, evaluar si tiene:
- Riesgo de breaking change en la API existente
- Necesidad de migracion de base de datos
- Dependencia de servicios externos (Redis, Docker, etc.)
- Impacto en performance

### 6. Formato de salida del plan

El plan DEBE seguir esta estructura exacta:

```markdown
# Plan: Fase N — [Nombre de la Fase]

**Fecha**: YYYY-MM-DD
**Fase**: N
**Estado actual**: [estado de STATE.md]
**Tests actuales**: [resultado de pytest]

## Resumen

[Una frase que resume el objetivo de la fase]

## Tareas

### T1: [Titulo]
- **Descripcion**: [que hacer]
- **Archivos**: [lista de archivos]
- **Dependencias**: Ninguna | T{x}
- **Criterios**: [lista verificable]
- **Estimacion**: S | M | L

[... repeticion para cada tarea ...]

## Orden de implementacion

1. T1 → T2 → T3 (secuencia)
4. T4 (paralelo con T2-T3)
5. T5 (depende de T3 y T4)

## Riesgos

| Tarea | Riesgo | Mitigacion |
|-------|--------|------------|
| T3    | [desc] | [accion]   |

## Notas

- [Cualquier discrepancia entre documentacion y codigo real]
- [Decisiones de diseno tomadas al planificar]
```

## Reglas

- NUNCA implementar codigo, solo planificar
- NUNCA modificar archivos del proyecto al planificar
- Siempre verificar el estado real del codigo, no solo la documentacion
- Cada tarea debe ser independiente y commiteable por si sola
- Los tests van en la misma tarea que el codigo que prueban
- Las migraciones Alembic van en la misma tarea que el modelo que crean
- Si una tarea es muy grande, dividirla en dos
- Incluir siempre la tarea de actualizar README.md como la ultima tarea del plan
- Incluir siempre una tarea de actualizar IA/STATE.md al completar la fase