from __future__ import annotations

from datetime import datetime

from src.api.client import OnyxLogClient
from src.models.schemas import LogQuery, LogRead, PaginatedResponse


def _serialize_query(query: LogQuery) -> dict:
    data = query.model_dump(exclude_none=True)
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data


async def get_logs(
    client: OnyxLogClient, *, limit: int = 100, offset: int = 0
) -> PaginatedResponse[LogRead]:
    data = await client._request(
        "GET", "/logs", params={"limit": limit, "offset": offset}
    )
    return PaginatedResponse[LogRead](**data)


async def get_log_by_id(client: OnyxLogClient, log_id: str) -> LogRead:
    data = await client._request("GET", f"/logs/{log_id}")
    return LogRead(**data)


async def query_logs(
    client: OnyxLogClient, query: LogQuery
) -> PaginatedResponse[LogRead]:
    data = await client._request("POST", "/logs/query", json=_serialize_query(query))
    return PaginatedResponse[LogRead](**data)
