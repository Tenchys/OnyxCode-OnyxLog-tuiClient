from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from textual.app import App
from textual.widgets import Button, DataTable, Input, Label, Select, Static

from src.api.client import ApiClientError
from src.models.schemas import ApiKeyCreateResponse, AppRead, PaginatedResponse
from src.screens.applications import (
    ApplicationsScreen,
    ConfirmDeleteModal,
    CreateApiKeyModal,
    CreateAppModal,
)


class MockApp(App):
    CSS_PATH = None

    def __init__(self) -> None:
        super().__init__()
        self.client = MagicMock()
        self.settings = MagicMock()
        self.settings.onyxlog_url = "http://localhost:8000"

    def on_mount(self) -> None:
        self.push_screen(ApplicationsScreen())


@pytest.fixture
def mock_app() -> MockApp:
    return MockApp()


def mock_app_read(
    app_uuid: str,
    name: str,
    app_id: str,
    environment: str,
    is_active: bool,
    description: str | None = None,
) -> AppRead:
    return AppRead(
        id=app_uuid,
        name=name,
        app_id=app_id,
        description=description,
        environment=environment,
        is_active=is_active,
        created_at=datetime.now(),
    )


def make_paginated_result(apps: list[AppRead]) -> PaginatedResponse[AppRead]:
    return PaginatedResponse[AppRead](items=apps, total=len(apps), limit=50, offset=0)


