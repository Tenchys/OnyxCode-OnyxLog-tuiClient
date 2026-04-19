---
name: onyxlog-tui-commit
description: Convenciones de commits y PRs para OnyxLog TUI Client. Formato Conventional Commits, scopes, reglas de agrupacion y flujos de creacion.
metadata:
  audience: developers
  workflow: onyxlog-tui
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
- Footer: referencia a tarea o issue (`Refs: #42`)

### Tipos

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Correccion de bug |
| `refactor` | Reestructuracion sin cambio funcional |
| `docs` | Cambios en documentacion |
| `test` | Agregar o corregir tests |
| `chore` | Mantenimiento, deps, config, herramientas |
| `perf` | Mejora de performance |
| `ci` | Cambios en CI/CD |
| `style` | Formato, no cambia logica |

### Scopes

| Scope | Capa afectada |
|-------|-------------|
| `screen` | Pantallas Textual (login, dashboard, logs, etc.) |
| `api` | Clientes HTTP (auth, applications, logs) |
| `models` | Schemas Pydantic |
| `db` | Base de datos local SQLite (aiosqlite) |
| `config` | Configuracion (settings, env vars) |
| `ui` | Widgets, estilos CSS, layouts |
| `deps` | Dependencias (pyproject.toml) |

Si el cambio afecta multiples scopes, usa el scope principal o el mas especifico.

### Ejemplos

```
feat(screen): add login screen with register form

- Add LoginScreen with username/email/password inputs
- Add register toggle between login and signup
- Store API key in SQLite on successful auth

Refs: #12
```

```
fix(api): handle connection errors gracefully in client

Show user-friendly notification instead of crashing when
the OnyxLog server is unreachable.
```

```
refactor(db): extract key storage into separate functions

Move store_key and get_active_key into db.py for reusability.
```

## Reglas de Agrupacion de Commits

| Regla | Criterio |
|-------|----------|
| COM-01 | No mezclar features con fixes en el mismo commit |
| COM-02 | No mezclar refactor con cambios funcionales |
| COM-03 | Cambios en DB schema en commit separado de UI changes |
| COM-04 | Tests en commit separado de la implementacion (excepto TDD) |
| COM-05 | Cambios de documentacion pueden ir con su feature o en commit propio |
| COM-06 | Actualizar AGENTS.md, README.md, `.opencode/agents/` o `.opencode/skills/` cuando corresponda |
| COM-07 | NUNCA commitear `.env`, secrets, API keys, `__pycache__`, `.pyc` |
| COM-08 | Ejecutar `ruff check src/ tests/` y `ruff format src/ tests/` antes de commitear |
| COM-09 | Si lint falla, corregir ANTES de commitear |
| COM-10 | Si se modifica el schema de SQLite, incluir la migracion en el mismo conjunto de cambios |

## Regla de Documentacion

Antes de hacer commit, verificar si algun cambio requiere actualizar documentacion operativa:

| Cambio | Accion |
|--------|--------|
| Nueva pantalla o screen | Actualizar README.md y, si aplica, AGENTS.md |
| Nuevo endpoint en api/ | Actualizar README.md, docs y referencias de skills |
| Nuevo schema o modelo | Verificar que este en models/schemas.py |
| Nuevo error_code | Actualizar tabla de codigos de error |
| Cambio en config | Verificar variables en config.py |
| Cambio en DB schema | Actualizar README.md, AGENTS.md y skills relacionadas |
| Cambio en agentes o skills | Actualizar `.opencode/agents/` o `.opencode/skills/` |

## Flujo de Creacion de Commit

1. Ejecutar `git status` para ver archivos modificados y sin trackear
2. Ejecutar `git diff --stat` y `git diff` para ver el contenido de los cambios
3. Ejecutar `git log --oneline -10` para entender el estilo de commits previos
4. **Verificacion de seguridad**: buscar secrets en el diff usando estos patrones:
   - Archivos `.env` (no `.env.example`)
   - Strings que parecen secrets: API keys reales, passwords hardcodeados
   - `password = "..."` con valor literal
   - Si se encuentran secrets: **BLOQUEAR** commit y reportar al usuario
