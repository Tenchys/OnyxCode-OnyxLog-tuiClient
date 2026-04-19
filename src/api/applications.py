from __future__ import annotations

from src.api.client import OnyxLogClient
from src.models.schemas import (
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyRead,
    AppCreate,
    AppRead,
    AppUpdate,
    PaginatedResponse,
)


def _normalize_applications_response(
    data: dict | list, *, limit: int, offset: int
) -> PaginatedResponse[AppRead]:
    if isinstance(data, list):
        items = [AppRead(**item) for item in data]
        return PaginatedResponse[AppRead](
            items=items,
            total=len(items),
            limit=limit,
            offset=offset,
        )

    if isinstance(data, dict):
        if all(key in data for key in ("items", "total", "limit", "offset")):
            return PaginatedResponse[AppRead](**data)

        raw_items = data.get("items")
        if raw_items is None:
            raw_items = data.get("applications")
        if raw_items is None:
            raw_items = data.get("data")

        if isinstance(raw_items, list):
            items = [AppRead(**item) for item in raw_items]
            return PaginatedResponse[AppRead](
                items=items,
                total=int(data.get("total", len(items))),
                limit=int(data.get("limit", limit)),
                offset=int(data.get("offset", offset)),
            )

    raise ValueError("Unexpected applications response format")


def _normalize_create_app_key_response(
    data: dict, payload: ApiKeyCreate
) -> ApiKeyCreateResponse:
    if all(field in data for field in ("id", "name", "key", "key_type")):
        return ApiKeyCreateResponse(**data)

    nested_api_key = data.get("api_key")
    if isinstance(nested_api_key, dict):
        key_value = nested_api_key.get("key") or nested_api_key.get("api_key")
        return ApiKeyCreateResponse(
            id=str(nested_api_key.get("id") or data.get("id") or ""),
            name=str(nested_api_key.get("name") or data.get("name") or payload.name),
            key=str(key_value or ""),
            key_type=str(
                nested_api_key.get("key_type")
                or data.get("key_type")
                or payload.key_type
            ),
        )

    key_value = data.get("key") or data.get("api_key")
    return ApiKeyCreateResponse(
        id=str(data.get("id") or ""),
        name=str(data.get("name") or payload.name),
        key=str(key_value or ""),
        key_type=str(data.get("key_type") or payload.key_type),
    )


async def list_applications(
    client: OnyxLogClient, *, limit: int = 50, offset: int = 0
) -> PaginatedResponse[AppRead]:
    data = await client._request(
        "GET", "/applications", params={"limit": limit, "offset": offset}
    )
    return _normalize_applications_response(data, limit=limit, offset=offset)


async def create_application(client: OnyxLogClient, app: AppCreate) -> AppRead:
    data = await client._request("POST", "/applications", json=app.model_dump())
    return AppRead(**data)


async def get_application(client: OnyxLogClient, app_id: str) -> AppRead:
    data = await client._request("GET", f"/applications/{app_id}")
    return AppRead(**data)


async def update_application(
    client: OnyxLogClient, app_id: str, app: AppUpdate
) -> AppRead:
    data = await client._request(
        "PUT", f"/applications/{app_id}", json=app.model_dump(exclude_none=True)
    )
    return AppRead(**data)


async def delete_application(client: OnyxLogClient, app_id: str) -> None:
    await client._request("DELETE", f"/applications/{app_id}")


async def list_app_keys(client: OnyxLogClient, app_id: str) -> list[ApiKeyRead]:
    data = await client._request("GET", f"/applications/{app_id}/keys")
    return [ApiKeyRead(**item) for item in data]


async def create_app_key(
    client: OnyxLogClient, app_id: str, key: ApiKeyCreate
) -> ApiKeyCreateResponse:
    data = await client._request(
        "POST", f"/applications/{app_id}/keys", json=key.model_dump()
    )
    return _normalize_create_app_key_response(data, key)
