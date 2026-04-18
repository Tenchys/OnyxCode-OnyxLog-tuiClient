---
name: onyxlog-docs
description: Genera y actualiza la documentacion de OnyxLog. Incluye instalacion, requisitos, referencia detallada de endpoints con ejemplos curl request/response, y variables de entorno.
metadata:
  audience: developers
  workflow: onyxlog
---

## Objetivo

Generar documentacion completa y actualizada de OnyxLog en dos archivos objetivos:

1. **README.md** — Contenido resumido: descripcion, stack, instalacion, requisitos, tabla de endpoints resumida, configuracion, autenticacion
2. **docs/api-reference.md** — Referencia detallada de cada endpoint con esquemas request/response y ejemplos curl

---

## Modos de Operacion

| Modo | Archivos generados | Descripcion |
|------|-------------------|-------------|
| `readme` | `README.md` | Actualiza solo README |
| `api-reference` | `docs/api-reference.md` | Genera solo la referencia detallada |
| `full` | `README.md` + `docs/api-reference.md` | Actualiza ambos (recomendado) |

Si no se especifica modo, usar `full`.

---

## Fuentes de Informacion

Cada seccion tiene fuentes especificas que DEBEN leerse para generar documentacion precisa. NUNCA inventar informacion.

### Seccion:Descripcion General

| Fuente | Que leer |
|--------|----------|
| `README.md` | Descripcion existente (preservar si es correcta) |
| `IA/CONTEXT/architecture.md` | Stack tecnologico, flujo de datos |
| `src/main.py` | Titulo y version de la app |

### Seccion: Requisitos e Instalacion

| Fuente | Que leer |
|--------|----------|
| `pyproject.toml` | Version de Python, dependencias principales |
| `requirements/base.txt` | Dependencias de produccion |
| `requirements/dev.txt` | Dependencias de desarrollo |
| `docker/Dockerfile` | Version de Python base, configuracion Docker |
| `docker/docker-compose.yml` | Servicios, versiones PostgreSQL y Redis |
| `.env.example` | Variables de entorno necesarias |
| `src/core/config.py` | Defaults de configuracion, prefijo ONYXLOG_ |
| `Makefile` | Comandos disponibles |

### Seccion: Endpoints

| Fuente | Que leer |
|--------|----------|
| `src/api/routes/*.py` | TODOS los route files — son la fuente principal |
| `src/schemas/*.py` | Schemas Pydantic para request/response bodies |
| `src/api/dependencies.py` | Dependencias de autenticacion (get_current_user, get_current_user_or_application) |
| `src/api/middleware.py` | Rutas publicas vs protegidas |
| `IA/CONTEXT/endpoints-reference.md` | Referencia existente (verificar que este actualizada) |
| `src/main.py` | Registro de routers y prefijos |

### Seccion: Configuracion

| Fuente | Que leer |
|--------|----------|
| `src/core/config.py` | Settings class con variables, tipos, defaults |
| `.env.example` | Variables de entorno con ejemplos |
| `docker/docker-compose.yml` | Configuracion de servicios externos |

### Seccion: Autenticacion

| Fuente | Que leer |
|--------|----------|
| `src/api/routes/auth.py` | Endpoints de auth |
| `src/services/auth_service.py` | Logica de autenticacion |
| `src/core/security.py` | Utilidades de seguridad |
| `IA/CONTEXT/workflows-reference.md` | Flujos de trabajo y roles |

---

## Reglas de Documentacion

### Reglas Generales

| ID | Regla |
|----|-------|
| DOC-01 | NUNCA inventar informacion. Si un archivo no existe o esta vacio, indicar "No documentado" |
| DOC-02 | Toda la documentacion en espanol, excepto nombres de endpoints, variables y codigo que van en ingles |
| DOC-03 | Los ejemplos curl usan `http://localhost:8000` como base URL |
| DOC-04 | Los ejemplos curl usan placeholders descriptivos: `tu_user_api_key`, `tu_app_api_key` |
| DOC-05 | Preservar estructura existente del README si es consistente. Solo actualizar secciones cambiadas |
| DOC-06 | Los schemas Pydantic se documentan con todos sus campos, tipos, requeridos/opcionales y defaults |
| DOC-07 | Cada tabla de endpoints DEBE incluir columna Auth indicando que tipo de API Key require |
| DOC-08 | Los endpoints publicos (sin autenticacion) llevan "Ninguna" en la columna Auth |
| DOC-09 | Agrupar endpoints por route file (auth, logs, applications, stats, alerts, dashboard, health, etc.) |
| DOC-10 | Mantener el orden de las secciones del README consistente con la estructura actual |

### Reglas para README.md

