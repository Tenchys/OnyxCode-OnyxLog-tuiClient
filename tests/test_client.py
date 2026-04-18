from __future__ import annotations

import httpx
import pytest

from src.api.client import ApiClientError, OnyxLogClient
from src.models.schemas import HealthResponse


def _make_handler(status_code: int, json_body: dict | None = None) -> httpx.Response:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body)

    return handler


def _connection_error_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("Connection refused")


@pytest.fixture
def client() -> OnyxLogClient:
    transport = httpx.MockTransport(
        _make_handler(200, {"status": "ok", "version": "1.0.0"})
    )
    c = OnyxLogClient(base_url="http://testserver")
    c._client = httpx.AsyncClient(transport=transport, base_url="http://testserver")
    return c


class TestOnyxLogClientInit:
    async def test_client_init(self) -> None:
        c = OnyxLogClient(base_url="http://custom:9000")
        assert c._client.base_url == "http://custom:9000"
        await c.close()


class TestHeaders:
    async def test_headers_without_api_key(self, client: OnyxLogClient) -> None:
        headers = client._headers
        assert headers == {"Content-Type": "application/json"}
        assert "X-API-Key" not in headers

    async def test_headers_with_api_key(self, client: OnyxLogClient) -> None:
        client.set_api_key("test-key-123")
        headers = client._headers
        assert headers == {
            "Content-Type": "application/json",
            "X-API-Key": "test-key-123",
        }

    async def test_set_and_clear_api_key(self, client: OnyxLogClient) -> None:
        client.set_api_key("test-key-123")
        assert client._api_key == "test-key-123"
        client.clear_api_key()
        assert client._api_key is None

    async def test_is_authenticated(self, client: OnyxLogClient) -> None:
        assert client.is_authenticated is False
        client.set_api_key("test-key-123")
        assert client.is_authenticated is True
        client.clear_api_key()
        assert client.is_authenticated is False


class TestHealthCheck:
    async def test_health_check_success(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(200, {"status": "ok", "version": "1.0.0"})
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await client.health_check()
        assert isinstance(result, HealthResponse)
        assert result.status == "ok"
        assert result.version == "1.0.0"
        await client.close()


class TestRequest:
    async def test_request_get_success(self) -> None:
        transport = httpx.MockTransport(_make_handler(200, {"data": "test"}))
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await client._request("GET", "/test")
        assert result == {"data": "test"}
        await client.close()

    async def test_request_post_success_with_body(self) -> None:
        transport = httpx.MockTransport(_make_handler(200, {"id": "123"}))
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await client._request("POST", "/test", json={"name": "test"})
        assert result == {"id": "123"}
        await client.close()

    async def test_request_skip_prefix(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/health"
            return httpx.Response(200, json={"status": "ok"})

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await client._request("GET", "/health", skip_prefix=True)
        assert result == {"status": "ok"}
        await client.close()


class TestErrorResponses:
    async def test_request_401_invalid_credentials(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                401,
                {"error_code": "INVALID_CREDENTIALS", "message": "Invalid credentials"},
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        try:
            await client._request(
                "POST", "/auth/login", json={"username": "wrong", "password": "wrong"}
            )
            pytest.fail("Should have raised ApiClientError")
        except ApiClientError as e:
            assert e.error_code == "INVALID_CREDENTIALS"
            assert e.status_code == 401
            assert e.message == "Invalid credentials"
        await client.close()

    async def test_request_403_invalid_api_key(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                403,
                {
                    "error_code": "INVALID_API_KEY",
                    "message": "Invalid or revoked API key",
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        try:
            await client._request("GET", "/applications")
            pytest.fail("Should have raised ApiClientError")
        except ApiClientError as e:
            assert e.error_code == "INVALID_API_KEY"
            assert e.status_code == 403
        await client.close()

    async def test_request_404_not_found(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                404,
                {
                    "error_code": "APPLICATION_NOT_FOUND",
                    "message": "Application not found",
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        try:
            await client._request("GET", "/applications/nonexistent")
            pytest.fail("Should have raised ApiClientError")
        except ApiClientError as e:
            assert e.error_code == "APPLICATION_NOT_FOUND"
            assert e.status_code == 404
        await client.close()

    async def test_request_409_duplicate_entry(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                409,
                {"error_code": "DUPLICATE_ENTRY", "message": "Username already exists"},
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        try:
            await client._request(
                "POST",
                "/auth/register",
                json={
                    "username": "existing",
                    "email": "test@test.com",
                    "password": "test",
                },
            )
            pytest.fail("Should have raised ApiClientError")
        except ApiClientError as e:
            assert e.error_code == "DUPLICATE_ENTRY"
            assert e.status_code == 409
        await client.close()

    async def test_request_422_validation_error(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                422, {"error_code": "VALIDATION_ERROR", "message": "Invalid input data"}
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        try:
            await client._request("POST", "/applications", json={})
            pytest.fail("Should have raised ApiClientError")
        except ApiClientError as e:
            assert e.error_code == "VALIDATION_ERROR"
            assert e.status_code == 422
        await client.close()

    async def test_request_429_rate_limited(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                429, {"error_code": "RATE_LIMITED", "message": "Too many requests"}
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        try:
            await client._request("GET", "/logs")
            pytest.fail("Should have raised ApiClientError")
        except ApiClientError as e:
            assert e.error_code == "RATE_LIMITED"
            assert e.status_code == 429
        await client.close()

    async def test_request_500_internal_error(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                500,
                {"error_code": "INTERNAL_ERROR", "message": "Internal server error"},
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        try:
            await client._request("GET", "/health")
            pytest.fail("Should have raised ApiClientError")
        except ApiClientError as e:
            assert e.error_code == "INTERNAL_ERROR"
            assert e.status_code == 500
        await client.close()


class TestConnectionErrors:
    async def test_connection_error(self) -> None:
        transport = httpx.MockTransport(_connection_error_handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        try:
            await client._request("GET", "/health")
            pytest.fail("Should have raised ApiClientError")
        except ApiClientError as e:
            assert e.error_code == "CONNECTION_ERROR"
            assert e.status_code == 0
            assert e.message == "Cannot connect to server"
        await client.close()

    async def test_timeout_error(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("Request timed out")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        try:
            await client._request("GET", "/health")
            pytest.fail("Should have raised ApiClientError")
        except ApiClientError as e:
            assert e.error_code == "TIMEOUT"
            assert e.status_code == 0
            assert e.message == "Request timed out"
        await client.close()


class TestContextManager:
    async def test_context_manager(self) -> None:
        async with OnyxLogClient(base_url="http://testserver") as client:
            assert isinstance(client, OnyxLogClient)
            assert client.is_authenticated is False


class TestStatus204:
    async def test_status_204_returns_empty_dict(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(204)

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await client._request("DELETE", "/logs/123")
        assert result == {}
        await client.close()
