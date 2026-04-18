---
name: onyxlog-commit
description: Convenciones de commits y PRs para OnyxLog. Formato Conventional Commits, reglas de agrupacion, templates de PR y flujos de creacion.
metadata:
  audience: developers
  workflow: onyxlog
---

## Conventional Commits

### Formato

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

- Linea principal: maximo 72 caracteres
- Descripcion: en ingles, Imperativo ("add", no "added" ni "adds")
- Cuerpo: explica el *por que*, no el *que*. Un bullet point por change concern
- Footer: referencia a fase o issue (`Refs: IA/PHASES.md#fase-2`)

### Tipos

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Correccion de bug |
| `refactor` | Reestructuracion sin cambio funcional |
| `docs` | Cambios en documentacion (README, docs) |
| `test` | Agregar o corregir tests |
| `chore` | Mantenimiento, deps, config, herramientas |
| `perf` | Mejora de performance |
| `ci` | Cambios en CI/CD |
| `style` | Formato, no cambia logica |

### Scopes

| Scope | Capa afectada |
|-------|-------------|
| `api` | Routes, dependencies, middleware |
| `models` | Modelos SQLAlchemy |
| `schemas` | Schemas Pydantic |
| `services` | Logica de negocio |
| `auth` | Autenticacion y API Keys |
| `db` | Migraciones, configuracion de BD |
| `config` | Configuracion de la aplicacion |
| `deps` | Dependencias (requirements, pyproject.toml) |

Si el cambio afecta multiples scopes, usa el scope principal o el mas especifico.

### Ejemplos

```
feat(api): add GET /stats/summary endpoint

- Add StatsService.summary() with aggregation logic
- Add StatsQuery and StatsRead schemas
- Register /stats router in main.py

Refs: IA/PHASES.md#fase-3
```

```
fix(auth): validate API key before processing request

The middleware was processing the request body before validating
the API key, allowing unauthenticated requests to consume resources.

Refs: #142
```

```
refactor(services): extract query builder from log_service

Move filter construction to a dedicated QueryBuilder class
for reusability across stats and log queries.
```

## Reglas de Agrupacion de Commits

| Regla | Criterio |
|-------|----------|
| COM-01 | No mezclar features con fixes en el mismo commit |
| COM-02 | No mezclar refactor con cambios funcionales |
| COM-03 | Migraciones Alembic en commit separado del cambio de modelo |
| COM-04 | Tests en commit separado de la implementacion (excepto TDD) |
| COM-05 | Cambios de documentacion pueden ir con su feature o en commit propio |
| COM-06 | Actualizar README.md cuando se agregan endpoints, modelos, configs o cambios de arquitectura (segun AGENTS.md) |
| COM-07 | NUNCA commitear `.env`, secrets, credenciales, `__pycache__`, `.pyc` |
| COM-08 | Ejecutar `black --check src/`, `isort --check src/`, `mypy src/` antes de commitear |
| COM-09 | Si lint o typecheck fallan, corregir ANTES de commitear |
| COM-10 | Si se modifica un modelo SQLAlchemy, incluir migracion Alembic en el mismo conjunto de cambios |

## Regla de Documentacion (AGENTS.md)

Antes de hacer commit, verificar si algun cambio requiere actualizar README.md:

| Cambio | Accion en README.md |
|--------|---------------------|
| Nuevo endpoint | Agregar a tabla de endpoints |
| Nuevo modelo o cambio en schema | Actualizar seccion Modelos de Datos |
| Nueva configuracion o variable de entorno | Agregar a tabla de variables de entorno |
| Fase completada | Actualizar tabla de estado del proyecto |
| Nuevo comando o cambio en flujo | Actualizar seccion Instalacion y Desarrollo |
| Cambio de arquitectura o estructura | Actualizar secciones correspondientes |

## Flujo de Creacion de Commit

1. Ejecutar `git status` para ver archivos modificados y sin trackear
2. Ejecutar `git diff --stat` y `git diff` para ver el contenido de los cambios
3. Ejecutar `git log --oneline -10` para entender el estilo de commits previos
4. **Verificacion de seguridad**: buscar secrets en el diff usando estos patrones:
   - Archivos `.env` (no `.env.example`)
   - Strings que parecen secrets: `sk_`, `key_`, `Bearer`, JWT largos
   - `SECRET_KEY = "..."` con valor literal
   - `password = "..."` con valor literal
   - `DATABASE_URL` con credenciales embebidas
   - Archivos `credentials.json`, `service-account.json`
   - Si se encuentran secrets: **BLOQUEAR** commit y reportar al usuario
