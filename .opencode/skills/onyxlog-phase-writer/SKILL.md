---
name: onyxlog-phase-writer
description: Metodologia para validar y escribir fases de OnyxLog en el sistema de archivos. Recibe la salida de onyxlog-phase-creator (3 bloques delimitados), valida que todo sea correcto y escribe phase-N.md, overview.md y STATE.md.
metadata:
  audience: developers
  workflow: onyxlog
---

## Formato de Entrada

El agente recibe como entrada la salida generada por `onyxlog-phase-creator`, que contiene 3 bloques delimitados:

```
=== phase-N.md ===
[contenido completo del archivo de fase]

=== overview.md (patch) ===
[fila nueva para la tabla de seguimiento]
[instrucciones de donde insertarla]

=== STATE.md (patch) ===
[secciones a reemplazar/agregar]
[instrucciones de que secciones modificar]
```

### Parsing de los delimitadores

1. Buscar el string `=== phase-N.md ===` para obtener el contenido de la nueva fase
2. Buscar el string `=== overview.md (patch) ===` para obtener la fila y las instrucciones de insercion
3. Buscar el string `=== STATE.md (patch) ===` para obtener las secciones a actualizar
4. El contenido entre cada delimitador y el siguiente (o fin de texto) pertenece a ese bloque

## Validaciones Pre-Escritura

Antes de escribir cualquier archivo, ejecutar las siguientes validaciones en orden. Si alguna falla, reportar el error y detenerse.

### 1. Verificar que phase-N.md no existe

- Leer `IA/PHASES/` para listar los archivos existentes
- Si `IA/PHASES/phase-N.md` ya existe (donde N es el numero de fase), reportar error: `ERROR: phase-N.md ya existe. No se puede sobreescribir una fase existente.`
- Si la fase ya existe, sugerir usar un numero de fase diferente o eliminar la fase existente primero

### 2. Verificar que overview.md tiene la estructura esperada

- Leer `IA/PHASES/overview.md`
- Verificar que contiene la tabla de seguimiento con el formato: `| Fase | Estado | Progreso | Archivo |`
- Si la tabla no existe o tiene formato incorrecto, reportar error: `ERROR: overview.md no tiene la tabla de seguimiento esperada.`

### 3. Verificar que STATE.md tiene la estructura esperada

- Leer `IA/STATE.md`
- Verificar que contiene las secciones: "Fase Actual", "Progreso" (tabla), "Tareas"
- Si falta alguna seccion, reportar error: `ERROR: STATE.md no tiene la estructura esperada (faltan secciones: ...).`

### 4. Verificar numero de fase

- Leer `IA/STATE.md` para determinar el numero de la ultima fase completada
- Leer `IA/PHASES/overview.md` para determinar el numero de la ultima fase en la tabla
- El numero de la nueva fase debe ser: `max(ultima fase en STATE.md, ultima fase en overview.md) + 1`
- Si el numero de fase en la entrada no coincide, reportar error: `ERROR: Numero de fase incorrecto. Se esperaba N pero se recibio M.`

### 5. Verificar contenido obligatorio de la fase

El contenido de `phase-N.md` debe contener TODAS estas secciones (en cualquier orden):

- `## Objetivos`
- `## Entregables`
- `## Criterios de Completitud`
- `## Tareas`

Si falta alguna seccion, reportar error: `ERROR: phase-N.md no contiene la seccion obligatoria: ## [seccion faltante].`

## Escritura de Archivos

Si todas las validaciones pasan, proceder a escribir los 3 archivos en este orden:

### 1. Escribir phase-N.md

- Ruta: `IA/PHASES/phase-N.md`
- Accion: Crear archivo nuevo con el contenido completo del bloque `=== phase-N.md ===`
- El contenido se escribe tal como viene del bloque, sin modificaciones

### 2. Actualizar overview.md

- Ruta: `IA/PHASES/overview.md`
- Accion: Insertar la nueva fila en la tabla de seguimiento
- La fila se inserta como ultima fila de la tabla, antes de cualquier linea vacia o seccion "Leyenda de Estados"
- REGLA: Buscar la ultima fila de la tabla (que empieza con `|`) y agregar la nueva fila inmediatamente despues
- No modificar ninguna otra parte del archivo

Ejemplo de insercion:
```
| 5 — Funcionalidades Avanzadas | ✅ Completada | 100% | [phase-5.md](phase-5.md) |
| 6 — Sistema de Notificaciones | ⏳ Pendiente | 0% | [phase-6.md](phase-6.md) |  <-- nueva fila
```