5. **Agrupacion**: analizar los cambios y agrupar por concern logico segun COM-01 a COM-06
   - Si hay multiples concerns, proponer commits separados
   - Si hay un solo concern, un solo commit
6. **Documentacion**: verificar si algun cambio requiere actualizar AGENTS.md (segun tabla arriba)
7. **Generar mensaje**: crear mensaje Conventional Commit por grupo
8. **Pre-commit check**: ejecutar lint (COM-08/09):
   ```bash
   ruff check src/ tests/
   ruff format --check src/ tests/
   pytest tests/ -v --tb=short
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
| `password = "..."` con valor literal | Password hardcodeado |
| `DATABASE_URL` con credenciales | Credenciales en connection string |

Patrones **permitidos**:

| Patron | Razon |
|--------|-------|
| `.env.example` | Plantilla sin valores reales |
| Variables leidas de `os.environ` o `Settings` | Valor desde entorno o config |
| Campo `password` en schemas/modelos | Nombre de campo, no valor real |

## Flujo de Creacion de PR

1. Ejecutar `git status` para ver estado actual
2. Ejecutar `git log <base>..HEAD --oneline` para ver commits del branch
3. Ejecutar `git diff <base>..HEAD` para ver todos los cambios
4. **Pre-review**: invocar revision con criterios de `onyxlog-tui-review`
5. **Verificacion de seguridad**: buscar secrets en el diff completo
6. **Compilar descripcion** usando el template de PR
7. **Crear branch** con formato: `<type>/<scope>-<short-description>`
8. **Push**: `git push -u origin <branch>`
9. **Crear PR** con `gh pr create` usando el label que mejor corresponda al tipo del cambio
10. Retornar URL del PR al usuario

### Nombres de Branches

```
<type>/<scope>-<short-description>

feat/screen-login-form
fix/api-connection-error
refactor/db-key-storage
test/auth-integration
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

Mapeo sugerido:
- `feat` -> `feature`
- `fix` -> `bugfix`
- `refactor` -> `refactor`
- `docs` -> `docs`
- `test` -> `testing`
- `chore`, `perf`, `ci`, `style` -> `chore`

Mapeo sugerido:
- `feat` -> `feature`
- `fix` -> `bugfix`
- `refactor` -> `refactor`
- `docs` -> `docs`
- `test` -> `testing`
- `chore`, `perf`, `ci`, `style` -> `chore`

## Template de Descripcion de PR

```markdown
## Resumen

- <cambio principal 1>
- <cambio principal 2>
- <cambio principal 3>

## Cambios Detallados

- `src/screens/<archivo>.py`: <descripcion del cambio>
- `src/api/<archivo>.py`: <descripcion del cambio>
- `src/models/schemas.py`: <descripcion del cambio>
- `src/db.py`: <descripcion del cambio>

## Testing

- [ ] Tests de API client para <endpoint/feature>
- [ ] Tests de DB local para <funcion>
- [ ] Tests de UI con pilot para <screen>
- Cobertura objetivo: >= 80%

## Checklist

- [x] Lint pasa (`ruff check src/ tests/`)
- [x] Formato pasa (`ruff format --check src/ tests/`)
- [x] Tests pasan (`pytest tests/ -v`)
- [x] AGENTS.md actualizado si aplica
- [x] Sin secrets en el diff
```

## Checklist Pre-Commit

Antes de cada commit, verificar:

```bash
# 1. Formato y lint
ruff check src/ tests/
ruff format --check src/ tests/

# 2. Tests (si aplica)
pytest tests/ -v --tb=short

# 3. Sin secrets
git diff --cached | grep -iE '(api_key|password|secret|token)\s*=\s*["'"'"']' && echo "BLOQUEADO: posible secret" || echo "OK"
```
