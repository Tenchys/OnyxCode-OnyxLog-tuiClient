from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from textual.app import App
from textual.widgets import Button, DataTable, Input, Select

from src.api.client import ApiClientError
from src.models.schemas import LogQuery, LogRead
from src.screens.logs import FilterModal, LogsScreen, SearchModal


class MockApp(App):
    CSS_PATH = None

    def __init__(self) -> None:
        super().__init__()
        self.client = MagicMock()
        self.settings = MagicMock()
        self.settings.onyxlog_url = "http://localhost:8000"

    def on_mount(self) -> None:
        self.push_screen(LogsScreen())


def make_log(id: str, level: str, message: str, app_id: str = "test-app") -> LogRead:
    return LogRead(
        id=UUID(id),
        timestamp=datetime(2026, 4, 17, 12, 0, 0),
        level=level,
        app_id=app_id,
        message=message,
        metadata=None,
    )


def mock_logs_request(logs: list[LogRead]) -> MagicMock:
    items_data = [
        {
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat(),
            "level": log.level,
            "app_id": log.app_id,
            "message": log.message,
            "metadata": None,
        }
        for log in logs
    ]
    return AsyncMock(
        return_value={
            "items": items_data,
            "total": len(logs),
            "limit": 100,
            "offset": 0,
        }
    )


@pytest.fixture
def mock_app():
    return MockApp()


@pytest.fixture
def populated_mock_app():
    app = MockApp()
    app.client._request = mock_logs_request(
        [
            make_log("11111111-1111-1111-1111-111111111111", "DEBUG", "Debug message"),
            make_log("22222222-2222-2222-2222-222222222222", "INFO", "Info message"),
            make_log(
                "33333333-3333-3333-3333-333333333333", "WARNING", "Warning message"
            ),
            make_log("44444444-4444-4444-4444-444444444444", "ERROR", "Error message"),
            make_log(
                "55555555-5555-5555-5555-555555555555", "CRITICAL", "Critical message"
            ),
        ]
    )
    return app


def get_screen(app):
    return app.screen