### 3. Actualizar STATE.md

- Ruta: `IA/STATE.md`
- Acciones:
  a. Reemplazar la seccion "## Fase Actual" con la nueva fase y estado "Pendiente"
  b. Agregar una fila en la tabla "## Progreso" para la nueva fase con estado "Pendiente" y progreso "0%"
  c. Agregar la tabla "## Tareas Fase N" con todas las tareas de la nueva fase, todas con estado "Pendiente"
  d. Actualizar "Nuevos Componentes Fase N" si el patch incluye componentes nuevos
  e. Mantener todas las metricas y datos de fases anteriores intactos

#### Formato de la seccion Fase Actual:

```markdown
## Fase Actual: N — [Nombre de la Fase]

**Estado**: Pendiente

**Proxima tarea**: T1 — [Titulo de la primera tarea]
```

#### Formato de la fila en tabla de Progreso:

```markdown
| N — [Nombre de la Fase] | ⏳ Pendiente | 0% |  |
```

#### Formato de la tabla de Tareas:

```markdown
## Tareas Fase N

| Tarea | Estado | Descripcion |
|-------|--------|-------------|
| T1 - [Titulo] | ⏳ Pendiente | [Descripcion corta] |
| T2 - [Titulo] | ⏳ Pendiente | [Descripcion corta] |
...
```

#### Nuevos Componentes (si aplica):

Si el patch incluye una seccion de nuevos componentes:

```markdown
## Nuevos Componentes Fase N

- [Componente 1]
- [Componente 2]
...
```

## Validaciones Post-Escritura

Despues de escribir los 3 archivos, ejecutar las siguientes validaciones:

1. Leer `IA/PHASES/phase-N.md` y verificar:
   - El archivo existe y no esta vacio
   - Contiene las secciones obligatorias (Objetivos, Entregables, Criterios, Tareas)
   - El numero de fase en el titulo coincide con el nombre del archivo

2. Leer `IA/PHASES/overview.md` y verificar:
   - La nueva fila esta presente en la tabla de seguimiento
   - La tabla tiene el numero correcto de filas (filas anteriores + 1)
   - El formato de la fila es consistente con las demas

3. Leer `IA/STATE.md` y verificar:
   - La seccion "Fase Actual" refleja la nueva fase
   - La tabla de Progreso tiene la nueva fila
   - La tabla de Tareas Fase N esta presente y tiene todas las tareas
   - Las fases anteriores siguen intactas

Si alguna validacion post-escritura falla, reportar el error especifico y sugerir correccion manual.

## Formato de Salida

Despues de completar todas las validaciones y escrituras, retornar un resumen:

```
Fase N creada exitosamente.

Archivos escritos:
- IA/PHASES/phase-N.md (creado, [N] lineas)
- IA/PHASES/overview.md (actualizado, fila agregada)
- IA/STATE.md (actualizado, secciones modificadas)

Validaciones:
- phase-N.md no existia previamente: OK
- overview.md tiene estructura esperada: OK
- STATE.md tiene estructura esperada: OK
- Numero de fase correcto (N): OK
- Secciones obligatorias presentes: OK
- Post-escritura phase-N.md: OK
- Post-escritura overview.md: OK
- Post-escritura STATE.md: OK

Proxima tarea sugerida: T1 — [Titulo de la primera tarea]
```

Si alguna validacion falla:

```
ERROR: [descripcion del error]

Acciones realizadas:
- [lista de archivos escritos o "ninguno" si se detuvo antes]

Acciones requeridas:
- [lista de correcciones manuales necesarias]
```

## Reglas

- Siempre validar ANTES de escribir cualquier archivo
- Si una validacion falla, NO escribir archivos y reportar el error
- Escribir los archivos en orden: phase-N.md → overview.md → STATE.md
- Si la escritura de phase-N.md falla, NO continuar con los otros archivos
- Si la escritura de overview.md falla, NO continuar con STATE.md
- Siempre ejecutar validaciones post-escritura
- NUNCA sobreescribir una fase existente
- NUNCA modificar archivos de `IA/CONTEXT/`
- NUNCA modificar archivos de codigo fuente
- Preservar el contenido existente de overview.md y STATE.md, solo agregar o actualizar secciones especificas
- Los estados de las tareas nuevas siempre son "Pendiente" (⏳)