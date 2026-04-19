from __future__ import annotations

import uuid

import httpx
import pytest

from src.api.applications import (
    create_app_key,
    create_application,
    delete_application,
    get_application,
    list_app_keys,
    list_applications,
    update_application,
)
from src.api.client import ApiClientError, OnyxLogClient
from src.models.schemas import ApiKeyCreate


def _make_handler(status_code: int, json_body: dict | list | None = None):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body)

    return handler


def _app_read_dict(
    app_id: str = "550e8400-e29b-41d4-a716-446655440000",
    name: str = "TestApp",
    environment: str = "production",
) -> dict:
    return {
        "id": app_id,
        "name": name,
        "app_id": "test-app",
        "description": "Test application",
        "environment": environment,
        "is_active": True,
        "created_at": "2026-01-01T00:00:00Z",
    }


class TestListApplications:
    @pytest.mark.asyncio
    async def test_list_applications_success(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "items": [_app_read_dict()],
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
        result = await list_applications(client)
        assert len(result.items) == 1
        assert result.items[0].name == "TestApp"
        assert result.total == 1
        await client.close()

    @pytest.mark.asyncio
    async def test_list_applications_pagination(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "items": [_app_read_dict()],
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
        result = await list_applications(client, limit=10, offset=20)
        assert result.limit == 10
        assert result.offset == 20
        assert result.total == 100
        await client.close()

    @pytest.mark.asyncio
    async def test_list_applications_empty(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(200, {"items": [], "total": 0, "limit": 50, "offset": 0})
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await list_applications(client)
        assert len(result.items) == 0
        assert result.total == 0
        await client.close()

    @pytest.mark.asyncio
    async def test_list_applications_accepts_plain_list_response(self) -> None:
        transport = httpx.MockTransport(_make_handler(200, [_app_read_dict()]))
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await list_applications(client)
        assert len(result.items) == 1
        assert result.total == 1
        assert result.items[0].app_id == "test-app"
        await client.close()


class TestCreateApplication:
    @pytest.mark.asyncio
    async def test_create_application_success(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(200, _app_read_dict(name="NewApp"))
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        from src.models.schemas import AppCreate

        app = AppCreate(name="NewApp", app_id="new-app", environment="production")
        result = await create_application(client, app)
        assert result.name == "NewApp"
        await client.close()

    @pytest.mark.asyncio
    async def test_create_application_duplicate(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                409,
                {
                    "error_code": "DUPLICATE_ENTRY",
                    "message": "Application ID already exists",
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        from src.models.schemas import AppCreate

        app = AppCreate(name="DupApp", app_id="dup-app", environment="production")
        with pytest.raises(ApiClientError) as exc_info:
            await create_application(client, app)
        assert exc_info.value.error_code == "DUPLICATE_ENTRY"
        await client.close()


class TestGetApplication:
    @pytest.mark.asyncio
    async def test_get_application_success(self) -> None:
        app_id = str(uuid.uuid4())
        transport = httpx.MockTransport(
            _make_handler(200, _app_read_dict(app_id=app_id))
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await get_application(client, app_id)
        assert str(result.id) == app_id
        await client.close()

    @pytest.mark.asyncio
    async def test_get_application_not_found(self) -> None:
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
        with pytest.raises(ApiClientError) as exc_info:
            await get_application(client, "nonexistent-id")
        assert exc_info.value.error_code == "APPLICATION_NOT_FOUND"
        assert exc_info.value.status_code == 404
        await client.close()


class TestUpdateApplication:
    @pytest.mark.asyncio
    async def test_update_application_success(self) -> None:
        app_id = str(uuid.uuid4())
        transport = httpx.MockTransport(
            _make_handler(200, _app_read_dict(app_id=app_id, name="UpdatedApp"))
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        from src.models.schemas import AppUpdate

        update = AppUpdate(name="UpdatedApp")
        result = await update_application(client, app_id, update)
        assert result.name == "UpdatedApp"
        await client.close()

    @pytest.mark.asyncio
    async def test_update_application_not_found(self) -> None:
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
        from src.models.schemas import AppUpdate

        with pytest.raises(ApiClientError) as exc_info:
            await update_application(client, "nonexistent-id", AppUpdate(name="Test"))
        assert exc_info.value.error_code == "APPLICATION_NOT_FOUND"
        await client.close()


class TestDeleteApplication:
    @pytest.mark.asyncio
    async def test_delete_application_success(self) -> None:
        transport = httpx.MockTransport(_make_handler(204))
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        await delete_application(client, "some-app-id")
        await client.close()

    @pytest.mark.asyncio
    async def test_delete_application_not_found(self) -> None:
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
        with pytest.raises(ApiClientError) as exc_info:
            await delete_application(client, "nonexistent-id")
        assert exc_info.value.error_code == "APPLICATION_NOT_FOUND"
        await client.close()


class TestAppKeys:
    @pytest.mark.asyncio
    async def test_list_app_keys_success(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                [
                    {
                        "id": "key-1",
                        "name": "Test Key",
                        "key_type": "app",
                        "role": None,
                        "user_id": None,
                        "app_id": "test-app",
                        "created_at": "2026-01-01T00:00:00Z",
                        "is_active": True,
                    }
                ],
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        result = await list_app_keys(client, "test-app")
        assert len(result) == 1
        assert result[0].name == "Test Key"
        await client.close()

    @pytest.mark.asyncio
    async def test_create_app_key_success(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "id": "key-new",
                    "name": "New Key",
                    "key": "ak_new_key_123",
                    "key_type": "app",
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        key = ApiKeyCreate(name="New Key", key_type="app")
        result = await create_app_key(client, "test-app", key)
        assert result.name == "New Key"
        assert result.key == "ak_new_key_123"
        await client.close()

    @pytest.mark.asyncio
    async def test_create_app_key_duplicate(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                409,
                {
                    "error_code": "DUPLICATE_ENTRY",
                    "message": "API key name already exists",
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        key = ApiKeyCreate(name="Duplicate Key", key_type="app")
        with pytest.raises(ApiClientError) as exc_info:
            await create_app_key(client, "test-app", key)
        assert exc_info.value.error_code == "DUPLICATE_ENTRY"
        await client.close()

    @pytest.mark.asyncio
    async def test_create_app_key_accepts_api_key_only_response(self) -> None:
        transport = httpx.MockTransport(
            _make_handler(
                200,
                {
                    "api_key": "ak_only_value_123",
                    "created_at": "2026-01-01T00:00:00Z",
                },
            )
        )
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        key = ApiKeyCreate(name="Only Value", key_type="application")
        result = await create_app_key(client, "test-app", key)
        assert result.key == "ak_only_value_123"
        assert result.name == "Only Value"
        assert result.key_type == "application"
        await client.close()


class TestConnectionErrors:
    @pytest.mark.asyncio
    async def test_list_applications_connection_error(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        with pytest.raises(ApiClientError) as exc_info:
            await list_applications(client)
        assert exc_info.value.error_code == "CONNECTION_ERROR"
        await client.close()

    @pytest.mark.asyncio
    async def test_create_application_timeout(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("Request timed out")

        transport = httpx.MockTransport(handler)
        client = OnyxLogClient(base_url="http://testserver")
        client._client = httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        )
        from src.models.schemas import AppCreate

        with pytest.raises(ApiClientError) as exc_info:
            await create_application(
                client, AppCreate(name="T", app_id="t", environment="prod")
            )
        assert exc_info.value.error_code == "TIMEOUT"
        await client.close()