| ID | Regla |
|----|-------|
| RM-01 | La seccion de Descripcion es un parrafo conciso |
| RM-02 | La tabla de Endpoint es resumida: Metodo, Ruta, Descripcion, Auth (una linea por endpoint) |
| RM-03 | La seccion de Instalacion y Desarrollo incluye comandos completos y probados |
| RM-04 | La tabla de Configuracion lista TODAS las variables con descripcion y default |
| RM-05 | La seccion de Docker incluye comandos de produccion y desarrollo |
| RM-06 | Preservar el changelog/historial de fases al final del README |

### Reglas para docs/api-reference.md

| ID | Regla |
|----|-------|
| AR-01 | Cada endpoint tiene su propia sub-seccion con titulo `### METHOD /api/v1/path` |
| AR-02 | Cada endpoint incluye: Descripcion, Autenticacion, Request Body (tabla), Response (con JSON ejemplo), Errores (tabla), Ejemplo curl |
| AR-03 | Los campos del Request Body se extraen directamente del schema Pydantic |
| AR-04 | Los campos opcionales se marcan con "(opcional)" y se incluye el default si existe |
| AR-05 | El Response JSON ejemplo usa valores representativos, no datos vacios |
| AR-06 | La tabla de Errores sigue el formato estandar de error codes de OnyxLog |
| AR-07 | Los grupos de endpoints siguen el mismo orden que los route files |
| AR-08 | Incluir tabla de contenidos al inicio con links a cada seccion |

---

## Formato: README.md

El README DEBE mantener la estructura general del archivo existente. Las secciones a actualizar son:

### Estructura esperada

```
# OnyxLog

## Descripcion

## Estado del Proyecto

## Stack Tecnologico

## Estructura del Proyecto

## Modelos de Datos

## Endpoints de la API

### [Grupo 1: Auth]
| Metodo | Ruta | Descripcion | Auth |
...

### [Grupo 2: Logs]
...

## Docker

## Instalacion y Desarrollo

## Configuracion

| Variable | Descripcion | Default |
...

## Autenticacion

## Documentacion

## [Changelog existente - NO MODIFICAR]
```

### Formato de tabla de endpoints en README

```markdown
### Autenticacion
| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/register` | Registrar nuevo usuario (admin) | Ninguna |
| POST | `/api/v1/auth/login` | Obtener API Key | Ninguna |
```

### Formato de tabla de configuracion en README

```markdown
| Variable | Descripcion | Default |
|----------|-------------|---------|
| `ONYXLOG_DATABASE_URL` | URL de conexion PostgreSQL | `postgresql+asyncpg://...` |
| `ONYXLOG_SECRET_KEY` | Clave secreta para JWT | `changeme-in-production` |
```

---

## Formato: docs/api-reference.md

### Estructura general

```markdown
# Referencia de API — OnyxLog

## Tabla de Contenidos

