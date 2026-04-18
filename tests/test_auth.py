from __future__ import annotations

import httpx
import pytest

from src.api.auth import login, register
from src.api.client import ApiClientError, OnyxLogClient


def _make_handler(status_code: int, json_body: dict | None = None) -> httpx.Response:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body)

    return handler


@pytest.fixture
def auth_client() -> OnyxLogClient:
    transport = httpx.MockTransport(
        _make_handler(200, {"status": "ok", "version": "1.0.0"})
    )
    client = OnyxLogClient(base_url="http://testserver")
    client._client = httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    )
    return client


class TestRegister:
    @pytest.mark.asyncio
    async def test_register_success(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "testuser",
                        "email": "test@example.com",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2026-01-01T00:00:00Z",
                    },
                    "api_key": {
                        "id": "key-456",
                        "key": "sk_test_key_abc123",
                        "role": "user",
                    },
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await register(client, "testuser", "test@example.com", "password123")
        assert result.user.username == "testuser"
        assert result.user.email == "test@example.com"
        assert result.api_key.key == "sk_test_key_abc123"
        await client.close()

    @pytest.mark.asyncio
    async def test_register_validation_error(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                422,
                {
                    "error_code": "VALIDATION_ERROR",
                    "message": "Invalid input data",
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await register(client, "", "bad-email", "")
        assert exc_info.value.error_code == "VALIDATION_ERROR"
        assert exc_info.value.status_code == 422
        await client.close()

    @pytest.mark.asyncio
    async def test_register_duplicate_entry(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                409,
                {
                    "error_code": "DUPLICATE_ENTRY",
                    "message": "Username already exists",
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await register(client, "existinguser", "test@example.com", "password123")
        assert exc_info.value.error_code == "DUPLICATE_ENTRY"
        assert exc_info.value.status_code == 409
        await client.close()


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "testuser",
                        "email": "test@example.com",
                        "role": "admin",
                        "is_active": True,
                        "created_at": "2026-01-01T00:00:00Z",
                    },
                    "api_key": {
                        "id": "key-456",
                        "key": "sk_test_key_abc123",
                        "role": "admin",
                    },
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await login(client, "testuser", "password123")
        assert result.user.username == "testuser"
        assert result.user.role == "admin"
        assert result.api_key.role == "admin"
        await client.close()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                401,
                {
                    "error_code": "INVALID_CREDENTIALS",
                    "message": "Invalid credentials",
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await login(client, "wronguser", "wrongpassword")
        assert exc_info.value.error_code == "INVALID_CREDENTIALS"
        assert exc_info.value.status_code == 401
        await client.close()


class TestConnectionErrors:
    @pytest.mark.asyncio
    async def test_register_connection_error(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await register(client, "user", "test@example.com", "pass")
        assert exc_info.value.error_code == "CONNECTION_ERROR"
        await client.close()

    @pytest.mark.asyncio
    async def test_login_connection_error(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await login(client, "user", "pass")
        assert exc_info.value.error_code == "CONNECTION_ERROR"
        await client.close()

    @pytest.mark.asyncio
    async def test_register_timeout(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("Request timed out")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await register(client, "user", "test@example.com", "pass")
        assert exc_info.value.error_code == "TIMEOUT"
        await client.close()

    @pytest.mark.asyncio
    async def test_login_timeout(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("Request timed out")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await login(client, "user", "pass")
        assert exc_info.value.error_code == "TIMEOUT"
        await client.close()
