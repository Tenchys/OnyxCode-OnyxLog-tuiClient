# API de OnyxLog — Referencia Rapida

Ver **`docs/api-reference.md`** para detalles completos con ejemplos curl.

## Endpoints

| Categoria | Endpoint | Metodo | Auth |
|-----------|----------|--------|------|
| Auth | `/api/v1/auth/register` | POST | Ninguna |
| Auth | `/api/v1/auth/login` | POST | Ninguna |
| Auth | `/api/v1/auth/viewers` | POST | User API Key |
| Auth | `/api/v1/auth/keys` | GET/POST | User API Key |
| Auth | `/api/v1/auth/keys/{id}` | DELETE | User API Key |
| Apps | `/api/v1/applications` | GET/POST | User API Key |
| Apps | `/api/v1/applications/{id}` | GET/PUT/DELETE | User API Key |
| Apps | `/api/v1/applications/{id}/keys` | GET/POST | User API Key |
| Logs | `/api/v1/logs` | GET/POST | App API Key |
| Logs | `/api/v1/logs/query` | POST | App API Key |
| Logs | `/api/v1/logs/export` | POST | App API Key |
| Logs | `/api/v1/logs/stream` | GET (SSE) | User API Key |
| Logs | `/api/v1/logs/{id}` | GET | App API Key |
| Stats | `/api/v1/stats/summary` | GET | App API Key |
| Stats | `/api/v1/stats/overview` | GET | User/App API Key |
| Stats | `/api/v1/stats/custom` | POST | App API Key |
| Metrics | `/api/v1/metrics/summary` | GET | User API Key |
| Metrics | `/api/v1/metrics/trends` | GET | User API Key |
| Alerts | `/api/v1/alerts` | GET/POST | User API Key |
| Alerts | `/api/v1/alerts/{id}` | GET/PUT/DELETE | User API Key |
| Alerts | `/api/v1/alerts/active` | GET | User API Key |
| Health | `/health` | GET | Ninguna |

## Codigos de Error Estandar

| HTTP | Codigo | Significado |
|------|--------|-------------|
| 401 | INVALID_CREDENTIALS | Login fallido |
| 403 | INVALID_API_KEY | API key invalida/revocada |
| 403 | ADMIN_REQUIRED | Requiere rol admin |
| 404 | *_NOT_FOUND | Recurso no encontrado |
| 409 | DUPLICATE_ENTRY | Username/email/app_id duplicado |
| 422 | VALIDATION_ERROR | Datos invalidos |
| 429 | RATE_LIMITED | Rate limit excedido |