5. **Agrupacion**: analizar los cambios y agrupar por concern logico segun COM-01 a COM-06
   - Si hay multiples concerns, proponer commits separados
   - Si hay un solo concern, un solo commit
6. **Documentacion**: verificar si algun cambio requiere actualizar README.md (segun tabla arriba)
   - Si falta actualizacion de README.md, incluir los cambios de documentacion en el commit o en un commit separado tipo `docs`
7. **Generar mensaje**: crear mensaje Conventional Commit por grupo
8. **Pre-commit check**: ejecutar lint y typecheck (COM-08/09)
   ```bash
   black --check src/ 2>&1
   isort --check src/ 2>&1
   mypy src/ 2>&1
   ```
   - Si fallan: corregir y reiniciar el flujo
9. **Ejecutar commit**:
   ```bash
   git add <archivos del grupo>
   git commit -m "<mensaje generado>"
   ```
10. **Verificar**: ejecutar `git status` y `git log -1` para confirmar

### Reglas de Deteccion de Secrets

Patrones que **BLOQUEAN** el commit:

| Patron | Razon |
|--------|-------|
| Archivo `.env` (no `.env.example`) | Contiene variables con valores reales |
| Strings tipo `sk_*`, `key_*`, `Bearer *` | Parecen API keys o tokens |
| `SECRET_KEY = "..."` con valor literal | Secret hardcodeado |
| `password = "..."` con valor literal | Password hardcodeado |
| `DATABASE_URL` con credenciales | Credenciales en connection string |
| `credentials.json`, `service-account.json` | Archivos de credenciales cloud |

Patrones **permitidos**:

| Patron | Razon |
|--------|-------|
| `.env.example` | Plantilla sin valores reales |
| `SECRET_KEY` leido de `os.environ` | Valor desde variable de entorno |
| Campo `password` en schemas/modelos | Nombre de campo, no valor real |

## Flujo de Creacion de PR

1. Ejecutar `git status` para ver estado actual
2. Ejecutar `git log <base>..HEAD --oneline` para ver commits del branch
3. Ejecutar `git diff <base>..HEAD` para ver todos los cambios
4. **Pre-review**: invocar revision con criterios de `onyxlog-review` sobre el diff
5. **Verificacion de seguridad**: buscar secrets en el diff completo
6. **Verificacion de documentacion**: confirmar README.md actualizado si corresponde
7. **Compilar descripcion** usando el template de PR (ver seccion Template)
8. **Crear branch** si es necesario con formato:
   ```
   <type>/<scope>-<short-description>
   ```
   Ejemplos: `feat/api-stats-summary`, `fix/auth-api-key-validation`, `refactor/services-query-builder`
9. **Push**:
   ```bash
   git push -u origin <branch>
   ```
10. **Crear PR**:
    ```bash
    gh pr create \
      --title "<type>(<scope>): <description>" \
      --body "<descripcion generada>" \
      --label "<type>"
    ```
11. Retornar URL del PR al usuario

### Nombres de Branches

```
<type>/<scope>-<short-description>

feat/api-stats-summary
fix/auth-api-key-validation
refactor/services-query-builder
docs/readme-phase-2
test/logs-integration
chore/deps-update
```

### Labels de PR

| Label | Uso |
|-------|-----|
| `feature` | Nuevas funcionalidades |
| `bugfix` | Correcciones de bugs |
| `refactor` | Reestructuracion |
| `docs` | Documentacion |
| `testing` | Tests |
| `chore` | Mantenimiento |

## Template de Descripcion de PR

```markdown
## Resumen

- <cambio principal 1>
- <cambio principal 2>
- <cambio principal 3>

## Cambios Detallados

- `src/api/routes/<archivo>.py`: <descripcion del cambio>
- `src/services/<archivo>.py`: <descripcion del cambio>
- `src/schemas/<archivo>.py`: <descripcion del cambio>
- `src/models/<archivo>.py`: <descripcion del cambio>
- `README.md`: <secciones actualizadas>

## Testing

- [ ] Tests de integracion para <endpoint/feature>
- [ ] Tests de servicio para <logica>
- Cobertura objetivo: >= 80%

## Notas de Despliegue

- [ ] Ejecutar `alembic upgrade head` (migracion nueva)
- [ ] Variable `<ONYXLOG_NUEVA_VAR>` en `.env.production`
- [ ] Dependencia nueva: `<paquete>`

## Checklist

- [x] Lint pasa (`black --check src/`, `isort --check src/`)
- [x] Type checking pasa (`mypy src/`)
- [x] Tests pasan (`pytest tests/ -v`)
- [x] README.md actualizado
- [x] Sin secrets en el diff
- [x] Migracion Alembic incluida (si aplica)
```

