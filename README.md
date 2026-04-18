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
