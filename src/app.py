from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen

from src.api.client import ApiClientError, OnyxLogClient
from src.config import Settings
from src.db import get_active_key, init_db
from src.screens.dashboard import DashboardScreen
from src.screens.login import LoginScreen


class OnyxLogApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "OnyxLog TUI"
    SUBTITLE = "Log Management Terminal Client"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=1),
        Binding("ctrl+c", "quit", "Quit", priority=1),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._client: OnyxLogClient | None = None
        self._settings: Settings | None = None

    @property
    def client(self) -> OnyxLogClient:
        if self._client is None:
            url = self.settings.onyxlog_url
            self._client = OnyxLogClient(base_url=url)
        return self._client

    @property
    def settings(self) -> Settings:
        if self._settings is None:
            self._settings = Settings()
        return self._settings

    def compose(self) -> ComposeResult:
        yield Screen()

    async def on_mount(self) -> None:
        await init_db()
        await self._try_auto_login()

    async def _try_auto_login(self) -> None:
        active_key = await get_active_key(self.settings.onyxlog_url)
        if active_key is None:
            self.push_screen(LoginScreen())
            return

        self.client.set_api_key(active_key["key"])
        try:
            await self.client.health_check()
            self.push_screen(DashboardScreen())
        except ApiClientError:
            self.push_screen(LoginScreen())

    async def on_unmount(self) -> None:
        if self._client is not None:
            await self._client.close()

    def _reconnect_client(self, new_url: str) -> None:
        self._client = None

    def action_quit(self) -> None:
        self.exit()


def main() -> None:
    app = OnyxLogApp()
    app.run()


if __name__ == "__main__":
    main()
