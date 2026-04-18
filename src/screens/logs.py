from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class LogsScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Logs Screen - Coming in Phase 13")
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()
