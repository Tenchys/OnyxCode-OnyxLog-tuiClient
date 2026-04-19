from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from textual.app import App
from textual.widgets import Button, DataTable, Input, Static

from src.api.client import ApiClientError
from src.screens.login import LoginScreen
from src.screens.settings import (
    DeleteKeyConfirmModal,
    LogoutConfirmModal,
    SettingsScreen,
)


class MockApp(App):
    CSS_PATH = None

    def __init__(self) -> None:
        super().__init__()
        self.client = MagicMock()
        self.client.health_check = AsyncMock(
            return_value=MagicMock(status="ok", version="1.0.0")
        )
        self.client.clear_api_key = MagicMock()
        self.settings = MagicMock()
        self.settings.onyxlog_url = "http://localhost:8000"
        self.settings.save_to_file = MagicMock()
        self._reconnect_client = MagicMock()

    def on_mount(self) -> None:
        self.push_screen(SettingsScreen())


@pytest.fixture
def mock_app():
    return MockApp()


def get_screen(app):
    return app.screen


class TestSettingsScreenMount:
    @pytest.mark.asyncio
    async def test_screen_mounts(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            assert isinstance(screen, SettingsScreen)

    @pytest.mark.asyncio
    async def test_has_title(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            title = screen.query_one("#settings-title", Static)
            assert title is not None
            assert "Settings" in title.render().plain

    @pytest.mark.asyncio
    async def test_has_url_input(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            url_input = screen.query_one("#url-input", Input)
            assert url_input is not None

    @pytest.mark.asyncio
    async def test_has_save_url_button(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            save_btn = screen.query_one("#btn-save-url", Button)
            assert save_btn is not None
            assert save_btn.label.plain == "Save"

    @pytest.mark.asyncio
    async def test_has_health_status(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            health_status = screen.query_one("#health-status", Static)
            assert health_status is not None

    @pytest.mark.asyncio
    async def test_has_check_health_button(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            check_btn = screen.query_one("#btn-check-health", Button)
            assert check_btn is not None
            assert check_btn.label.plain == "Check"

    @pytest.mark.asyncio
    async def test_has_keys_table(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            keys_table = screen.query_one("#keys-table", DataTable)
            assert keys_table is not None

    @pytest.mark.asyncio
    async def test_has_delete_key_button(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            delete_btn = screen.query_one("#btn-delete-key", Button)
            assert delete_btn is not None
            assert delete_btn.label.plain == "Delete Selected"

    @pytest.mark.asyncio
    async def test_has_logout_button(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            logout_btn = screen.query_one("#btn-logout", Button)
            assert logout_btn is not None
            assert logout_btn.label.plain == "Logout"


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_shows_connected(self, mock_app):
        mock_app.client.health_check = AsyncMock(
            return_value=MagicMock(status="ok", version="1.0.0")
        )

        with patch(
            "src.screens.settings.db.list_keys", new_callable=AsyncMock, return_value=[]
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.pause()
                screen = get_screen(mock_app)
                health_status = screen.query_one("#health-status", Static)
                health_text = health_status.render().plain
                assert "Connected" in health_text

    @pytest.mark.asyncio
    async def test_health_check_shows_disconnected_on_error(self, mock_app):
        mock_app.client.health_check = AsyncMock(
            side_effect=ApiClientError("CONNECTION_ERROR", 0, "Cannot connect")
        )

        with patch(
            "src.screens.settings.db.list_keys", new_callable=AsyncMock, return_value=[]
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.pause()
                screen = get_screen(mock_app)
                health_status = screen.query_one("#health-status", Static)
                health_text = health_status.render().plain
                assert "Disconnected" in health_text

    @pytest.mark.asyncio
    async def test_health_check_button_triggers_check(self, mock_app):
        mock_app.client.health_check = AsyncMock(
            return_value=MagicMock(status="ok", version="1.0.0")
        )

        with patch(
            "src.screens.settings.db.list_keys", new_callable=AsyncMock, return_value=[]
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.pause()
                screen = get_screen(mock_app)
                check_btn = screen.query_one("#btn-check-health", Button)
                check_btn.press()
                await pilot.pause()
                mock_app.client.health_check.assert_called()


class TestApiKeysList:
    @pytest.mark.asyncio
    async def test_load_keys_populates_table(self, mock_app):
        mock_keys = [
            {
                "id": "key-1",
                "name": "test-key",
                "key_type": "user",
                "role": "admin",
                "created_at": "2026-04-19T10:00:00+00:00",
                "is_active": 1,
            },
            {
                "id": "key-2",
                "name": "app-key",
                "key_type": "application",
                "role": "viewer",
                "created_at": "2026-04-18T10:00:00+00:00",
                "is_active": 0,
            },
        ]

        with patch(
            "src.screens.settings.db.list_keys",
            new_callable=AsyncMock,
            return_value=mock_keys,
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.pause()
                screen = get_screen(mock_app)
                table = screen.query_one("#keys-table", DataTable)
                assert table.row_count == 2


class TestSaveUrl:
    @pytest.mark.asyncio
    async def test_save_url_updates_settings(self, mock_app):
        mock_app.settings.save_to_file = MagicMock()

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            url_input = screen.query_one("#url-input", Input)
            url_input.value = "http://new-server:8000"

            save_btn = screen.query_one("#btn-save-url", Button)
            save_btn.press()
            await pilot.pause()

            assert mock_app.settings.onyxlog_url == "http://new-server:8000"
            mock_app.settings.save_to_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_url_empty_shows_error(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            url_input = screen.query_one("#url-input", Input)
            url_input.value = ""

            save_btn = screen.query_one("#btn-save-url", Button)
            save_btn.press()
            await pilot.pause()

            notifications = list(mock_app._notifications)
            assert len(notifications) > 0
            last_notification = notifications[-1]
            assert last_notification.severity == "error"

    @pytest.mark.asyncio
    async def test_save_url_unchanged_shows_info(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            url_input = screen.query_one("#url-input", Input)
            url_input.value = "http://localhost:8000"

            save_btn = screen.query_one("#btn-save-url", Button)
            save_btn.press()
            await pilot.pause()

            notifications = list(mock_app._notifications)
            assert len(notifications) > 0
            assert notifications[-1].severity == "information"

    @pytest.mark.asyncio
    async def test_save_url_failure_notifies_error(self, mock_app):
        mock_app.settings.save_to_file = MagicMock(
            side_effect=RuntimeError("disk error")
        )

        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            url_input = screen.query_one("#url-input", Input)
            url_input.value = "http://other-server:8000"

            save_btn = screen.query_one("#btn-save-url", Button)
            save_btn.press()
            await pilot.pause()

            notifications = list(mock_app._notifications)
            assert len(notifications) > 0
            assert notifications[-1].severity == "error"


class TestDeleteKey:
    @pytest.mark.asyncio
    async def test_delete_key_without_selection_shows_warning(self, mock_app):
        with patch(
            "src.screens.settings.db.list_keys", new_callable=AsyncMock, return_value=[]
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                screen = get_screen(mock_app)
                delete_btn = screen.query_one("#btn-delete-key", Button)
                delete_btn.press()
                await pilot.pause()

                notifications = list(mock_app._notifications)
                assert len(notifications) > 0
                last_notification = notifications[-1]
                assert last_notification.severity == "warning"

    @pytest.mark.asyncio
    async def test_handle_delete_confirm_runs_worker_when_confirmed(self):
        screen = SettingsScreen()
        screen.run_worker = MagicMock(side_effect=lambda coro: coro.close())

        screen._handle_delete_confirm(True)
        screen.run_worker.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_selected_key_out_of_bounds_no_delete(self):
        mock_app = MockApp()
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)

            table = MagicMock()
            table.cursor_row = 5
            screen.query_one = MagicMock(return_value=table)

            with (
                patch(
                    "src.screens.settings.db.list_keys",
                    new_callable=AsyncMock,
                    return_value=[{"id": "key-1", "name": "k1", "is_active": 0}],
                ) as mock_list_keys,
                patch(
                    "src.screens.settings.db.delete_key", new_callable=AsyncMock
                ) as mock_delete,
            ):
                await screen._delete_selected_key()

                mock_list_keys.assert_called_once()
                mock_delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_selected_key_non_active_refreshes_keys(self):
        mock_app = MockApp()
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)

            table = MagicMock()
            table.cursor_row = 0
            screen.query_one = MagicMock(return_value=table)
            screen.notify = MagicMock()
            screen.run_worker = MagicMock(side_effect=lambda coro: coro.close())

            with (
                patch(
                    "src.screens.settings.db.list_keys",
                    new_callable=AsyncMock,
                    return_value=[{"id": "key-1", "name": "k1", "is_active": 0}],
                ),
                patch(
                    "src.screens.settings.db.delete_key", new_callable=AsyncMock
                ) as mock_delete,
            ):
                await screen._delete_selected_key()

                mock_delete.assert_called_once_with("key-1")
                screen.run_worker.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_selected_key_active_triggers_logout(self):
        mock_app = MockApp()
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)

            table = MagicMock()
            table.cursor_row = 0
            screen.query_one = MagicMock(return_value=table)
            screen.notify = MagicMock()
            screen._do_logout = AsyncMock()
            screen.run_worker = MagicMock(side_effect=lambda coro: coro.close())

            with (
                patch(
                    "src.screens.settings.db.list_keys",
                    new_callable=AsyncMock,
                    return_value=[{"id": "key-1", "name": "k1", "is_active": 1}],
                ),
                patch(
                    "src.screens.settings.db.delete_key", new_callable=AsyncMock
                ) as mock_delete,
            ):
                await screen._delete_selected_key()

                mock_delete.assert_called_once_with("key-1")
                screen._do_logout.assert_awaited_once()


class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_button_shows_confirm_modal(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            logout_btn = screen.query_one("#btn-logout", Button)
            logout_btn.press()
            await pilot.pause()

            modal = mock_app.screen
            assert isinstance(modal, LogoutConfirmModal)

    @pytest.mark.asyncio
    async def test_logout_deactivates_active_key_and_navigates_login(self, mock_app):
        with (
            patch(
                "src.screens.settings.db.get_active_key",
                new_callable=AsyncMock,
                return_value={"id": "active-key-id"},
            ) as mock_get_active_key,
            patch(
                "src.screens.settings.db.deactivate_key", new_callable=AsyncMock
            ) as mock_deactivate_key,
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                screen = get_screen(mock_app)
                await screen._do_logout()
                await pilot.pause()

                mock_get_active_key.assert_called_once_with(
                    server_url="http://localhost:8000"
                )
                mock_deactivate_key.assert_called_once_with("active-key-id")
                mock_app.client.clear_api_key.assert_called_once()
                assert isinstance(mock_app.screen, LoginScreen)


class TestLogoutConfirmModal:
    @pytest.mark.asyncio
    async def test_modal_composes_correctly(self, mock_app):
        test_app = App()
        test_app.client = MagicMock()
        test_app.push_screen(LogoutConfirmModal())

        async with test_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            current_screen = test_app.screen
            assert hasattr(current_screen, "query_one")
            assert hasattr(current_screen, "on_button_pressed")

    @pytest.mark.asyncio
    async def test_modal_dismisses_on_cancel(self, mock_app):
        test_app = App()
        test_app.client = MagicMock()
        test_app.push_screen(LogoutConfirmModal())

        async with test_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            current_screen = test_app.screen
            assert hasattr(current_screen, "query_one")


class TestDeleteKeyConfirmModal:
    @pytest.mark.asyncio
    async def test_modal_composes_correctly(self, mock_app):
        test_app = App()
        test_app.client = MagicMock()
        test_app.push_screen(DeleteKeyConfirmModal(key_name="my-test-key"))

        async with test_app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            current_screen = test_app.screen
            assert hasattr(current_screen, "query_one")


class TestConfirmModals:
    def test_logout_confirm_modal_confirm_and_cancel(self):
        modal = LogoutConfirmModal()
        modal.dismiss = MagicMock()

        confirm_event = MagicMock()
        confirm_event.button.id = "confirm-btn"
        modal.on_button_pressed(confirm_event)
        modal.dismiss.assert_called_once_with(True)

        modal.dismiss.reset_mock()
        cancel_event = MagicMock()
        cancel_event.button.id = "cancel-btn"
        modal.on_button_pressed(cancel_event)
        modal.dismiss.assert_called_once_with(False)

    def test_delete_key_confirm_modal_confirm_and_cancel(self):
        modal = DeleteKeyConfirmModal(key_name="test-key")
        modal.dismiss = MagicMock()

        confirm_event = MagicMock()
        confirm_event.button.id = "confirm-btn"
        modal.on_button_pressed(confirm_event)
        modal.dismiss.assert_called_once_with(True)

        modal.dismiss.reset_mock()
        cancel_event = MagicMock()
        cancel_event.button.id = "cancel-btn"
        modal.on_button_pressed(cancel_event)
        modal.dismiss.assert_called_once_with(False)


class TestNavigation:
    @pytest.mark.asyncio
    async def test_escape_goes_back(self, mock_app):
        async with mock_app.run_test() as pilot:
            await pilot.pause()
            screen = get_screen(mock_app)
            assert isinstance(screen, SettingsScreen)
            await pilot.press("escape")
            await pilot.pause()

    @pytest.mark.asyncio
    async def test_r_key_refreshes(self, mock_app):
        with patch(
            "src.screens.settings.db.list_keys", new_callable=AsyncMock, return_value=[]
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.pause()
                await pilot.press("r")
                await pilot.pause()
