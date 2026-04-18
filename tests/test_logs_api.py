from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import httpx
import pytest

from src.api.client import ApiClientError, OnyxLogClient
from src.api.logs import get_log_by_id, get_logs, query_logs
from src.models.schemas import LogQuery


def _make_handler(status_code: int, json_body: dict | list | None = None):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body)

    return handler


def _log_read_dict(
    log_id: str = "550e8400-e29b-41d4-a716-446655440000",
    level: str = "INFO",
    app_id: str = "test-app",
    message: str = "Test log message",
) -> dict:
    return {
        "id": log_id,
        "timestamp": "2026-01-01T00:00:00Z",
        "level": level,
        "app_id": app_id,
        "message": message,
        "metadata": None,
    }


class TestGetLogs:
    @pytest.mark.asyncio
    async def test_get_logs_success(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "items": [_log_read_dict()],
                    "total": 1,
                    "limit": 100,
                    "offset": 0,
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await get_logs(client)
        assert len(result.items) == 1
        assert result.items[0].message == "Test log message"
        assert result.total == 1
        await client.close()

    @pytest.mark.asyncio
    async def test_get_logs_pagination(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "items": [_log_read_dict()],
                    "total": 100,
                    "limit": 10,
                    "offset": 20,
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await get_logs(client, limit=10, offset=20)
        assert result.limit == 10
        assert result.offset == 20
        assert result.total == 100
        await client.close()

    @pytest.mark.asyncio
    async def test_get_logs_sends_limit_and_offset_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/api/v1/logs"
            assert request.url.params.get("limit") == "10"
            assert request.url.params.get("offset") == "20"
            return httpx.Response(
                200,
                json={
                    "items": [_log_read_dict()],
                    "total": 100,
                    "limit": 10,
                    "offset": 20,
                },
            )

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await get_logs(client, limit=10, offset=20)
        assert result.limit == 10
        assert result.offset == 20
        await client.close()

    @pytest.mark.asyncio
    async def test_get_logs_empty(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(200, {"items": [], "total": 0, "limit": 100, "offset": 0})
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await get_logs(client)
        assert len(result.items) == 0
        assert result.total == 0
        await client.close()


class TestGetLogById:
    @pytest.mark.asyncio
    async def test_get_log_by_id_success(self) -> None:
        log_id = str(uuid.uuid4())
        transport = httpx.MockTransport(
            _make_handler(200, _log_read_dict(log_id=log_id))
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await get_log_by_id(client, log_id)
        assert str(result.id) == log_id
        await client.close()

    @pytest.mark.asyncio
    async def test_get_log_by_id_not_found(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                404,
                {
                    "error_code": "LOG_NOT_FOUND",
                    "message": "Log entry not found",
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await get_log_by_id(client, "nonexistent-id")
        assert exc_info.value.error_code == "LOG_NOT_FOUND"
        assert exc_info.value.status_code == 404
        await client.close()


class TestQueryLogs:
    @pytest.mark.asyncio
    async def test_query_logs_by_level(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "items": [_log_read_dict(level="ERROR")],
                    "total": 1,
                    "limit": 100,
                    "offset": 0,
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        query = LogQuery(level="ERROR")
        result = await query_logs(client, query)
        assert len(result.items) == 1
        assert result.items[0].level == "ERROR"
        await client.close()

    @pytest.mark.asyncio
    async def test_query_logs_by_app_id(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "items": [_log_read_dict(app_id="my-app")],
                    "total": 1,
                    "limit": 100,
                    "offset": 0,
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        query = LogQuery(app_id="my-app")
        result = await query_logs(client, query)
        assert len(result.items) == 1
        assert result.items[0].app_id == "my-app"
        await client.close()

    @pytest.mark.asyncio
    async def test_query_logs_with_timeframe(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "items": [_log_read_dict()],
                    "total": 1,
                    "limit": 100,
                    "offset": 0,
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)  # noqa: UP017
        end = datetime(2026, 1, 2, tzinfo=timezone.utc)  # noqa: UP017
        query = LogQuery(start_time=start, end_time=end)
        result = await query_logs(client, query)
        assert len(result.items) == 1
        await client.close()

    @pytest.mark.asyncio
    async def test_query_logs_serializes_filters_payload(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)  # noqa: UP017
        end = datetime(2026, 1, 2, tzinfo=timezone.utc)  # noqa: UP017

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/api/v1/logs/query"
            payload = json.loads(request.content.decode())
            assert payload == {
                "app_id": "my-app",
                "level": "ERROR",
                "start_time": "2026-01-01T00:00:00+00:00",
                "end_time": "2026-01-02T00:00:00+00:00",
                "search": "failed",
                "limit": 25,
                "offset": 10,
            }
            return httpx.Response(
                200,
                json={
                    "items": [_log_read_dict(level="ERROR", app_id="my-app")],
                    "total": 1,
                    "limit": 25,
                    "offset": 10,
                },
            )

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        query = LogQuery(
            app_id="my-app",
            level="ERROR",
            start_time=start,
            end_time=end,
            search="failed",
            limit=25,
            offset=10,
        )
        result = await query_logs(client, query)
        assert len(result.items) == 1
        assert result.limit == 25
        assert result.offset == 10
        await client.close()

    @pytest.mark.asyncio
    async def test_query_logs_with_search(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "items": [_log_read_dict(message="User login successful")],
                    "total": 1,
                    "limit": 100,
                    "offset": 0,
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        query = LogQuery(search="login")
        result = await query_logs(client, query)
        assert len(result.items) == 1
        assert "login" in result.items[0].message
        await client.close()

    @pytest.mark.asyncio
    async def test_query_logs_combined_filters(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "items": [_log_read_dict(level="WARNING", app_id="prod-app")],
                    "total": 1,
                    "limit": 50,
                    "offset": 0,
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        query = LogQuery(app_id="prod-app", level="WARNING", limit=50)
        result = await query_logs(client, query)
        assert len(result.items) == 1
        assert result.items[0].app_id == "prod-app"
        assert result.items[0].level == "WARNING"
        await client.close()

    @pytest.mark.asyncio
    async def test_query_logs_empty_result(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(200, {"items": [], "total": 0, "limit": 100, "offset": 0})
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        query = LogQuery(app_id="nonexistent-app")
        result = await query_logs(client, query)
        assert len(result.items) == 0
        assert result.total == 0
        await client.close()


class TestConnectionErrors:
    @pytest.mark.asyncio
    async def test_get_logs_connection_error(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await get_logs(client)
        assert exc_info.value.error_code == "CONNECTION_ERROR"
        await client.close()

    @pytest.mark.asyncio
    async def test_get_log_by_id_connection_error(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await get_log_by_id(client, "some-id")
        assert exc_info.value.error_code == "CONNECTION_ERROR"
        await client.close()

    @pytest.mark.asyncio
    async def test_query_logs_connection_error(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await query_logs(client, LogQuery())
        assert exc_info.value.error_code == "CONNECTION_ERROR"
        await client.close()

    @pytest.mark.asyncio
    async def test_get_logs_timeout(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("Request timed out")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await get_logs(client)
        assert exc_info.value.error_code == "TIMEOUT"
        await client.close()
