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


async def list_applications(
    client: OnyxLogClient, *, limit: int = 50, offset: int = 0
) -> PaginatedResponse[AppRead]:
    data = await client._request(
        "GET", "/applications", params={"limit": limit, "offset": offset}
    )
    return PaginatedResponse[AppRead](**data)


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
    return ApiKeyCreateResponse(**data)
