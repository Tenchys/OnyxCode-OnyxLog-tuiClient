# OnyxLog TUI Client

Terminal UI client for OnyxLog log management system.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
onyxlog-tui
```

With custom server URL:

```bash
onyxlog-tui --url http://host:8000
```

## Configuration

The OnyxLog TUI Client uses a priority-based configuration system:

**Priority: CLI flag > environment variable > config file > default**

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ONYXLOG_URL` | Server URL | `http://localhost:8000` |

### Config File

The config file is located at `~/.onyxlog/config.toml` and uses the TOML format:

```toml
[server]
url = "http://localhost:8000"
```

The config directory `~/.onyxlog/` is created automatically if it doesn't exist.

## Data Models

The TUI uses Pydantic v2 models for data validation and serialization:

| Model | Purpose |
|-------|---------|
| `UserCreate` | User registration input |
| `UserRead` | User data returned from API |
| `UserWithKey` | Combined user + API key from auth endpoints |
| `LoginRequest` | Login credentials |
| `AppCreate` | Application creation input |
| `AppRead` | Application data returned from API |
| `AppUpdate` | Application update input (all fields optional) |
| `LogRead` | Log entry returned from API |
| `LogCreate` | Log entry creation input |
| `LogQuery` | Query parameters for log search |
| `ApiKeyRead` | API key metadata from API |
| `ApiKeyCreate` | API key creation input |
| `ApiKeyCreateResponse` | API key creation response with key value |
| `AuthApiKeyResponse` | API key nested in auth response |
| `PaginatedResponse[T]` | Generic paginated list response |
| `ErrorResponse` | API error response |
| `HealthResponse` | Server health check response |
| `StatsOverview` | Dashboard statistics |
| `LogLevel` | Enum for log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

## API Client

The `OnyxLogClient` class is the central HTTP client for communicating with the OnyxLog server.

### OnyxLogClient

```python
from src.api.client import OnyxLogClient, ApiClientError

# Using context manager (recommended)
async with OnyxLogClient(base_url="http://localhost:8000") as client:
    client.set_api_key("your-api-key")
    
    # Health check (no auth required)
    health = await client.health_check()
    print(f"Server: {health.status} v{health.version}")
    
    # Authenticated requests
    response = await client._request("GET", "/applications")
```

### ApiClientError

All HTTP errors are wrapped in `ApiClientError` with structured error codes:

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 401 | `INVALID_CREDENTIALS` | Login failed |
| 403 | `INVALID_API_KEY` | API key invalid or revoked |
| 404 | `*_NOT_FOUND` | Resource not found |
| 409 | `DUPLICATE_ENTRY` | Username/email/app_id already exists |
| 422 | `VALIDATION_ERROR` | Invalid input data |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |
| Connection failed | `CONNECTION_ERROR` | Cannot connect to server |
| Timeout | `TIMEOUT` | Request timed out |

```python
try:
    await client._request("POST", "/auth/login", json={"username": "user", "password": "pass"})
except ApiClientError as e:
    print(f"Error [{e.status_code}]: {e.message}")
    if e.error_code == "INVALID_CREDENTIALS":
        # Handle login failure
        pass
```

### Context Manager Pattern

```python
async with OnyxLogClient() as client:
    client.set_api_key(api_key)
    # Use client...
# Connection automatically closed
```

### Health Check

```python
health = await client.health_check()
# Returns HealthResponse(status="ok", version="1.0.0")
```

## Authentication

The `src/api/auth.py` module provides `register()` and `login()` functions.

### Register

```python
from src.api.auth import register
from src.api.client import OnyxLogClient

async with OnyxLogClient() as client:
    user_with_key = await register(
        client,
        username="newuser",
        email="user@example.com",
        password="securepassword",
    )
    print(f"User: {user_with_key.user.username}")
    print(f"API Key: {user_with_key.api_key.key}")
```

### Login

```python
from src.api.auth import login
from src.api.client import OnyxLogClient

async with OnyxLogClient() as client:
    user_with_key = await login(client, username="existinguser", password="password")
    client.set_api_key(user_with_key.api_key.key)
```

### Return Value

Both functions return `UserWithKey` containing:

- `user`: `UserRead` with id, username, email, role, is_active, created_at
- `api_key`: `AuthApiKeyResponse` with id, key, role

## Local Database

The TUI stores API keys locally in a SQLite database for convenience and security.

### Database Location

Default path: `~/.onyxlog/keys.db`

### Schema

```sql
CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    key TEXT NOT NULL,
    key_type TEXT NOT NULL,   -- 'user' | 'application'
    role TEXT,                 -- 'admin' | 'viewer' (user only)
    user_id TEXT,
    app_id TEXT,
    server_url TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER DEFAULT 1
);
```

### Available Operations

