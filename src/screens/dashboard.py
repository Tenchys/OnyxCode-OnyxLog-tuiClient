from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from src.api.client import ApiClientError


class DashboardScreen(Screen):
    BINDINGS = [
        ("a", "go_applications", "Applications"),
        ("l", "go_logs", "Logs"),
        ("s", "go_settings", "Settings"),
        ("q", "quit", "Quit"),
        ("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Static(
                    "OnyxLog Dashboard", id="dashboard-title", classes="dashboard-title"
                ),
                Container(
                    Static("Navigation", id="nav-label", classes="section-label"),
                    Horizontal(
                        Button(
                            "Applications", variant="primary", id="btn-applications"
                        ),
                        Button("Logs", variant="primary", id="btn-logs"),
                        Button("Settings", variant="primary", id="btn-settings"),
                        classes="nav-buttons",
                    ),
                    id="nav-container",
                    classes="nav-container",
                ),
                Container(
                    Static(
                        "Statistics Overview", id="stats-label", classes="section-label"
                    ),
                    Static(
                        "Loading stats...", id="stats-content", classes="stats-content"
                    ),
                    id="stats-container",
                    classes="stats-container",
                ),
                id="dashboard-content",
                classes="dashboard-content",
            ),
            id="dashboard-main",
        )
        yield Footer()

    async def on_mount(self) -> None:
        self.run_worker(self._load_stats())

    async def _load_stats(self) -> None:
        stats_widget = self.query_one("#stats-content", Static)
        client = self.app.client

        if not client.is_authenticated:
            stats_widget.update("Not authenticated. Please login.")
            return

        try:
            data = await client._request("GET", "/stats/overview")
            total_logs = data.get("total_logs", 0)
            total_applications = data.get("total_applications", 0)
            active_applications = data.get("active_applications", 0)
            recent_logs_24h = data.get("recent_logs_24h", 0)

            stats_text = (
                f"  Total Logs:       {total_logs:,}\n"
                f"  Total Applications: {total_applications:,}\n"
                f"  Active Applications: {active_applications:,}\n"
                f"  Recent Logs (24h): {recent_logs_24h:,}"
            )
            stats_widget.update(stats_text)
        except ApiClientError:
            stats_widget.update("Unable to load stats")
        except Exception:
            stats_widget.update("Unable to load stats")

    def action_go_applications(self) -> None:
        from src.screens.applications import ApplicationsScreen

        self.app.push_screen(ApplicationsScreen())

    def action_go_logs(self) -> None:
        from src.screens.logs import LogsScreen

        self.app.push_screen(LogsScreen())

    def action_go_settings(self) -> None:
        from src.screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-applications":
            self.action_go_applications()
        elif event.button.id == "btn-logs":
            self.action_go_logs()
        elif event.button.id == "btn-settings":
            self.action_go_settings()
