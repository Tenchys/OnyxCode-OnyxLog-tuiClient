from __future__ import annotations

from src.api.client import OnyxLogClient
from src.models.schemas import UserWithKey


async def register(
    client: OnyxLogClient, username: str, email: str, password: str
) -> UserWithKey:
    data = await client._request(
        "POST",
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    return UserWithKey(**data)


async def login(client: OnyxLogClient, username: str, password: str) -> UserWithKey:
    data = await client._request(
        "POST",
        "/auth/login",
        json={"username": username, "password": password},
    )
    return UserWithKey(**data)
