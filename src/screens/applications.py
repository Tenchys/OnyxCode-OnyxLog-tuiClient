from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)

from src import db
from src.api.applications import (
    create_app_key,
    create_application,
    delete_application,
    list_applications,
)
from src.api.client import ApiClientError
from src.models.schemas import ApiKeyCreate, AppCreate, AppRead

ERROR_MESSAGES = {
    "CONNECTION_ERROR": "Cannot connect to server. Check URL and try again.",
    "VALIDATION_ERROR": "Please check the form fields.",
    "DUPLICATE_ENTRY": "An application with this ID already exists.",
    "TIMEOUT": "Server is taking too long to respond.",
}


class ApplicationsScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "go_back", "Back"),
        ("n", "new_app", "New"),
        ("d", "delete_app", "Delete"),
        ("enter", "detail", "Detail"),
        ("r", "refresh", "Refresh"),
        ("k", "create_key", "Key"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._loaded_apps: list[AppRead] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Applications", id="apps-title", classes="section-title"),
            DataTable(
                id="apps-table",
                cursor_type="row",
            ),
            id="apps-container",
        )
        yield Footer()

    async def on_mount(self) -> None:
        table = self.query_one("#apps-table", DataTable)
        table.add_columns("Name", "App ID", "Environment", "Status")
        self.run_worker(self._load_applications())

    async def _load_applications(self) -> None:
        table = self.query_one("#apps-table", DataTable)
        table.loading = True
        try:
            client = self.app.client
            result = await list_applications(client)
            self._loaded_apps = list(result.items)
            table.clear()
            for app in self._loaded_apps:
                status = "Active" if app.is_active else "Inactive"
                table.add_row(app.name, app.app_id, app.environment, status)
        except ApiClientError as e:
            self.notify(ERROR_MESSAGES.get(e.error_code, e.message), severity="error")
        except Exception:
            self.notify("Unable to load applications", severity="error")
        finally:
            table.loading = False

    def action_new_app(self) -> None:
        self.app.push_screen(CreateAppModal(), self._handle_app_created)

    def _get_selected_app(self) -> AppRead | None:
        table = self.query_one("#apps-table", DataTable)
        if table.row_count == 0:
            return None
        selected_row = table.cursor_row
        if selected_row is None:
            return None
        if selected_row < 0 or selected_row >= len(self._loaded_apps):
            return None
        return self._loaded_apps[selected_row]

    def action_delete_app(self) -> None:
        selected_app = self._get_selected_app()
        if selected_app is None:
            self.notify("Select an application first", severity="warning")
            return
        self.app.push_screen(ConfirmDeleteModal(), self._handle_delete_confirm)

    def action_detail(self) -> None:
        selected_app = self._get_selected_app()
        if selected_app is None:
            self.notify("Select an application first", severity="warning")
            return
        self.notify(
            f"Detail view for '{selected_app.app_id}' coming soon",
            severity="information",
        )

    def action_refresh(self) -> None:
        self.run_worker(self._load_applications())

    def action_create_key(self) -> None:
        selected_app = self._get_selected_app()
        if selected_app is None:
            self.notify("Select an application first", severity="warning")
            return
        self.app.push_screen(
            CreateApiKeyModal(app_id=str(selected_app.id)), self._handle_key_created
        )

    def _handle_app_created(self, created: bool) -> None:
        if created:
            self.run_worker(self._load_applications())

    async def _handle_delete_confirm(self, confirmed: bool) -> None:
        if not confirmed:
            return
        selected_app = self._get_selected_app()
        if selected_app is None:
            return
        try:
            await delete_application(self.app.client, str(selected_app.id))
            self.notify("Application deleted", severity="information")
            self.run_worker(self._load_applications())
        except ApiClientError as e:
            self.notify(ERROR_MESSAGES.get(e.error_code, e.message), severity="error")

    async def _handle_key_created(self, result: dict | None) -> None:
        if result is None:
            return
        try:
            await db.store_key(
                id=str(result["id"]),
                name=str(result["name"]),
                key=str(result["key"]),
                key_type="application",
                server_url=self.app.settings.onyxlog_url,
                app_id=str(result["app_id"]),
            )
        except Exception:
            self.notify(
                "API key created, but could not be saved locally",
                severity="warning",
            )
        self.notify("API key created successfully", severity="information")


