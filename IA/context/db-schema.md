# Base de Datos Local (SQLite)

Usa **aiosqlite** para todas las operaciones. La DB se inicializa con `init_db()` en `src/db.py`.

## Tabla: api_keys

```sql
CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    key TEXT NOT NULL,
    key_type TEXT NOT NULL,   -- 'user' | 'application'
    role TEXT,                 -- 'admin' | 'viewer' (solo user)
    user_id TEXT,
    app_id TEXT,
    server_url TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER DEFAULT 1
);
```

## Columnas

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `id` | TEXT PK | UUID de la API key |
| `name` | TEXT | Nombre descriptivo |
| `key` | TEXT | Valor de la API key (secreto) |
| `key_type` | TEXT | `user` o `application` |
| `role` | TEXT | `admin` o `viewer` (solo tipo `user`) |
| `user_id` | TEXT | ID del usuario propietario |
| `app_id` | TEXT | ID de la aplicacion (solo tipo `application`) |
| `server_url` | TEXT | URL del servidor OnyxLog asociado |
| `created_at` | TEXT | ISO 8601 timestamp |
| `is_active` | INTEGER | 1=activa, 0=revocada |

## Reglas

- Las API keys se almacenan **SOLO** en SQLite local, nunca en archivos de texto plano.
- Cada key esta asociada a un `server_url` para soportar multiples servidores.