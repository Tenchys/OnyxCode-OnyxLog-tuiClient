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