class CreateAppModal(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Create Application", id="modal-title"),
            Label("Name", id="name-label"),
            Input(placeholder="Application name", id="name-input"),
            Label("App ID", id="appid-label"),
            Input(placeholder="unique-app-id", id="appid-input"),
            Label("Environment", id="env-label"),
            Select(
                [
                    ("Development", "development"),
                    ("Testing", "testing"),
                    ("Production", "production"),
                ],
                id="env-select",
            ),
            Label("Description (optional)", id="desc-label"),
            Input(placeholder="Description", id="desc-input"),
            Container(
                Button("Create", variant="primary", id="create-btn"),
                Button("Cancel", variant="default", id="cancel-btn"),
                classes="button-row",
            ),
            id="modal-container",
            classes="modal-container",
        )

    def on_mount(self) -> None:
        self.query_one("#name-input", Input).focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(False)
        elif event.button.id == "create-btn":
            await self._handle_create()

    async def _handle_create(self) -> None:
        name = self.query_one("#name-input", Input).value.strip()
        app_id = self.query_one("#appid-input", Input).value.strip()
        environment = self.query_one("#env-select", Select).value
        description = self.query_one("#desc-input", Input).value.strip() or None

        if not name or not app_id or not environment:
            self.notify("Name, App ID, and Environment are required", severity="error")
            return

        try:
            app = AppCreate(
                name=name,
                app_id=app_id,
                environment=environment,
                description=description,
            )
            await create_application(self.app.client, app)
            self.dismiss(True)
        except ApiClientError as e:
            self.notify(ERROR_MESSAGES.get(e.error_code, e.message), severity="error")


class CreateApiKeyModal(ModalScreen[dict | None]):
    def __init__(self, app_id: str | None = None) -> None:
        super().__init__()
        self._app_id = app_id
        self._created_result: dict | None = None

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Create API Key", id="modal-title"),
            Label("Key Name", id="name-label"),
            Input(placeholder="My API Key", id="name-input"),
            Label("", id="key-display"),
            Container(
                Button("Create", variant="primary", id="create-btn"),
                Button("Close", variant="default", id="close-btn"),
                classes="button-row",
            ),
            id="modal-container",
            classes="modal-container",
        )

    def on_mount(self) -> None:
        self.query_one("#name-input", Input).focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss(self._created_result)
        elif event.button.id == "create-btn":
            await self._handle_create()

    async def _handle_create(self) -> None:
        name = self.query_one("#name-input", Input).value.strip()
        if not name:
            self.notify("Key name is required", severity="error")
            return

        if self._app_id:
            app_id = self._app_id
        else:
            self.notify("No application selected", severity="error")
            return

        try:
            key_data = ApiKeyCreate(name=name, key_type="application")
            result = await create_app_key(self.app.client, app_id, key_data)
            key_display = self.query_one("#key-display", Label)
            key_display.update(f"Key: {result.key}")
            self.query_one("#name-input", Input).disabled = True
            self.query_one("#create-btn", Button).disabled = True
            self._created_result = {
                "id": result.id,
                "key": result.key,
                "name": result.name,
                "app_id": app_id,
            }
        except ApiClientError as e:
            self.notify(ERROR_MESSAGES.get(e.error_code, e.message), severity="error")


class ConfirmDeleteModal(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Delete Application", id="modal-title"),
            Label("Are you sure you want to delete this application?"),
            Label("This action cannot be undone."),
            Container(
                Button("Delete", variant="error", id="confirm-btn"),
                Button("Cancel", variant="default", id="cancel-btn"),
                classes="button-row",
            ),
            id="modal-container",
            classes="modal-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            self.dismiss(True)
        else:
            self.dismiss(False)
