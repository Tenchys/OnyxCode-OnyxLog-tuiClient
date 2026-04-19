from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Static

from src import db
from src.api.client import ApiClientError


class SettingsScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "go_back", "Back"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Static("Settings", id="settings-title", classes="section-title"),
                self._build_server_section(),
                self._build_health_section(),
                self._build_keys_section(),
                self._build_account_section(),
                id="settings-content",
            ),
            id="settings-main",
        )
        yield Footer()

    def _build_server_section(self) -> Container:
        return Container(
            Static("Server Configuration", classes="section-label"),
            Horizontal(
                Static("URL:", id="url-label"),
                Input(placeholder="http://localhost:8000", id="url-input"),
                Button("Save", variant="primary", id="btn-save-url"),
                id="url-row",
            ),
            id="server-container",
            classes="settings-container",
        )

    def _build_health_section(self) -> Container:
        return Container(
            Static("Server Health", classes="section-label"),
            Horizontal(
                Static("Status:", id="health-label"),
                Static("Unknown", id="health-status", classes="health-unknown"),
                Button("Check", variant="default", id="btn-check-health"),
                id="health-row",
            ),
            id="health-container",
            classes="settings-container",
        )

    def _build_keys_section(self) -> Container:
        return Container(
            Static("Saved API Keys", classes="section-label"),
            DataTable(id="keys-table", cursor_type="row"),
            Horizontal(
                Button("Delete Selected", variant="error", id="btn-delete-key"),
                id="keys-actions",
            ),
            id="keys-container",
            classes="settings-container",
        )

    def _build_account_section(self) -> Container:
        return Container(
            Static("Account", classes="section-label"),
            Button("Logout", variant="error", id="btn-logout"),
            id="account-container",
            classes="settings-container",
        )

    async def on_mount(self) -> None:
        url_input = self.query_one("#url-input", Input)
        url_input.value = self.app.settings.onyxlog_url

        keys_table = self.query_one("#keys-table", DataTable)
        keys_table.add_columns("Name", "Type", "Role", "Created", "Active")

        self.run_worker(self._load_keys())
        self.run_worker(self._check_health())

    async def _check_health(self) -> None:
        status = self.query_one("#health-status", Static)
        status.update("Checking...")
        status.remove_class("health-ok")
        status.remove_class("health-error")
        status.add_class("health-unknown")

        try:
            await self.app.client.health_check()
            status.update("Connected")
            status.remove_class("health-unknown")
            status.remove_class("health-error")
            status.add_class("health-ok")
        except ApiClientError:
            status.update("Disconnected")
            status.remove_class("health-unknown")
            status.remove_class("health-ok")
            status.add_class("health-error")

    async def _load_keys(self) -> None:
        table = self.query_one("#keys-table", DataTable)
        table.loading = True
        try:
            keys = await db.list_keys(server_url=self.app.settings.onyxlog_url)
            table.clear()
            for key in keys:
                created = key.get("created_at", "")
                try:
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    created_fmt = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    created_fmt = created
                active = "Yes" if key.get("is_active") else "No"
                table.add_row(
                    key.get("name", ""),
                    key.get("key_type", ""),
                    key.get("role", "-"),
                    created_fmt,
                    active,
                )
        except Exception:
            self.notify("Unable to load API keys", severity="error")
        finally:
            table.loading = False

    def action_refresh(self) -> None:
        self.run_worker(self._load_keys())
        self.run_worker(self._check_health())

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save-url":
            self._handle_save_url()
        elif event.button.id == "btn-check-health":
            self.run_worker(self._check_health())
        elif event.button.id == "btn-logout":
            self.app.push_screen(LogoutConfirmModal(), self._handle_logout_confirm)
        elif event.button.id == "btn-delete-key":
            self._handle_delete_key()

    def _handle_save_url(self) -> None:
        url_input = self.query_one("#url-input", Input)
        new_url = url_input.value.strip()

        if not new_url:
            self.notify("URL cannot be empty", severity="error")
            return

        current_url = self.app.settings.onyxlog_url
        if new_url == current_url:
            self.notify("URL is unchanged", severity="information")
            return

        self.app.settings.onyxlog_url = new_url
        try:
            self.app.settings.save_to_file()
            self.app._reconnect_client(new_url)
            self.notify("URL saved. Reconnecting...", severity="information")
            self.run_worker(self._check_health())
        except Exception as e:
            self.notify(f"Failed to save URL: {e}", severity="error")

    def _handle_delete_key(self) -> None:
        table = self.query_one("#keys-table", DataTable)
        if table.row_count == 0:
            self.notify("No API key selected", severity="warning")
            return

        cursor_row = table.cursor_row
        if cursor_row is None:
            self.notify("Select an API key to delete", severity="warning")
            return

        row_values = table.get_row_at(cursor_row)
        key_name = str(row_values[0]) if row_values else None
        self.app.push_screen(
            DeleteKeyConfirmModal(key_name=key_name), self._handle_delete_confirm
        )

    def _handle_delete_confirm(self, confirmed: bool) -> None:
        if confirmed:
            self.run_worker(self._delete_selected_key())

    async def _delete_selected_key(self) -> None:
        table = self.query_one("#keys-table", DataTable)
        cursor_row = table.cursor_row
        if cursor_row is None:
            return

        keys = await db.list_keys(server_url=self.app.settings.onyxlog_url)
        if cursor_row >= len(keys):
            return

        key = keys[cursor_row]
        key_id = key.get("id")
        key_name = key.get("name")
        is_active = bool(key.get("is_active"))

        try:
            await db.delete_key(key_id)
            self.notify(
                f"API key '{key_name or 'unknown'}' deleted", severity="information"
            )

            if is_active:
                await self._do_logout()
            else:
                self.run_worker(self._load_keys())
        except Exception as e:
            self.notify(f"Failed to delete key: {e}", severity="error")

    def _handle_logout_confirm(self, confirmed: bool) -> None:
        if confirmed:
            self.run_worker(self._do_logout())

    async def _do_logout(self) -> None:
        active_key = await db.get_active_key(
            server_url=self.app.settings.onyxlog_url,
            key_type="user",
        )
        if active_key is not None:
            await db.deactivate_key(active_key["id"])

        self.app.client.clear_api_key()

        from src.screens.login import LoginScreen

        self.app.screen_stack.clear()
        self.app.push_screen(LoginScreen())


class LogoutConfirmModal(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Confirm Logout", id="modal-title"),
            Label("Are you sure you want to logout?"),
            Label("You will need to login again to access the server."),
            Container(
                Button("Logout", variant="error", id="confirm-btn"),
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


class DeleteKeyConfirmModal(ModalScreen[bool]):
    def __init__(self, key_name: str | None = None) -> None:
        super().__init__()
        self._key_name = key_name

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Delete API Key", id="modal-title"),
            Label(
                f"Are you sure you want to delete the API key '{self._key_name or ''}'?"
            ),
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
