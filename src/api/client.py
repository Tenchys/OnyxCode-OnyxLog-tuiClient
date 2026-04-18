from __future__ import annotations

import httpx

from src.models.schemas import HealthResponse


class ApiClientError(Exception):
    def __init__(self, error_code: str, status_code: int, message: str) -> None:
        self.error_code = error_code
        self.status_code = status_code
        self.message = message
        super().__init__(f"[{status_code}] {error_code}: {message}")


class OnyxLogClient:
    BASE_PATH = "/api/v1"

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self._api_key: str | None = None

    async def close(self) -> None:
        await self._client.aclose()

    def set_api_key(self, key: str) -> None:
        self._api_key = key

    def clear_api_key(self) -> None:
        self._api_key = None

    @property
    def is_authenticated(self) -> bool:
        return self._api_key is not None

    @property
    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["X-API-Key"] = self._api_key
        return headers

    async def _request(
        self, method: str, path: str, *, skip_prefix: bool = False, **kwargs
    ) -> dict:
        if skip_prefix:
            url = path
        else:
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

    async def health_check(self) -> HealthResponse:
        data = await self._request("GET", "/health", skip_prefix=True)
        return HealthResponse(**data)

    async def __aenter__(self) -> OnyxLogClient:
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
