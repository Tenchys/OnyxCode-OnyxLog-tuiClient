from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from textual.app import App
from textual.widgets import Button, Static

from src.api.client import ApiClientError
from src.screens.dashboard import DashboardScreen


class MockApp(App):
    CSS_PATH = None

    def __init__(self) -> None:
        super().__init__()
        self.client = MagicMock()
        self.client.health_check = AsyncMock(
            return_value=MagicMock(status="ok", version="1.0.0")
        )
        self.settings = MagicMock()
        self.settings.onyxlog_url = "http://localhost:8000"

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())


@pytest.fixture
def mock_app():
    return MockApp()


def get_screen(app):
    return app.screen


class TestDashboardScreenMount:
    @pytest.mark.asyncio
    async def test_screen_mounts(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            assert isinstance(screen, DashboardScreen)

    @pytest.mark.asyncio
    async def test_has_title(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            title = screen.query_one("#dashboard-title", Static)
            assert title is not None
            assert "OnyxLog Dashboard" in title.render().plain

    @pytest.mark.asyncio
    async def test_has_applications_button(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            btn = screen.query_one("#btn-applications", Button)
            assert btn is not None
            assert "Applications" in btn.label.plain

    @pytest.mark.asyncio
    async def test_has_logs_button(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            btn = screen.query_one("#btn-logs", Button)
            assert btn is not None
            assert "Logs" in btn.label.plain

    @pytest.mark.asyncio
    async def test_has_settings_button(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            btn = screen.query_one("#btn-settings", Button)
            assert btn is not None
            assert "Settings" in btn.label.plain


class TestDashboardNavigation:
    @pytest.mark.asyncio
    async def test_binding_a_navigates_to_applications(self, mock_app):
        from src.screens.applications import ApplicationsScreen

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("a")
            await pilot.pause()
            assert isinstance(mock_app.screen, ApplicationsScreen)

    @pytest.mark.asyncio
    async def test_binding_l_navigates_to_logs(self, mock_app):
        from src.screens.logs import LogsScreen

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("l")
            await pilot.pause()
            assert isinstance(mock_app.screen, LogsScreen)

    @pytest.mark.asyncio
    async def test_binding_s_navigates_to_settings(self, mock_app):
        from src.screens.settings import SettingsScreen

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("s")
            await pilot.pause()
            assert isinstance(mock_app.screen, SettingsScreen)

    @pytest.mark.asyncio
    async def test_button_applications_navigates(self, mock_app):
        from src.screens.applications import ApplicationsScreen

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            btn = mock_app.screen.query_one("#btn-applications", Button)
            btn.press()
            await pilot.pause()
            assert isinstance(mock_app.screen, ApplicationsScreen)

    @pytest.mark.asyncio
    async def test_button_logs_navigates(self, mock_app):
        from src.screens.logs import LogsScreen

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            btn = mock_app.screen.query_one("#btn-logs", Button)
            btn.press()
            await pilot.pause()
            assert isinstance(mock_app.screen, LogsScreen)

    @pytest.mark.asyncio
    async def test_button_settings_navigates(self, mock_app):
        from src.screens.settings import SettingsScreen

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            btn = mock_app.screen.query_one("#btn-settings", Button)
            btn.press()
            await pilot.pause()
            assert isinstance(mock_app.screen, SettingsScreen)


class TestDashboardStats:
    @pytest.mark.asyncio
    async def test_stats_loads_on_mount(self, mock_app):
        mock_app.client.is_authenticated = True
        mock_app.client._request = AsyncMock(
            return_value={
                "total_logs": 1000,
                "total_applications": 5,
                "active_applications": 3,
                "recent_logs_24h": 250,
            }
        )

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            screen = get_screen(mock_app)
            stats = screen.query_one("#stats-content", Static)
            stats_text = stats.render().plain
            assert "1,000" in stats_text
            assert "5" in stats_text
            assert "3" in stats_text
            assert "250" in stats_text

    @pytest.mark.asyncio
    async def test_stats_shows_error_on_connection_failure(self, mock_app):
        mock_app.client.is_authenticated = True
        mock_app.client._request = AsyncMock(
            side_effect=ApiClientError("CONNECTION_ERROR", 0, "Cannot connect")
        )

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            screen = get_screen(mock_app)
            stats = screen.query_one("#stats-content", Static)
            assert "Unable to load stats" in stats.render().plain

    @pytest.mark.asyncio
    async def test_stats_shows_not_authenticated(self, mock_app):
        mock_app.client.is_authenticated = False

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            stats = screen.query_one("#stats-content", Static)
            assert "Not authenticated" in stats.render().plain
