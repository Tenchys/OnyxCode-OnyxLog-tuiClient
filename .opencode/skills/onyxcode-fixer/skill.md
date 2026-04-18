---
name: onyxcode-fixer
description: Skill para comparar una fase o tarea contra el codigo real, detectar inconsistencias y reparar el codigo y tests sin delegar la correccion a otros subagentes.
metadata:
  audience: developers
  workflow: onyxlog-tui
---

## Proposito

Este skill guia al agente `onyxcode-fixer` para revisar una especificacion y corregir el codigo hasta alinearlo con lo pedido.

## Alcance

Usar cuando exista una fase, tarea o descripcion de trabajo que deba contrastarse con la implementacion actual.

## Tipos de inconsistencia

| Tipo | Significado |
|------|-------------|
| `missing` | Falta una parte pedida por la especificacion |
| `partial` | Existe, pero esta incompleto o incorrecto |
| `drift` | El codigo se desvio de lo pedido |
| `convention` | No respeta patrones del proyecto |
| `test_gap` | Falta cobertura para lo implementado |

## Regla principal

El agente debe corregir solo lo necesario para cumplir la especificacion. No debe proponer mejoras ajenas ni reescribir partes no relacionadas.

## Flujo

1. Leer la especificacion.
2. Leer el codigo relevante.
3. Identificar diferencias.
4. Clasificar cada diferencia.
5. Aplicar correcciones.
6. Escribir o ajustar tests.
7. Verificar el resultado.
8. Reportar el cierre de gaps.

## Criterios de correccion

- Si una pantalla cambia, seguir `onyxlog-tui-screens`.
- Si una API cambia, seguir `onyxlog-tui-api-client`.
- Si cambia estilo, naming o arquitectura general, seguir `onyxlog-tui-coding`.
- Si falta cobertura, seguir `onyxlog-tui-testing`.
- Si el cambio toca criterios de auditoria, usar `onyxlog-tui-review` como referencia.

## Reglas

- No delegar a subagentes.
- No modificar archivos fuera del scope.
- No introducir cambios cosméticos sin necesidad.
- No romper la arquitectura existente.
- Mantener el codigo minimal y coherente con la especificacion.

## Verificacion

Usar siempre:

```bash
ruff check src/ tests/
ruff format src/ tests/
pytest tests/ -v
```

## Formato de reporte

```md
# Fix Report

## Especificacion
- ...

## Gaps encontrados
- ...

## Cambios aplicados
- ...

## Verificacion
- ...

## Pendientes
- ...
```