```python
from src.db import init_db, store_key, get_active_key, list_keys, delete_key, deactivate_key

# Initialize database (creates table if not exists)
await init_db()

# Store a new API key
await store_key(
    id="key-1",
    name="My API Key",
    key="sk-xxxxx",
    key_type="user",
    server_url="http://localhost:8000",
    role="admin",
    user_id="user-123",
)

# Get active key for a server
key = await get_active_key("http://localhost:8000")
if key:
    print(f"Active key: {key['name']}")

# List all keys or filter by server
all_keys = await list_keys()
server_keys = await list_keys(server_url="http://localhost:8000")

# Deactivate a key (soft delete)
await deactivate_key("key-1")

# Permanently delete a key
await delete_key("key-1")
```

### Security

- API keys are stored **only** in the local SQLite database
- API keys are **never** stored in plain text config files or environment variables
- The database file is stored in the user's home directory with default filesystem permissions

## Login Screen

The `LoginScreen` is the first screen shown when the TUI starts. It provides both login and registration functionality.

### Features

- **Login**: Authenticate with username and password
- **Register**: Create a new account with username, email, and password
- **Form Validation**: Required fields are validated before submission
- **Error Handling**: User-friendly error messages for all failure scenarios

### Error Messages

| Error Code | User Message |
|------------|-------------|
| `INVALID_CREDENTIALS` | Invalid username or password |
| `DUPLICATE_ENTRY` | Username or email already exists |
| `CONNECTION_ERROR` | Cannot connect to server. Check URL and try again. |
| `VALIDATION_ERROR` | Please check the form fields. |
| `TIMEOUT` | Server is taking too long to respond. |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Submit login form |
| `q` | Quit the application |

### Login Flow

1. User enters username and password
2. On login success: API key is stored in local SQLite database and dashboard is shown
3. On login failure: Error notification is displayed

### Register Flow

1. User enters username, email, and password
2. On registration success: Account is created, API key is stored, and dashboard is shown
3. On registration failure: Error notification is displayed

## App Shell (OnyxLogApp)

The `OnyxLogApp` class is the main application entry point that manages the TUI lifecycle.

### OnyxLogApp

```python
from src.app import OnyxLogApp

app = OnyxLogApp()
app.run()
```

### Auto-Login Flow

On application startup, `OnyxLogApp` attempts auto-login:

1. Initialize local SQLite database (`init_db()`)
2. Check for active API key in local database (`get_active_key()`)
3. If no key found → show `LoginScreen`
4. If key found:
   - Set API key on client (`client.set_api_key(key)`)
   - Attempt health check (`client.health_check()`)
   - On success → show `DashboardScreen`
   - On failure → show `LoginScreen`

### Key Bindings

| Binding | Action | Description |
|---------|--------|-------------|
| `Ctrl+Q` | `quit` | Exit the application |
| `Ctrl+C` | `quit` | Exit the application |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `client` | `OnyxLogClient` | HTTP client for API communication |
| `settings` | `Settings` | Application configuration |

### CSS

The app uses `styles.tcss` for styling. See `src/styles.tcss` for available styles.

## Dashboard Screen

The `DashboardScreen` is the main screen shown after successful login. It provides navigation to all TUI features and displays system statistics.

### Navigation Menu

The dashboard provides a navigation menu with three main options:

- **Applications**: Manage applications and API keys
- **Logs**: View and filter log entries
- **Settings**: Configure server URL, manage API keys, logout

### Statistics Overview

The dashboard automatically loads and displays system statistics from the server:

- **Total Logs**: Total number of log entries in the system
- **Total Applications**: Total number of registered applications
- **Active Applications**: Number of currently active applications
- **Recent Logs (24h)**: Number of log entries from the last 24 hours

Stats are loaded on mount using `GET /api/v1/stats/overview`. If the server is unreachable, "Unable to load stats" is displayed.

### Key Bindings

| Key | Action | Description |
|-----|--------|-------------|
| `a` | `go_applications` | Navigate to Applications screen |
| `l` | `go_logs` | Navigate to Logs screen |
| `s` | `go_settings` | Navigate to Settings screen |
| `q` | `quit` | Exit the application |
| `Escape` | `go_back` | Go back to previous screen |

### Screen Layout

```
┌─────────────────────────────────────────────┐
│                 OnyxLog                      │
├─────────────────────────────────────────────┤
│                                             │
│            OnyxLog Dashboard                 │
│                                             │
│  Navigation                                 │
│  [Applications] [Logs] [Settings]           │
│                                             │
│  Statistics Overview                        │
│    Total Logs:       1,000                  │
│    Total Applications: 5                    │
│    Active Applications: 3                   │
│    Recent Logs (24h): 250                   │
│                                             │
├─────────────────────────────────────────────┤
│  a: apps  l: logs  s: settings  q: quit     │
└─────────────────────────────────────────────┘
```

## Development

Run tests:

```bash
pytest tests/ -v
```

Run lint:

```bash
ruff check src/ tests/
```

Format code:

```bash
ruff format src/ tests/
```
