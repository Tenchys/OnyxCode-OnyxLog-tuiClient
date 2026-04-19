from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime

import httpx

from src.api.client import ApiClientError, OnyxLogClient
from src.models.schemas import LogQuery, LogRead, PaginatedResponse


def _serialize_query(query: LogQuery) -> dict:
    data = query.model_dump(exclude_none=True)
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data


async def get_logs(
    client: OnyxLogClient,
    *,
    limit: int = 100,
    offset: int = 0,
    api_key: str | None = None,
) -> PaginatedResponse[LogRead]:
    data = await client._request(
        "GET",
        "/logs",
        params={"limit": limit, "offset": offset},
        api_key=api_key,
    )
    return PaginatedResponse[LogRead](**data)


async def get_log_by_id(
    client: OnyxLogClient, log_id: str, *, api_key: str | None = None
) -> LogRead:
    data = await client._request("GET", f"/logs/{log_id}", api_key=api_key)
    return LogRead(**data)


async def query_logs(
    client: OnyxLogClient, query: LogQuery, *, api_key: str | None = None
) -> PaginatedResponse[LogRead]:
    data = await client._request(
        "POST",
        "/logs/query",
        json=_serialize_query(query),
        api_key=api_key,
    )
    return PaginatedResponse[LogRead](**data)


def _parse_sse_event(event_type: str, data_lines: list[str]) -> LogRead | None:
    if event_type not in ("log", "message"):
        return None

    if not data_lines:
        return None

    data_str = "\n".join(data_lines).strip()
    if not data_str:
        return None

    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        return None

    try:
        return LogRead(**data)
    except Exception:
        return None


async def stream_logs(
    client: OnyxLogClient, *, levels: list[str] | None = None, max_retries: int = 5
) -> AsyncIterator[LogRead]:
    params: dict[str, str] = {}
    if levels:
        params["levels"] = ",".join(levels)

    headers = client._headers.copy()
    headers["Accept"] = "text/event-stream"

    retry_count = 0

    while retry_count <= max_retries:
        try:
            received_logs = False
            async with client._client.stream(
                "GET",
                f"{client.BASE_PATH}/logs/stream",
                params=params,
                headers=headers,
            ) as response:
                if response.status_code >= 400:
                    raise ApiClientError(
                        "STREAM_ERROR",
                        response.status_code,
                        "Failed to connect to stream",
                    )
                event_type = "message"
                data_lines: list[str] = []

                async for line in response.aiter_lines():
                    if line == "":
                        parsed_log = _parse_sse_event(event_type, data_lines)
                        event_type = "message"
                        data_lines = []
                        if parsed_log is None:
                            continue
                        retry_count = 0
                        received_logs = True
                        yield parsed_log
                        continue

                    if line.startswith(":"):
                        continue

                    if line.startswith("event:"):
                        event_type = line[len("event:") :].strip()
                        continue

                    if line.startswith("data:"):
                        data_lines.append(line[len("data:") :].strip())

                parsed_log = _parse_sse_event(event_type, data_lines)
                if parsed_log is not None:
                    retry_count = 0
                    received_logs = True
                    yield parsed_log

                if received_logs:
                    await asyncio.sleep(0)
                    continue

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            if retry_count >= max_retries:
                raise ApiClientError(
                    "CONNECTION_ERROR",
                    0,
                    f"Stream connection failed after {max_retries} retries: {e}",
                )
            retry_count += 1
            await asyncio.sleep(min(2 ** (retry_count - 1), 60.0))
            continue
        except ApiClientError:
            raise
        except Exception as e:
            if retry_count >= max_retries:
                raise ApiClientError(
                    "STREAM_ERROR",
                    0,
                    f"Stream error after {max_retries} retries: {e}",
                )
            retry_count += 1
            await asyncio.sleep(min(2 ** (retry_count - 1), 60.0))
            continue

        if retry_count >= max_retries:
            raise ApiClientError(
                "STREAM_ERROR",
                0,
                f"Stream disconnected after {max_retries} retries",
            )

        retry_count += 1
        await asyncio.sleep(min(2 ** (retry_count - 1), 60.0))
