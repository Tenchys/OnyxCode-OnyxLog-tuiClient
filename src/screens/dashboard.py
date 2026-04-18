from __future__ import annotations

from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class DashboardScreen(Screen):
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> None:
        yield Header()
        yield Static("Dashboard - Coming in Phase 9")
        yield Footer()
