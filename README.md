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