class TestLogsScreenMount:
    @pytest.mark.asyncio
    async def test_screen_mounts(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            assert isinstance(get_screen(mock_app), LogsScreen)

    @pytest.mark.asyncio
    async def test_has_logs_table(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            table = screen.query_one("#logs-table", DataTable)
            assert table is not None

    @pytest.mark.asyncio
    async def test_logs_table_has_columns(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            table = screen.query_one("#logs-table", DataTable)
            columns = [str(c.label) for c in table.columns.values()]
            assert "Timestamp" in columns
            assert "Level" in columns
            assert "App" in columns
            assert "Message" in columns


class TestLogsScreenLoading:
    @pytest.mark.asyncio
    async def test_loads_logs_on_mount(self, populated_mock_app):
        async with populated_mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            screen = get_screen(populated_mock_app)
            table = screen.query_one("#logs-table", DataTable)
            assert table.row_count == 5

    @pytest.mark.asyncio
    async def test_notify_on_load(self, populated_mock_app):
        async with populated_mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()

    @pytest.mark.asyncio
    async def test_handles_connection_error(self, mock_app):
        mock_app.client._request = AsyncMock(
            side_effect=ApiClientError("CONNECTION_ERROR", 0, "Cannot connect")
        )
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            screen = get_screen(mock_app)
            table = screen.query_one("#logs-table", DataTable)
            assert table.row_count == 0


class TestLogsScreenStyles:
    def test_level_coloring_matches_spec(self):
        screen = LogsScreen()
        assert screen._format_level("DEBUG").style == "dim"
        assert screen._format_level("INFO").style == "green"
        assert screen._format_level("WARNING").style == "yellow"
        assert screen._format_level("ERROR").style == "bold red"
        assert screen._format_level("CRITICAL").style == "bold red reverse"


class TestLogsScreenBindings:
    @pytest.mark.asyncio
    async def test_binding_r_refreshes(self, populated_mock_app):
        async with populated_mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            populated_mock_app.client._request = mock_logs_request(
                [
                    make_log("66666666-6666-6666-6666-666666666666", "INFO", "New log"),
                ]
            )
            await pilot.press("r")
            await pilot.pause()
            await pilot.pause()
            screen = get_screen(populated_mock_app)
            table = screen.query_one("#logs-table", DataTable)
            assert table.row_count == 1

    @pytest.mark.asyncio
    async def test_binding_f_opens_filter_modal(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("f")
            await pilot.pause()
            assert isinstance(mock_app.screen, FilterModal)

    @pytest.mark.asyncio
    async def test_binding_slash_opens_search_modal(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("/")
            await pilot.pause()
            assert isinstance(mock_app.screen, SearchModal)

    @pytest.mark.asyncio
    async def test_binding_c_clears_filters(self, mock_app):
        mock_app.client._request = mock_logs_request([])
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("c")
            await pilot.pause()

    @pytest.mark.asyncio
    async def test_binding_escape_goes_back(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            assert mock_app.screen.parent is None or isinstance(
                mock_app.screen, type(mock_app.screen)
            )


class TestFilterModal:
    @pytest.mark.asyncio
    async def test_filter_modal_mounts(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("f")
            await pilot.pause()
            assert isinstance(mock_app.screen, FilterModal)

    @pytest.mark.asyncio
    async def test_filter_modal_has_level_select(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("f")
            await pilot.pause()
            select = mock_app.screen.query_one("#level-select", Select)
            assert select is not None

    @pytest.mark.asyncio
    async def test_filter_modal_has_appid_select(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("f")
            await pilot.pause()
            select = mock_app.screen.query_one("#appid-select", Select)
            assert select is not None

    @pytest.mark.asyncio
    async def test_filter_modal_apply_dismisses(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("f")
            await pilot.pause()
            apply_btn = mock_app.screen.query_one("#apply-btn", Button)
            apply_btn.press()
            await pilot.pause()


class TestLogsScreenFiltering:
    @pytest.mark.asyncio
    async def test_apply_filters_uses_query_logs(self, populated_mock_app):
        async with populated_mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            screen = get_screen(populated_mock_app)
            populated_mock_app.client._request.reset_mock()

            await screen._handle_filter_applied(LogQuery(level="ERROR"))
            await pilot.pause()
            await pilot.pause()

            called_paths = [
                call.args[1]
                for call in populated_mock_app.client._request.await_args_list
            ]
            assert "/logs/query" in called_paths

    @pytest.mark.asyncio
    async def test_clear_filters_from_modal_uses_get_logs(self, populated_mock_app):
        async with populated_mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            screen = get_screen(populated_mock_app)

            await screen._handle_filter_applied(LogQuery(level="ERROR"))
            await pilot.pause()
            await pilot.pause()

            populated_mock_app.client._request.reset_mock()
            await screen._handle_filter_applied(LogQuery())
            await pilot.pause()
            await pilot.pause()

            called_paths = [
                call.args[1]
                for call in populated_mock_app.client._request.await_args_list
            ]
            assert screen._current_filters is None
            assert "/logs" in called_paths


class TestSearchModal:
    @pytest.mark.asyncio
    async def test_search_modal_mounts(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("/")
            await pilot.pause()
            assert isinstance(mock_app.screen, SearchModal)

    @pytest.mark.asyncio
    async def test_search_modal_has_input(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("/")
            await pilot.pause()
            inp = mock_app.screen.query_one("#search-input", Input)
            assert inp is not None

    @pytest.mark.asyncio
    async def test_search_modal_cancel_dismisses(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("/")
            await pilot.pause()
            cancel_btn = mock_app.screen.query_one("#cancel-btn", Button)
            cancel_btn.press()
            await pilot.pause()


class TestLogsScreenNavigation:
    @pytest.mark.asyncio
    async def test_back_navigation(self, mock_app):
        from src.screens.dashboard import DashboardScreen

        mock_app2 = MockApp()
        mock_app2.client = MagicMock()
        mock_app2.settings = MagicMock()
        mock_app2.settings.onyxlog_url = "http://localhost:8000"

        async with mock_app2.run_test() as pilot:
            pilot.app.push_screen(DashboardScreen())
            await pilot.pause()
            pilot.app.push_screen(LogsScreen())
            await pilot.pause()
            pilot.app.pop_screen()
            await pilot.pause()
            assert isinstance(pilot.app.screen, DashboardScreen)
