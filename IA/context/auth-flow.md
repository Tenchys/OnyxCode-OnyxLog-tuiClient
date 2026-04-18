# Flujo de Autenticacion

## Registro

```
POST /api/v1/auth/register
Body: { "username": "...", "email": "...", "password": "..." }
Response: { "user": {...}, "api_key": { "id": "...", "key": "onyx_...", "role": "admin" } }
```

El registro crea un usuario con rol `admin` y devuelve una API key de tipo `user`.

## Login

```
POST /api/v1/auth/login
Body: { "username": "...", "password": "..." }
Response: { "user": {...}, "api_key": { "id": "...", "key": "onyx_...", "role": "admin" } }
```

## Uso de API Key

Todas las requests autenticadas incluyen el header:

```
X-API-Key: <key>
```

## Almacenamiento Local

Tras registro/login, la API key se guarda en SQLite con metadatos:
- `key_type`: `user` o `application`
- `role`: `admin` o `viewer` (solo para tipo `user`)
- `server_url`: URL del servidor asociado
- `is_active`: marcada como activa

## Tipos de API Key

| Tipo | Obtenida via | Acceso |
|------|-------------|--------|
| `user` (admin) | Registro/Login | Todos los endpoints |
| `user` (viewer) | POST /auth/viewers | Solo lectura |
| `application` | POST /applications/{id}/keys | Logs, Stats, Custom metrics |