- [Autenticacion y API Keys](#autenticacion-y-api-keys)
- [Gestion de Aplicaciones](#gestion-de-aplicaciones)
- [Logs](#logs)
- [Estadisticas y Queries](#estadisticas-y-queries)
- ...

---

## Autenticacion y API Keys

### POST /api/v1/auth/register
Descripcion del endpoint.

**Autenticacion:** Ninguna (endpoint publico)

**Request Body:**
| Campo | Tipo | Requerido | Default | Descripcion |
|-------|------|-----------|---------|-------------|
| username | string | Si | - | Nombre de usuario unico |
| email | string | Si | - | Email del usuario |
| password | string | Si | - | Contrasena (min 8 caracteres) |

**Response 201:**
\```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "miuser",
  "email": "user@test.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
\```

**Errores:**
| HTTP | error_code | Condicion |
|------|------------|-----------|
| 400 | VALIDATION_ERROR | Datos invalidos |
| 409 | ALREADY_EXISTS | Username o email ya registrado |

**Ejemplo:**
\```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "miuser", "email": "user@test.com", "password": "secure123"}'
\```

---

### POST /api/v1/auth/login
...
```

### Formato de cada endpoint

Cada endpoint DEBE incluir TODOS estos elementos:

1. **Titulo**: `### METHOD /api/v1/path`
2. **Descripcion**: 1-2 lineas explicando que hace
3. **Autenticacion**: Tipo de auth requerida (Ninguna, User API Key, App API Key, Admin API Key)
4. **Request Body** (solo POST/PUT/PATCH): Tabla con Campo, Tipo, Requerido, Default, Descripcion
5. **Query Parameters** (si aplica): Tabla con Parametro, Tipo, Requerido, Default, Descripcion
6. **Path Parameters** (si aplica): Tabla con Parametro, Tipo, Descripcion
7. **Response**: Status code + JSON ejemplo con valores representativos
8. **Errores**: Tabla con HTTP, error_code, Condicion
9. **Ejemplo curl**: Comando curl completo y funcional

### Excepciones

- Endpoints GET sin request body omiten la seccion Request Body
- Endpoints DELETE con status 204 omiten el Response JSON
- Endpoints publicos indican "Ninguna (endpoint publico)" en Autenticacion

---

## Error Codes Estandar

Todos los errores de la API siguen esta estructura:

```json
{
  "message": "Descripcion legible del error",
  "error_code": "ERROR_CODE"
}
```

| HTTP | error_code | Uso |
|------|------------|-----|
| 400 | VALIDATION_ERROR | Datos invalidos o incompletos |
| 401 | AUTH_REQUIRED | API Key faltante |
| 403 | INVALID_API_KEY | API Key invalida o revocada |
| 404 | NOT_FOUND | Recurso no encontrado |
| 409 | ALREADY_EXISTS | Recurso duplicado |
| 422 | INVALID_CUSTOM_DATA | custom_data no pasa validacion |
| 429 | RATE_LIMITED | Rate limit excedido |
| 500 | INTERNAL_ERROR | Error inesperado del servidor |

---

## Flujo de Generacion

### Paso 1: Recopilar informacion

Leer TODAS las fuentes listadas en la seccion "Fuentes de Informacion" segun el modo:

- Para `readme`: leer todas las fuentes
- Para `api-reference`: enfocarse en sources de Endpoints
- Para `full`: leer todas las fuentes

### Paso 2: Generar README.md

1. Preservar la estructura existente del README
2. Actualizar las secciones que hayan cambiado:
   - Descripcion (si cambio el stack)
   - Estado del Proyecto (verificar contra STATE.md)
   - Stack Tecnologico (verificar contra pyproject.toml y architecture.md)
   - Estructura del Proyecto (verificar contra archivos reales)
   - Modelos de Datos (verificar contra IA/CONTEXT/models-reference.md)
   - Endpoints de la API (verificar contra routes/*.py)
   - Docker (verificar contra docker/)
   - Instalacion y Desarrollo (verificar contra requirements/ y Makefile)
   - Configuracion (verificar contra src/core/config.py)
   - Autenticacion (verificar contra auth.py y workflows-reference.md)
3. NUNCA modificar el changelog/historial al final del README

### Paso 3: Generar docs/api-reference.md

1. Crear tabla de contenidos con links
2. Para cada route file en `src/api/routes/`, generar la documentacion de sus endpoints
3. Para cada endpoint:
   a. Extraer metodo HTTP, ruta, response_model, status_code del decorador
   b. Extraer dependeencias de autenticacion del `Depends(get_current_user)` o similar
   c. Extraer request body schema del tipo del parametro
   d. Leer el schema Pydantic correspondiente para campos, tipos, defaults
   e. Extraer posibles errores de los HTTPException en el route o service
   f. Generar ejemplo curl con datos representativos
4. Ordenar grupos segun el orden de registro en `main.py`

### Paso 4: Actualizar contexto

Despues de generar la documentacion, actualizar:

- `IA/CONTEXT/endpoints-reference.md` si se encontraron endpoints nuevos o cambiados
- `IA/STATE.md` si la tarea de documentacion esta marcada como pendiente

### Paso 5: Verificar consistencia

Verificar que:

- Todo endpoint en routes/*.py aparece en el README y en api-reference.md
- Toda variable en config.py aparece en la tabla de configuracion del README
- Las dependencias en requirements/ coinciden con pyproject.toml
- Los error codes documentados coinciden con los usados en el codigo

---

## Nombres de Schemas por Route

Para mapear endpoints a schemas, usar esta referencia (se actualiza leyendo los schemas reales):

| Route | SchemasPydantic (?) |
|-------|---------------------|
| `auth.py` | `auth.py` (UserCreate, UserLogin, UserRead, ApiKeyCreate, ApiKeyRead, ViewerCreate) |
| `logs.py` | `log.py` (LogCreate, LogRead, LogQuery), `export.py` (ExportRequest), `retention.py` (RetentionPolicy*, RetentionStats) |
| `applications.py` | `application.py` (ApplicationCreate, ApplicationRead, ApplicationUpdate) |
| `stats.py` | `query.py` (LogQuery, StatsQuery), schemas de estadisticas |
| `alerts.py` | `alert.py` (AlertRuleCreate, AlertRuleRead, AlertRuleUpdate, AlertRead) |
| `dashboard.py` | `metrics.py` (MetricSummary, MetricTrends) |
| `health.py` | `health.py` (HealthResponse, ReadyResponse) |
| `info.py` | `info.py` (SystemInfo) |
| `config.py` | `config.py` (ConfigRead) |
| `metrics.py` | Sin schema (Prometheus format) |

---

## Notas Importantes

- NUNCA eliminar contenido existente del README que este correcto. Solo actualizar o agregar
- Los ejemplos curl deben ser completos y funcionales (con headers, body, URL)
- Para endpoints paginados, documentar los query parameters `page` y `page_size`
- Para endpoints con `PaginatedResponse[T]`, mostrar la estructura de respuesta paginada
- El WebSocket endpoint documenta parametros como query params (no body)
- El SSE endpoint documenta los filtros como query params