## Checklist Pre-Commit

Antes de cada commit, verificar:

```bash
# 1. Formato
black --check src/
isort --check src/

# 2. Tipos
mypy src/

# 3. Tests (si aplica)
pytest tests/ -v --tb=short

# 4. Sin secrets
git diff --cached | grep -iE '(SECRET_KEY|password|token|api_key)\s*=\s*["'"'"']' && echo "BLOQUEADO: posible secret" || echo "OK"
```

## Errores Comunes y Como Evitarlos

| Error | Solucion |
|-------|----------|
| Commit con `.env` | Agregar `.env` a `.gitignore`, solo commitear `.env.example` |
| Commit con `__pycache__` | Verificar `.gitignore` incluye `__pycache__/` |
| Mensaje generico ("fix bug") | Usar formato Conventional Commits con scope especifico |
| Mezclar refactor + feature | Crear dos commits separados (COM-02) |
| Olvidar actualizar README | Verificar regla de documentacion antes de commit (COM-06) |
| Commit sin migracion | Si se cambio un modelo, generar migracion primero (COM-10) |
| `-m` multilinea desordenada | Usar `-m "titulo" -m "cuerpo"` o heredoc para commits multilinea |

## Ejemplo de Sesion Completa: Commit

**Escenario**: Se agrego endpoint GET /stats/summary con su servicio y schema.

```bash
# Paso 1-2: Verificar cambios
git status
git diff --stat

# Paso 3: Ver historial
git log --oneline -5

# Paso 4: Sin secrets (verificado manualmente)

# Paso 5: Agrupacion
# - src/api/routes/stats.py + src/services/stats_service.py + src/schemas/query.py
#   → Un solo concern: feat(api) add stats summary
# - README.md → incluido en el mismo commit (COM-05)

# Paso 6: README necesita actualizacion (nuevo endpoint)

# Paso 7: Generar mensaje
# feat(api): add GET /stats/summary endpoint

# Paso 8: Pre-commit check
black --check src/
isort --check src/
mypy src/

# Paso 9: Commit
git add src/api/routes/stats.py src/services/stats_service.py src/schemas/query.py README.md
git commit -m "feat(api): add GET /stats/summary endpoint

- Add StatsService.summary() with aggregation logic
- Add StatsQuery and StatsRead schemas
- Register /stats router in main.py
- Update README.md endpoints table

Refs: IA/PHASES.md#fase-3"

# Paso 10: Verificar
git log -1
git status
```

## Ejemplo de Sesion Completa: PR

**Escenario**: Branch `feat/api-stats-summary` listo para PR.

```bash
# Pasos 1-3: Ver cambios
git status
git log main..HEAD --oneline
git diff main..HEAD

# Paso 4: Pre-review (invocar onyxlog-reviewer en modo diff)

# Paso 7: Compilar descripcion con template

# Paso 8-9: Push
git push -u origin feat/api-stats-summary

# Paso 10: Crear PR
gh pr create \
  --title "feat(api): add stats summary endpoints" \
  --body "$(cat <<'EOF'
## Resumen

- Add GET /stats/summary endpoint with aggregation logic
- Add StatsService with summary, trends, and error analysis methods
- Add StatsQuery and StatsRead schemas

## Cambios Detallados

- `src/api/routes/stats.py`: New endpoints for summary, trends, errors
- `src/services/stats_service.py`: Aggregation and query methods
- `src/schemas/query.py`: StatsQuery and StatsRead schemas
- `README.md`: Updated endpoints table

## Testing

- [x] Tests de integracion para /stats/summary
- [x] Tests de servicio para StatsService
- Cobertura: 85%

## Notas de Despliegue

- [ ] Ejecutar `alembic upgrade head`
- [ ] No se requieren nuevas variables de entorno

## Checklist

- [x] Lint pasa
- [x] Type checking pasa
- [x] Tests pasan
- [x] README.md actualizado
- [x] Sin secrets en el diff
- [x] Migracion Alembic incluida
EOF
)" \
  --label "feature"
```