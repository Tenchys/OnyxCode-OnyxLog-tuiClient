from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from textual.app import App
from textual.widgets import Input

from src.api.client import ApiClientError
from src.screens.login import LoginScreen


class MockApp(App):
    CSS_PATH = None

    def __init__(self) -> None:
        super().__init__()
        self.client = MagicMock()
        self.settings = MagicMock()
        self.settings.onyxlog_url = "http://localhost:8000"

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())


@pytest.fixture
def mock_app():
    return MockApp()


def get_screen(app):
    return app.screen


class TestLoginScreenMount:
    @pytest.mark.asyncio
    async def test_screen_mounts(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            assert isinstance(screen, LoginScreen)

    @pytest.mark.asyncio
    async def test_has_username_input(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            username_input = screen.query_one("#username-input", Input)
            assert username_input is not None

    @pytest.mark.asyncio
    async def test_has_email_input(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            email_input = screen.query_one("#email-input", Input)
            assert email_input is not None

    @pytest.mark.asyncio
    async def test_has_password_input(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            password_input = screen.query_one("#password-input", Input)
            assert password_input is not None
            assert password_input.password is True

    @pytest.mark.asyncio
    async def test_has_login_button(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            login_btn = screen.query_one("#login-btn")
            assert login_btn is not None
            assert login_btn.label.plain == "Login"

    @pytest.mark.asyncio
    async def test_has_register_button(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            register_btn = screen.query_one("#register-btn")
            assert register_btn is not None
            assert register_btn.label.plain == "Register"


class TestLoginFlow:
    @pytest.mark.asyncio
    async def test_login_success(self, mock_app):
        from src.models.schemas import AuthApiKeyResponse, UserRead, UserWithKey

        mock_api_key = AuthApiKeyResponse(
            id="key-123", key="sk_test_key_abc123", role="user"
        )
        mock_user = UserRead(
            id="550e8400-e29b-41d4-a716-446655440000",
            username="testuser",
            email="test@example.com",
            role="user",
            is_active=True,
            created_at=datetime.now(),
        )
        mock_result = UserWithKey(user=mock_user, api_key=mock_api_key)

        with (
            patch(
                "src.screens.login.login",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch("src.screens.login.db.store_key", new_callable=AsyncMock),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                screen = get_screen(mock_app)
                screen.query_one("#username-input", Input).value = "testuser"
                screen.query_one("#password-input", Input).value = "password123"

                login_btn = screen.query_one("#login-btn")
                login_btn.press()

                await pilot.pause()

                mock_app.client.set_api_key.assert_called_once_with(
                    "sk_test_key_abc123"
                )

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_app):
        with patch(
            "src.screens.login.login",
            new_callable=AsyncMock,
            side_effect=ApiClientError(
                "INVALID_CREDENTIALS", 401, "Invalid credentials"
            ),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                screen = get_screen(mock_app)
                screen.query_one("#username-input", Input).value = "wronguser"
                screen.query_one("#password-input", Input).value = "wrongpass"

                login_btn = screen.query_one("#login-btn")
                login_btn.press()

                await pilot.pause()

                notifications = list(mock_app._notifications)
                assert len(notifications) > 0
                last_notification = notifications[-1]
                assert last_notification.severity == "error"

    @pytest.mark.asyncio
    async def test_login_connection_error(self, mock_app):
        with patch(
            "src.screens.login.login",
            new_callable=AsyncMock,
            side_effect=ApiClientError(
                "CONNECTION_ERROR", 0, "Cannot connect to server"
            ),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                screen = get_screen(mock_app)
                screen.query_one("#username-input", Input).value = "testuser"
                screen.query_one("#password-input", Input).value = "password123"

                login_btn = screen.query_one("#login-btn")
                login_btn.press()

                await pilot.pause()

                notifications = list(mock_app._notifications)
                assert len(notifications) > 0
                last_notification = notifications[-1]
                assert last_notification.severity == "error"


class TestRegisterFlow:
    @pytest.mark.asyncio
    async def test_register_success(self, mock_app):
        from src.models.schemas import AuthApiKeyResponse, UserRead, UserWithKey

        mock_api_key = AuthApiKeyResponse(
            id="key-123", key="sk_test_key_abc123", role="user"
        )
        mock_user = UserRead(
            id="550e8400-e29b-41d4-a716-446655440000",
            username="newuser",
            email="new@example.com",
            role="user",
            is_active=True,
            created_at=datetime.now(),
        )
        mock_result = UserWithKey(user=mock_user, api_key=mock_api_key)

        with (
            patch(
                "src.screens.login.register",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch("src.screens.login.db.store_key", new_callable=AsyncMock),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                screen = get_screen(mock_app)
                screen.query_one("#username-input", Input).value = "newuser"
                screen.query_one("#email-input", Input).value = "new@example.com"
                screen.query_one("#password-input", Input).value = "password123"

                register_btn = screen.query_one("#register-btn")
                register_btn.press()

                await pilot.pause()

                mock_app.client.set_api_key.assert_called_once_with(
                    "sk_test_key_abc123"
                )

    @pytest.mark.asyncio
    async def test_register_duplicate_entry(self, mock_app):
        with patch(
            "src.screens.login.register",
            new_callable=AsyncMock,
            side_effect=ApiClientError(
                "DUPLICATE_ENTRY", 409, "Username already exists"
            ),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                screen = get_screen(mock_app)
                screen.query_one("#username-input", Input).value = "existinguser"
                screen.query_one("#email-input", Input).value = "test@example.com"
                screen.query_one("#password-input", Input).value = "password123"

                register_btn = screen.query_one("#register-btn")
                register_btn.press()

                await pilot.pause()

                notifications = list(mock_app._notifications)
                assert len(notifications) > 0
                last_notification = notifications[-1]
                assert last_notification.severity == "error"


class TestValidation:
    @pytest.mark.asyncio
    async def test_login_empty_username(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            screen.query_one("#username-input", Input).value = ""
            screen.query_one("#password-input", Input).value = "password123"

            login_btn = screen.query_one("#login-btn")
            login_btn.press()

            await pilot.pause()

            notifications = list(mock_app._notifications)
            assert len(notifications) > 0
            last_notification = notifications[-1]
            assert last_notification.severity == "error"

    @pytest.mark.asyncio
    async def test_login_empty_password(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            screen.query_one("#username-input", Input).value = "testuser"
            screen.query_one("#password-input", Input).value = ""

            login_btn = screen.query_one("#login-btn")
            login_btn.press()

            await pilot.pause()

            notifications = list(mock_app._notifications)
            assert len(notifications) > 0
            last_notification = notifications[-1]
            assert last_notification.severity == "error"

    @pytest.mark.asyncio
    async def test_register_missing_email(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            screen.query_one("#username-input", Input).value = "newuser"
            screen.query_one("#email-input", Input).value = ""
            screen.query_one("#password-input", Input).value = "password123"

            register_btn = screen.query_one("#register-btn")
            register_btn.press()

            await pilot.pause()

            notifications = list(mock_app._notifications)
            assert len(notifications) > 0
            last_notification = notifications[-1]
            assert last_notification.severity == "error"
