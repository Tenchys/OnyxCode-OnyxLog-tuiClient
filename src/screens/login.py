from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from src import db
from src.api.auth import login, register
from src.api.client import ApiClientError

ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": "Invalid username or password",
    "DUPLICATE_ENTRY": "Username or email already exists",
    "CONNECTION_ERROR": "Cannot connect to server. Check URL and try again.",
    "VALIDATION_ERROR": "Please check the form fields.",
    "TIMEOUT": "Server is taking too long to respond.",
}


class LoginScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("enter", "submit", "Submit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("OnyxLog", id="login-title", classes="login-title"),
            Label("Username", id="username-label"),
            Input(placeholder="Enter your username", id="username-input"),
            Label("Email (optional, for registration)", id="email-label"),
            Input(placeholder="Enter your email", id="email-input"),
            Label("Password", id="password-label"),
            Input(
                placeholder="Enter your password", id="password-input", password=True
            ),
            Container(
                Button("Login", variant="primary", id="login-btn"),
                Button("Register", variant="default", id="register-btn"),
                classes="button-row",
            ),
            id="login-container",
            classes="login-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#username-input", Input).focus()

    async def _handle_auth(self, action: str) -> None:
        username = self.query_one("#username-input", Input).value.strip()
        email = self.query_one("#email-input", Input).value.strip()
        password = self.query_one("#password-input", Input).value

        if not username or not password:
            self.notify("Username and password are required", severity="error")
            return

        if action == "register" and not email:
            self.notify("Email is required for registration", severity="error")
            return

        client = self.app.client

        try:
            if action == "login":
                result = await login(client, username, password)
            else:
                result = await register(client, username, email, password)

            api_key = result.get_api_key()
            client.set_api_key(api_key)

            await db.store_key(
                id=result.get_key_id() or "unknown",
                name=f"{username}-key",
                key=api_key,
                key_type="user",
                server_url=self.app.settings.onyxlog_url,
                role=result.get_role() or "viewer",
                user_id=str(result.user.id),
            )

            from src.screens.dashboard import DashboardScreen

            self.app.push_screen(DashboardScreen())

        except ApiClientError as e:
            message = ERROR_MESSAGES.get(e.error_code, e.message)
            self.notify(message, severity="error")
        except Exception as e:
            import traceback

            from rich.markup import escape

            error_detail = escape(f"{type(e).__name__}: {e}")
            self.notify(f"Error: {error_detail}", severity="error", timeout=10)
            # Log full traceback to console for debugging
            traceback.print_exc()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login-btn":
            self.run_worker(self._handle_auth("login"))
        elif event.button.id == "register-btn":
            self.run_worker(self._handle_auth("register"))

    def action_submit(self) -> None:
        self.run_worker(self._handle_auth("login"))
