from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.api.client import ApiClientError
from src.app import OnyxLogApp


class TestOnyxLogApp:
    @pytest.mark.asyncio
    async def test_app_starts_with_auto_login_success(self, tmp_path):
        app = OnyxLogApp()

        mock_key_data = {
            "id": "key-1",
            "name": "test-key",
            "key": "test-api-key-123",
            "key_type": "user",
            "role": "admin",
            "user_id": "user-1",
            "app_id": None,
            "server_url": "http://localhost:8000",
            "created_at": "2026-04-18T10:00:00Z",
            "is_active": 1,
        }

        with (
            patch("src.app.init_db", new_callable=AsyncMock),
            patch("src.app.get_active_key", new_callable=AsyncMock) as mock_get_key,
        ):
            mock_get_key.return_value = mock_key_data

            mock_client = MagicMock()
            mock_client.set_api_key = MagicMock()
            mock_client.close = AsyncMock()
            mock_client.health_check = AsyncMock(
                return_value=MagicMock(status="ok", version="1.0.0")
            )
            app._client = mock_client

            await app.on_mount()

            assert len(app.screen_stack) == 1
            from src.screens.dashboard import DashboardScreen

            assert isinstance(app.screen, DashboardScreen)
            mock_client.set_api_key.assert_called_once_with("test-api-key-123")

    @pytest.mark.asyncio
    async def test_app_starts_without_api_key_shows_login(self, tmp_path):
        app = OnyxLogApp()

        with (
            patch("src.app.init_db", new_callable=AsyncMock),
            patch("src.app.get_active_key", new_callable=AsyncMock) as mock_get_key,
        ):
            mock_get_key.return_value = None

            mock_client = MagicMock()
            app._client = mock_client

            await app.on_mount()

            assert len(app.screen_stack) == 1
            from src.screens.login import LoginScreen

            assert isinstance(app.screen, LoginScreen)

    @pytest.mark.asyncio
    async def test_app_starts_with_invalid_api_key_shows_login(self, tmp_path):
        app = OnyxLogApp()

        mock_key_data = {
            "id": "key-1",
            "name": "test-key",
            "key": "invalid-key",
            "key_type": "user",
            "role": "admin",
            "user_id": "user-1",
            "app_id": None,
            "server_url": "http://localhost:8000",
            "created_at": "2026-04-18T10:00:00Z",
            "is_active": 1,
        }

        with (
            patch("src.app.init_db", new_callable=AsyncMock),
            patch("src.app.get_active_key", new_callable=AsyncMock) as mock_get_key,
        ):
            mock_get_key.return_value = mock_key_data

            mock_client = MagicMock()
            mock_client.set_api_key = MagicMock()
            mock_client.close = AsyncMock()
            mock_client.health_check = AsyncMock(
                side_effect=ApiClientError("INVALID_API_KEY", 403, "Invalid API key")
            )
            app._client = mock_client

            await app.on_mount()

            assert len(app.screen_stack) == 1
            from src.screens.login import LoginScreen

            assert isinstance(app.screen, LoginScreen)

    @pytest.mark.asyncio
    async def test_app_quit_binding(self):
        app = OnyxLogApp()
        with (
            patch("src.app.init_db", new_callable=AsyncMock),
            patch("src.app.get_active_key", new_callable=AsyncMock) as mock_get_key,
        ):
            mock_get_key.return_value = None
            async with app.run_test() as pilot:
                assert app.is_running is True
                app.action_quit()
                await pilot.pause()
                assert app.is_running is False

    @pytest.mark.asyncio
    async def test_client_property_creates_client(self):
        app = OnyxLogApp()
        app._settings = MagicMock()
        app._settings.onyxlog_url = "http://localhost:8000"

        client = app.client

        from src.api.client import OnyxLogClient

        assert isinstance(client, OnyxLogClient)

    @pytest.mark.asyncio
    async def test_settings_property_creates_settings(self):
        app = OnyxLogApp()

        settings = app.settings

        from src.config import Settings

        assert isinstance(settings, Settings)


class TestOnyxLogAppIntegration:
    @pytest.mark.asyncio
    async def test_full_auto_login_flow_mocked(self, tmp_path):
        app = OnyxLogApp()

        mock_key_data = {
            "id": "key-123",
            "name": "auto-login-key",
            "key": "valid-key-abc",
            "key_type": "user",
            "role": "admin",
            "user_id": "user-456",
            "app_id": None,
            "server_url": "http://localhost:8000",
            "created_at": "2026-04-18T10:00:00Z",
            "is_active": 1,
        }

        with (
            patch("src.app.init_db", new_callable=AsyncMock),
            patch("src.app.get_active_key", new_callable=AsyncMock) as mock_get_key,
        ):
            mock_get_key.return_value = mock_key_data

            mock_client = MagicMock()
            mock_client.set_api_key = MagicMock()
            mock_client.close = AsyncMock()
            mock_client.health_check = AsyncMock(
                return_value=MagicMock(status="ok", version="1.0.0")
            )
            app._client = mock_client

            async with app.run_test() as pilot:
                await app.on_mount()
                await pilot.pause()

                from src.screens.dashboard import DashboardScreen

                assert isinstance(app.screen, DashboardScreen)
                mock_client.set_api_key.assert_called_with("valid-key-abc")
