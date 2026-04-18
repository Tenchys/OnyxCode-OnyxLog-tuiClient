from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserRead(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str


class AppCreate(BaseModel):
    name: str
    app_id: str
    description: str | None = None
    environment: str


class AppRead(BaseModel):
    id: UUID
    name: str
    app_id: str
    description: str | None
    environment: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    environment: str | None = None


class LogRead(BaseModel):
    id: UUID
    timestamp: datetime
    level: str
    app_id: str
    message: str
    metadata: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class LogCreate(BaseModel):
    app_id: str
    level: str
    message: str
    metadata: dict | None = None


class LogQuery(BaseModel):
    app_id: str | None = None
    level: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    search: str | None = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ApiKeyRead(BaseModel):
    id: str
    name: str
    key_type: str
    role: str | None = None
    user_id: str | None = None
    app_id: str | None = None
    created_at: datetime
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class ApiKeyCreate(BaseModel):
    name: str
    key_type: str
    role: str | None = None


class ApiKeyCreateResponse(BaseModel):
    id: str
    name: str
    key: str
    key_type: str


class AuthApiKeyResponse(BaseModel):
    id: str
    key: str
    role: str


class UserWithKey(BaseModel):
    user: UserRead
    api_key: AuthApiKeyResponse | str

    def get_api_key(self) -> str:
        """Get the API key string regardless of response format."""
        if isinstance(self.api_key, str):
            return self.api_key
        return self.api_key.key

    def get_key_id(self) -> str | None:
        """Get the API key ID if available."""
        if isinstance(self.api_key, str):
            return None
        return self.api_key.id

    def get_role(self) -> str | None:
        """Get the role if available."""
        if isinstance(self.api_key, str):
            return None
        return self.api_key.role


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict | None = None


class HealthResponse(BaseModel):
    status: str
    version: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class StatsOverview(BaseModel):
    total_logs: int
    total_applications: int
    active_applications: int
    recent_logs_24h: int
