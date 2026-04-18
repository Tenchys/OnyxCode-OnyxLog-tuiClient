from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.models.schemas import (
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyRead,
    AppCreate,
    AppRead,
    AppUpdate,
    AuthApiKeyResponse,
    ErrorResponse,
    HealthResponse,
    LogCreate,
    LoginRequest,
    LogLevel,
    LogQuery,
    LogRead,
    PaginatedResponse,
    StatsOverview,
    UserCreate,
    UserRead,
    UserWithKey,
)


class TestLogLevel:
    def test_log_level_enum_values(self):
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"
        assert LogLevel.CRITICAL == "CRITICAL"

    def test_log_level_is_string(self):
        level = LogLevel.INFO
        assert isinstance(level, str)
        assert level == "INFO"


class TestUserCreate:
    def test_user_create_valid(self):
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="securepass123",
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "securepass123"

    def test_user_create_missing_required_field(self):
        with pytest.raises(ValidationError):
            UserCreate(username="testuser")

    def test_user_create_incorrect_type(self):
        with pytest.raises(ValidationError):
            UserCreate(username=123, email="test@example.com", password="pass")


class TestUserRead:
    def test_user_read_valid(self):
        user_id = uuid4()
        now = datetime.now()
        user = UserRead(
            id=user_id,
            username="testuser",
            email="test@example.com",
            role="admin",
            is_active=True,
            created_at=now,
        )
        assert user.id == user_id
        assert user.username == "testuser"
        assert user.role == "admin"
        assert user.is_active is True

    def test_user_read_default_is_active(self):
        user_id = uuid4()
        now = datetime.now()
        user = UserRead(
            id=user_id,
            username="testuser",
            email="test@example.com",
            role="admin",
            created_at=now,
        )
        assert user.is_active is True

    def test_user_read_from_attributes(self):
        class FakeUser:
            id = uuid4()
            username = "from_attr"
            email = "attr@example.com"
            role = "viewer"
            is_active = False
            created_at = datetime.now()

        user = UserRead.model_validate(FakeUser())
        assert user.username == "from_attr"
        assert user.is_active is False


class TestAuthApiKeyResponse:
    def test_auth_api_key_response_valid(self):
        key = AuthApiKeyResponse(id="key-1", key="onyx_abc123", role="admin")
        assert key.id == "key-1"
        assert key.key == "onyx_abc123"
        assert key.role == "admin"

    def test_auth_api_key_response_missing_field(self):
        with pytest.raises(ValidationError):
            AuthApiKeyResponse(id="key-1", key="onyx_abc123")


class TestUserWithKey:
    def test_user_with_key_valid(self):
        user_id = uuid4()
        now = datetime.now()
        user = UserRead(
            id=user_id,
            username="testuser",
            email="test@example.com",
            role="admin",
            created_at=now,
        )
        api_key = AuthApiKeyResponse(id="key-1", key="onyx_abc123", role="admin")
        result = UserWithKey(user=user, api_key=api_key)
        assert result.user.username == "testuser"
        assert result.api_key.key == "onyx_abc123"

    def test_user_with_key_nested_from_dict(self):
        data = {
            "user": {
                "id": str(uuid4()),
                "username": "testuser",
                "email": "test@example.com",
                "role": "admin",
                "created_at": datetime.now().isoformat(),
            },
            "api_key": {
                "id": "key-1",
                "key": "onyx_abc123",
                "role": "admin",
            },
        }
        result = UserWithKey(**data)
        assert result.user.username == "testuser"
        assert result.api_key.key == "onyx_abc123"