class TestApplicationsScreen:
    @pytest.mark.asyncio
    async def test_mounts_with_title_and_datatable(self, mock_app: MockApp) -> None:
        with patch(
            "src.screens.applications.list_applications",
            new_callable=AsyncMock,
            return_value=make_paginated_result([]),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                screen = mock_app.screen
                assert isinstance(screen, ApplicationsScreen)

                title = screen.query_one("#apps-title", Static)
                assert "Applications" in title.render().plain

                table = screen.query_one("#apps-table", DataTable)
                assert table is not None

    @pytest.mark.asyncio
    async def test_mount_loads_applications_in_table(self, mock_app: MockApp) -> None:
        apps = [
            mock_app_read(
                "550e8400-e29b-41d4-a716-446655440001",
                "Main App",
                "main-app",
                "production",
                True,
            ),
            mock_app_read(
                "550e8400-e29b-41d4-a716-446655440002",
                "Dev App",
                "dev-app",
                "development",
                False,
            ),
        ]
        with patch(
            "src.screens.applications.list_applications",
            new_callable=AsyncMock,
            return_value=make_paginated_result(apps),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.pause()

                table = mock_app.screen.query_one("#apps-table", DataTable)
                assert table.row_count == 2

    @pytest.mark.asyncio
    async def test_binding_n_opens_create_app_modal(self, mock_app: MockApp) -> None:
        with patch(
            "src.screens.applications.list_applications",
            new_callable=AsyncMock,
            return_value=make_paginated_result([]),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("n")
                await pilot.pause()

                assert isinstance(mock_app.screen, CreateAppModal)

    @pytest.mark.asyncio
    async def test_binding_r_triggers_refresh(self, mock_app: MockApp) -> None:
        list_mock = AsyncMock(return_value=make_paginated_result([]))
        with patch("src.screens.applications.list_applications", new=list_mock):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("r")
                await pilot.pause()

                assert list_mock.await_count >= 2

    @pytest.mark.asyncio
    async def test_binding_d_deletes_selected_application(
        self, mock_app: MockApp
    ) -> None:
        apps = [
            mock_app_read(
                "550e8400-e29b-41d4-a716-446655440001",
                "Main App",
                "main-app",
                "production",
                True,
            )
        ]
        delete_mock = AsyncMock(return_value=None)
        with (
            patch(
                "src.screens.applications.list_applications",
                new_callable=AsyncMock,
                return_value=make_paginated_result(apps),
            ),
            patch("src.screens.applications.delete_application", new=delete_mock),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.pause()

                screen = mock_app.screen
                table = screen.query_one("#apps-table", DataTable)
                table.move_cursor(row=0)

                await pilot.press("d")
                await pilot.pause()
                assert isinstance(mock_app.screen, ConfirmDeleteModal)

                confirm_btn = mock_app.screen.query_one("#confirm-btn", Button)
                confirm_btn.press()
                await pilot.pause()
                await pilot.pause()

                assert isinstance(mock_app.screen, ApplicationsScreen)
                delete_mock.assert_awaited_once()
                call_args = delete_mock.await_args.args
                assert call_args[0] is mock_app.client
                assert call_args[1] == "main-app"

    @pytest.mark.asyncio
    async def test_binding_enter_configured_and_detail_action_notifies(
        self, mock_app: MockApp
    ) -> None:
        apps = [
            mock_app_read(
                "550e8400-e29b-41d4-a716-446655440001",
                "Main App",
                "main-app",
                "production",
                True,
            )
        ]
        with patch(
            "src.screens.applications.list_applications",
            new_callable=AsyncMock,
            return_value=make_paginated_result(apps),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.pause()

                table = mock_app.screen.query_one("#apps-table", DataTable)
                table.move_cursor(row=0)

                keys = {binding[0] for binding in mock_app.screen.BINDINGS}
                assert "enter" in keys

                mock_app.screen.action_detail()
                await pilot.pause()

                notifications = list(mock_app._notifications)
                assert any("coming soon" in str(n.message) for n in notifications)


class TestCreateAppModal:
    @pytest.mark.asyncio
    async def test_create_application_success(self, mock_app: MockApp) -> None:
        create_mock = AsyncMock(
            return_value=mock_app_read(
                "550e8400-e29b-41d4-a716-446655440001",
                "Main App",
                "main-app",
                "production",
                True,
            )
        )
        with (
            patch(
                "src.screens.applications.list_applications",
                new_callable=AsyncMock,
                return_value=make_paginated_result([]),
            ),
            patch("src.screens.applications.create_application", new=create_mock),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("n")
                await pilot.pause()

                modal = mock_app.screen
                assert isinstance(modal, CreateAppModal)

                modal.query_one("#name-input", Input).value = "Main App"
                modal.query_one("#appid-input", Input).value = "main-app"
                modal.query_one("#desc-input", Input).value = "Production app"
                modal.query_one("#env-select", Select).value = "production"

                modal.query_one("#create-btn", Button).press()
                await pilot.pause()
                await pilot.pause()

                assert isinstance(mock_app.screen, ApplicationsScreen)
                create_mock.assert_awaited_once()
                call_args = create_mock.await_args.args
                assert call_args[0] is mock_app.client
                app_create = call_args[1]
                assert app_create.name == "Main App"
                assert app_create.app_id == "main-app"

    @pytest.mark.asyncio
    async def test_create_application_duplicate_app_id_shows_error(
        self, mock_app: MockApp
    ) -> None:
        create_mock = AsyncMock(
            side_effect=ApiClientError("DUPLICATE_ENTRY", 409, "Already exists")
        )
        with (
            patch(
                "src.screens.applications.list_applications",
                new_callable=AsyncMock,
                return_value=make_paginated_result([]),
            ),
            patch("src.screens.applications.create_application", new=create_mock),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("n")
                await pilot.pause()

                modal = mock_app.screen
                assert isinstance(modal, CreateAppModal)
                modal.query_one("#name-input", Input).value = "Main App"
                modal.query_one("#appid-input", Input).value = "main-app"
                modal.query_one("#env-select", Select).value = "production"

                modal.query_one("#create-btn", Button).press()
                await pilot.pause()

                assert isinstance(mock_app.screen, CreateAppModal)
                notifications = list(mock_app._notifications)
                assert any(
                    "already exists" in str(n.message).lower() for n in notifications
                )


class TestCreateApiKeyModal:
    @pytest.mark.asyncio
    async def test_create_api_key_success_shows_key_and_closes_on_close(
        self, mock_app: MockApp
    ) -> None:
        apps = [
            mock_app_read(
                "550e8400-e29b-41d4-a716-446655440001",
                "Main App",
                "main-app",
                "production",
                True,
            )
        ]
        create_key_mock = AsyncMock(
            return_value=ApiKeyCreateResponse(
                id="key-1",
                name="Production Key",
                key="olk_123456",
                key_type="application",
            )
        )
        with (
            patch(
                "src.screens.applications.list_applications",
                new_callable=AsyncMock,
                return_value=make_paginated_result(apps),
            ),
            patch("src.screens.applications.create_app_key", new=create_key_mock),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.pause()

                screen = mock_app.screen
                table = screen.query_one("#apps-table", DataTable)
                table.move_cursor(row=0)

                await pilot.press("k")
                await pilot.pause()

                modal = mock_app.screen
                assert isinstance(modal, CreateApiKeyModal)
                modal.query_one("#name-input", Input).value = "Production Key"

                modal.query_one("#create-btn", Button).press()
                await pilot.pause()
                await pilot.pause()

                assert isinstance(mock_app.screen, CreateApiKeyModal)
                create_key_mock.assert_awaited_once()
                call_args = create_key_mock.await_args.args
                assert call_args[0] is mock_app.client
                assert call_args[1] == "main-app"
                key_payload = call_args[2]
                assert key_payload.name == "Production Key"

                key_display = modal.query_one("#key-display", Label)
                assert "olk_123456" in key_display.render().plain

                modal.query_one("#close-btn", Button).press()
                await pilot.pause()
                assert isinstance(mock_app.screen, ApplicationsScreen)


class TestApplicationsScreenErrors:
    @pytest.mark.asyncio
    async def test_connection_error_shows_notification(self, mock_app: MockApp) -> None:
        with patch(
            "src.screens.applications.list_applications",
            new_callable=AsyncMock,
            side_effect=ApiClientError("CONNECTION_ERROR", 0, "Cannot connect"),
        ):
            async with mock_app.run_test() as pilot:
                await pilot.pause()
                await pilot.pause()

                notifications = list(mock_app._notifications)
                assert any("Cannot connect" in str(n.message) for n in notifications)
