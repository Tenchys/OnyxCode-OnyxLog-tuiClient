---
name: onyxlog-tui-api-client
description: Patrones del cliente HTTP para OnyxLog TUI. httpx.AsyncClient, auth, headers, manejo de errores, endpoints y SSE streaming.
metadata:
  audience: developers
  workflow: onyxlog-tui
---

## Cliente base: OnyxLogClient

Clase central que envuelve `httpx.AsyncClient` con base_url configurable y header `X-API-Key`.

```python
from __future__ import annotations

import httpx


class ApiClientError(Exception):
    def __init__(self, error_code: str, status_code: int, message: str):
        self.error_code = error_code
        self.status_code = status_code
        self.message = message
        super().__init__(f"[{status_code}] {error_code}: {message}")


class OnyxLogClient:
    BASE_PATH = "/api/v1"

    def __init__(self, base_url: str = "http://localhost:8000"):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self._api_key: str | None = None

    async def close(self) -> None:
        await self._client.aclose()

    def set_api_key(self, key: str) -> None:
        self._api_key = key

    def clear_api_key(self) -> None:
        self._api_key = None

    @property
    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["X-API-Key"] = self._api_key
        return headers

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.BASE_PATH}{path}"
        try:
            response = await self._client.request(
                method, url, headers=self._headers, **kwargs
            )
        except httpx.ConnectError:
            raise ApiClientError("CONNECTION_ERROR", 0, "Cannot connect to server")
        except httpx.TimeoutException:
            raise ApiClientError("TIMEOUT", 0, "Request timed out")

        if response.status_code >= 400:
            try:
                data = response.json()
                error_code = data.get("error_code", "UNKNOWN_ERROR")
                message = data.get("message", response.text)
            except Exception:
                error_code = "UNKNOWN_ERROR"
                message = response.text
            raise ApiClientError(error_code, response.status_code, message)

        if response.status_code == 204:
            return {}
        return response.json()
```

## Modulos de API

Cada modulo agrupa endpoints por recurso. Importar y usar a traves de `OnyxLogClient`.

### auth.py — Registro y Login

```python
from __future__ import annotations

from src.models.schemas import UserWithKey


async def register(client: OnyxLogClient, username: str, email: str, password: str) -> UserWithKey:
    data = await client._request("POST", "/auth/register", json={
        "username": username, "email": email, "password": password,
    })
    return UserWithKey(**data)


async def login(client: OnyxLogClient, username: str, password: str) -> UserWithKey:
    data = await client._request("POST", "/auth/login", json={
        "username": username, "password": password,
    })
    return UserWithKey(**data)
```

### applications.py — CRUD de aplicaciones

```python
from __future__ import annotations

from src.models.schemas import AppRead, AppCreate, PaginatedResponse


async def list_applications(client: OnyxLogClient, page: int = 1, page_size: int = 50) -> PaginatedResponse[AppRead]:
    data = await client._request("GET", "/applications", params={"page": page, "page_size": page_size})
    return PaginatedResponse[AppRead](**data)


async def create_application(client: OnyxLogClient, app: AppCreate) -> AppRead:
    data = await client._request("POST", "/applications", json=app.model_dump())
    return AppRead(**data)


async def delete_application(client: OnyxLogClient, app_id: str) -> None:
    await client._request("DELETE", f"/applications/{app_id}")
```

### logs.py — Consulta de logs

```python
from __future__ import annotations

from src.models.schemas import LogRead, LogQuery, PaginatedResponse


async def get_logs(client: OnyxLogClient, query: LogQuery) -> PaginatedResponse[LogRead]:
    data = await client._request("POST", "/logs/query", json=query.model_dump(exclude_none=True))
    return PaginatedResponse[LogRead](**data)


async def get_log_by_id(client: OnyxLogClient, log_id: str) -> LogRead:
    data = await client._request("GET", f"/logs/{log_id}")
    return LogRead(**data)
```

## SSE Streaming (logs en tiempo real)

```python
import httpx
import json


async def stream_logs(client: OnyxLogClient, levels: list[str] | None = None):
    params = {}
    if levels:
        params["levels"] = ",".join(levels)

    headers = client._headers.copy()
    headers["Accept"] = "text/event-stream"

    async with client._client.stream("GET", f"{client.BASE_PATH}/logs/stream", params=params, headers=headers) as response:
        if response.status_code >= 400:
            raise ApiClientError("STREAM_ERROR", response.status_code, "Failed to connect to stream")
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                data = line[len("data:"):].strip()
                if data:
                    yield json.loads(data)
```

## Manejo de errores

La clase `ApiClientError` centraliza todos los errores HTTP:

| Escenario | Codigo | Accion en UI |
|-----------|--------|-------------|
| Sin conexion al servidor | `CONNECTION_ERROR` | Mostrar mensaje "Cannot connect" con boton retry |
| Timeout | `TIMEOUT` | Mostrar "Request timed out" |
| 401 INVALID_CREDENTIALS | 401 | Mostrar "Invalid credentials" en login |
| 403 INVALID_API_KEY | 403 | Limpiar key local, redirigir a login |
| 403 ADMIN_REQUIRED | 403 | Mostrar "Admin access required" |
| 404 *_NOT_FOUND | 404 | Mostrar "Resource not found" |
| 409 DUPLICATE_ENTRY | 409 | Mostrar "Already exists" |
| 422 VALIDATION_ERROR | 422 | Mostrar errores de validacion por campo |
| 429 RATE_LIMITED | 429 | Mostrar "Rate limit exceeded, try later" |

Patron en Screen:

```python
async def _load_data(self) -> None:
    try:
        result = await client.get_something()
    except ApiClientError as e:
        if e.error_code == "CONNECTION_ERROR":
            self.notify("Cannot connect to server. Check URL in Settings.", severity="error")
        elif e.error_code in ("INVALID_API_KEY",):
            await self.app.logout()
            self.app.push_screen(LoginScreen())
        else:
            self.notify(e.message, severity="error")
        return
```

## Health check

```python
async def health_check(client: OnyxLogClient) -> dict:
    data = await client._request("GET", "/health", skip_prefix=True)
    return data
```

Nota: El endpoint `/health` no usa el prefijo `/api/v1` ni requiere API key. Implementar soporte en `_request` con parametro `skip_prefix=True` o metodo separado.

## Patron de reintentos

```python
import asyncio


async def _request_with_retry(self, method: str, path: str, max_retries: int = 2, **kwargs) -> dict:
    for attempt in range(max_retries + 1):
        try:
            return await self._request(method, path, **kwargs)
        except ApiClientError as e:
            if e.error_code == "RATE_LIMITED" and attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
                continue
            raise
```