class TestLoginRequest:
    def test_login_request_valid(self):
        login = LoginRequest(username="testuser", password="password123")
        assert login.username == "testuser"
        assert login.password == "password123"

    def test_login_request_missing_password(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser")


class TestAppCreate:
    def test_app_create_valid(self):
        app = AppCreate(
            name="My App",
            app_id="my-app",
            environment="production",
        )
        assert app.name == "My App"
        assert app.app_id == "my-app"
        assert app.environment == "production"

    def test_app_create_with_description(self):
        app = AppCreate(
            name="My App",
            app_id="my-app",
            description="A test application",
            environment="production",
        )
        assert app.description == "A test application"

    def test_app_create_optional_description(self):
        app = AppCreate(
            name="My App",
            app_id="my-app",
            environment="production",
        )
        assert app.description is None

    def test_app_create_missing_required(self):
        with pytest.raises(ValidationError):
            AppCreate(name="My App")


class TestAppRead:
    def test_app_read_valid(self):
        app_id = uuid4()
        now = datetime.now()
        app = AppRead(
            id=app_id,
            name="My App",
            app_id="my-app",
            description="Test",
            environment="production",
            is_active=True,
            created_at=now,
        )
        assert app.id == app_id
        assert app.is_active is True

    def test_app_read_from_attributes(self):
        class FakeApp:
            id = uuid4()
            name = "from_attr"
            app_id = "attr-app"
            description = None
            environment = "dev"
            is_active = True
            created_at = datetime.now()

        app = AppRead.model_validate(FakeApp())
        assert app.name == "from_attr"


class TestAppUpdate:
    def test_app_update_all_fields(self):
        update = AppUpdate(
            name="Updated App",
            description="Updated desc",
            environment="staging",
        )
        assert update.name == "Updated App"
        assert update.description == "Updated desc"
        assert update.environment == "staging"

    def test_app_update_partial(self):
        update = AppUpdate(name="Updated App")
        assert update.name == "Updated App"
        assert update.description is None
        assert update.environment is None

    def test_app_update_empty(self):
        update = AppUpdate()
        assert update.name is None
        assert update.description is None


class TestLogRead:
    def test_log_read_valid(self):
        log_id = uuid4()
        now = datetime.now()
        log = LogRead(
            id=log_id,
            timestamp=now,
            level="ERROR",
            app_id="my-app",
            message="Something went wrong",
            metadata={"error_code": 500},
        )
        assert log.level == "ERROR"
        assert log.metadata == {"error_code": 500}

    def test_log_read_optional_metadata(self):
        log_id = uuid4()
        now = datetime.now()
        log = LogRead(
            id=log_id,
            timestamp=now,
            level="INFO",
            app_id="my-app",
            message="Info message",
        )
        assert log.metadata is None


class TestLogCreate:
    def test_log_create_valid(self):
        log = LogCreate(
            app_id="my-app",
            level="WARNING",
            message="Warning message",
        )
        assert log.app_id == "my-app"
        assert log.level == "WARNING"

    def test_log_create_with_metadata(self):
        log = LogCreate(
            app_id="my-app",
            level="INFO",
            message="With metadata",
            metadata={"user_id": "u1"},
        )
        assert log.metadata == {"user_id": "u1"}


class TestLogQuery:
    def test_log_query_defaults(self):
        query = LogQuery()
        assert query.app_id is None
        assert query.limit == 100
        assert query.offset == 0

    def test_log_query_with_filters(self):
        query = LogQuery(
            app_id="my-app",
            level="ERROR",
            start_time=datetime.now(),
            limit=50,
        )
        assert query.app_id == "my-app"
        assert query.level == "ERROR"
        assert query.limit == 50

    def test_log_query_limit_bounds(self):
        with pytest.raises(ValidationError):
            LogQuery(limit=0)

    def test_log_query_limit_exceeds_max(self):
        with pytest.raises(ValidationError):
            LogQuery(limit=2000)


class TestApiKeyRead:
    def test_api_key_read_valid(self):
        key = ApiKeyRead(
            id="key-1",
            name="Test Key",
            key_type="user",
            role="admin",
            created_at=datetime.now(),
        )
        assert key.key_type == "user"
        assert key.role == "admin"
        assert key.is_active is True

    def test_api_key_read_default_is_active(self):
        key = ApiKeyRead(
            id="key-1",
            name="Test Key",
            key_type="user",
            created_at=datetime.now(),
        )
        assert key.is_active is True


class TestApiKeyCreate:
    def test_api_key_create_valid(self):
        key = ApiKeyCreate(name="New Key", key_type="user")
        assert key.name == "New Key"
        assert key.key_type == "user"

    def test_api_key_create_with_role(self):
        key = ApiKeyCreate(name="Admin Key", key_type="user", role="admin")
        assert key.role == "admin"


class TestApiKeyCreateResponse:
    def test_api_key_create_response_valid(self):
        key = ApiKeyCreateResponse(
            id="key-1",
            name="Test Key",
            key="onyx_abc123",
            key_type="user",
        )
        assert key.key == "onyx_abc123"


class TestPaginatedResponse:
    def test_paginated_response_strings(self):
        response = PaginatedResponse[str](
            items=["a", "b", "c"],
            total=100,
            limit=10,
            offset=0,
        )
        assert response.items == ["a", "b", "c"]
        assert response.total == 100
        assert response.limit == 10

    def test_paginated_response_ints(self):
        response = PaginatedResponse[int](
            items=[1, 2, 3],
            total=50,
            limit=3,
            offset=10,
        )
        assert response.items == [1, 2, 3]
        assert response.offset == 10

    def test_paginated_response_with_objects(self):
        user_id = uuid4()
        now = datetime.now()
        response = PaginatedResponse[UserRead](
            items=[
                UserRead(
                    id=user_id,
                    username="user1",
                    email="u1@example.com",
                    role="admin",
                    created_at=now,
                ),
            ],
            total=1,
            limit=10,
            offset=0,
        )
        assert len(response.items) == 1
        assert response.items[0].username == "user1"


class TestErrorResponse:
    def test_error_response_valid(self):
        error = ErrorResponse(
            error_code="NOT_FOUND",
            message="Resource not found",
        )
        assert error.error_code == "NOT_FOUND"

    def test_error_response_with_details(self):
        error = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Invalid data",
            details={"field": "email", "reason": "invalid format"},
        )
        assert error.details == {"field": "email", "reason": "invalid format"}

    def test_error_response_optional_details(self):
        error = ErrorResponse(error_code="ERROR", message="Error message")
        assert error.details is None


class TestHealthResponse:
    def test_health_response_valid(self):
        health = HealthResponse(status="healthy", version="1.0.0")
        assert health.status == "healthy"
        assert health.version == "1.0.0"


class TestStatsOverview:
    def test_stats_overview_valid(self):
        stats = StatsOverview(
            total_logs=1000,
            total_applications=10,
            active_applications=8,
            recent_logs_24h=150,
        )
        assert stats.total_logs == 1000
        assert stats.active_applications == 8

    def test_stats_overview_zero_values(self):
        stats = StatsOverview(
            total_logs=0,
            total_applications=0,
            active_applications=0,
            recent_logs_24h=0,
        )
        assert stats.total_logs == 0


class TestEdgeCases:
    def test_empty_string_username(self):
        user = UserCreate(username="", email="test@example.com", password="pass")
        assert user.username == ""

    def test_none_metadata(self):
        log = LogCreate(
            app_id="my-app",
            level="INFO",
            message="Test",
            metadata=None,
        )
        assert log.metadata is None

    def test_incorrect_type_raises(self):
        with pytest.raises(ValidationError):
            AppCreate(
                name="My App",
                app_id=123,
                environment="production",
            )

    def test_uuid_field_validation(self):
        with pytest.raises(ValidationError):
            UserRead(
                id="not-a-uuid",
                username="test",
                email="test@example.com",
                role="admin",
                created_at=datetime.now(),
            )
