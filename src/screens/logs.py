from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
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

from src.api.client import ApiClientError
from src.api.logs import get_logs, query_logs
from src.models.schemas import LogQuery

if TYPE_CHECKING:
    from src.api.client import OnyxLogClient


LEVEL_STYLES = {
    "DEBUG": "dim",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "bold red",
    "CRITICAL": "bold red reverse",
}

ERROR_MESSAGES = {
    "CONNECTION_ERROR": "Cannot connect to server. Check URL and try again.",
    "TIMEOUT": "Server is taking too long to respond.",
}


class LogsScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "go_back", "Back"),
        ("r", "refresh", "Refresh"),
        ("f", "filter", "Filter"),
        ("/", "search", "Search"),
        ("c", "clear", "Clear"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._current_filters: LogQuery | None = None
        self._search_text: str | None = None
        self._app_ids: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Logs", id="logs-title", classes="section-title"),
            DataTable(id="logs-table", cursor_type="row"),
            id="logs-container",
        )
        yield Footer()

    async def on_mount(self) -> None:
        table = self.query_one("#logs-table", DataTable)
        table.add_columns("Timestamp", "Level", "App", "Message")
        self.run_worker(self._load_logs())

    async def _load_logs(self) -> None:
        table = self.query_one("#logs-table", DataTable)
        table.loading = True
        try:
            client: OnyxLogClient = self.app.client
            if self._current_filters:
                result = await query_logs(client, self._current_filters)
            else:
                result = await get_logs(client, limit=200)
            self._app_ids = sorted({log.app_id for log in result.items})
            logs_to_display = result.items
            if self._search_text:
                logs_to_display = [
                    log
                    for log in result.items
                    if self._search_text in log.message.lower()
                ]
            self._populate_table(table, logs_to_display)
            count = len(logs_to_display)
            self.notify(f"{count} logs loaded", severity="information")
        except ApiClientError as e:
            self.notify(ERROR_MESSAGES.get(e.error_code, e.message), severity="error")
        except Exception:
            self.notify("Unable to load logs", severity="error")
        finally:
            table.loading = False

    def _populate_table(self, table: DataTable, logs: list) -> None:
        table.clear()
        for log in logs:
            timestamp_str = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            level_text = self._format_level(log.level)
            table.add_row(timestamp_str, level_text, log.app_id, log.message)

    def _format_level(self, level: str) -> Text:
        style = LEVEL_STYLES.get(level.upper(), "")
        return Text(level, style=style)

    def action_refresh(self) -> None:
        self.run_worker(self._load_logs())

    def action_filter(self) -> None:
        self.app.push_screen(
            FilterModal(self._current_filters, self._app_ids),
            self._handle_filter_applied,
        )

    def action_search(self) -> None:
        self.app.push_screen(SearchModal(), self._handle_search_applied)

    def action_clear(self) -> None:
        self._current_filters = None
        self._search_text = None
        self.run_worker(self._load_logs())
        self.notify("Filters cleared", severity="information")

    async def _handle_filter_applied(self, filters: LogQuery | None) -> None:
        if filters is not None:
            if self._is_empty_query(filters):
                self._current_filters = None
            else:
                self._current_filters = filters
            self.run_worker(self._load_logs())

    async def _handle_search_applied(self, search_text: str | None) -> None:
        if search_text is not None and search_text.strip():
            self._search_text = search_text.strip().lower()
        else:
            self._search_text = None
        self.run_worker(self._load_logs())

    @staticmethod
    def _is_empty_query(query: LogQuery) -> bool:
        return (
            query.level is None
            and query.app_id is None
            and query.start_time is None
            and query.end_time is None
            and query.search is None
            and query.limit == 100
            and query.offset == 0
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()


class FilterModal(ModalScreen[LogQuery | None]):
    def __init__(
        self,
        current_filters: LogQuery | None = None,
        app_ids: list[str] | None = None,
    ) -> None:
        super().__init__()
        self._current_filters = current_filters or LogQuery()
        self._app_ids = app_ids or []

    def compose(self) -> ComposeResult:
        level_options = [
            ("DEBUG", "DEBUG"),
            ("INFO", "INFO"),
            ("WARNING", "WARNING"),
            ("ERROR", "ERROR"),
            ("CRITICAL", "CRITICAL"),
        ]
        app_options = [(app_id, app_id) for app_id in self._app_ids]
        yield Container(
            Static("Filter Logs", id="filter-title"),
            Label("Level", id="level-label"),
            Select(level_options, id="level-select"),
            Label("App ID", id="appid-label"),
            Select(app_options, prompt="All applications", id="appid-select"),
            Label("Start Time (YYYY-MM-DD HH:MM:SS)", id="start-label"),
            Input(placeholder="2026-04-01 00:00:00", id="start-input"),
            Label("End Time (YYYY-MM-DD HH:MM:SS)", id="end-label"),
            Input(placeholder="2026-04-18 23:59:59", id="end-input"),
            Horizontal(
                Button("Apply", variant="primary", id="apply-btn"),
                Button("Clear", variant="default", id="clear-btn"),
                Button("Cancel", variant="default", id="cancel-btn"),
                classes="button-row",
            ),
            id="filter-container",
            classes="modal-container",
        )

    def on_mount(self) -> None:
        if self._current_filters.level:
            self.query_one("#level-select", Select).value = self._current_filters.level
        if self._current_filters.app_id:
            self.query_one("#appid-select", Select).value = self._current_filters.app_id
        if self._current_filters.start_time:
            self.query_one(
                "#start-input", Input
            ).value = self._current_filters.start_time.strftime("%Y-%m-%d %H:%M:%S")
        if self._current_filters.end_time:
            self.query_one(
                "#end-input", Input
            ).value = self._current_filters.end_time.strftime("%Y-%m-%d %H:%M:%S")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "clear-btn":
            self.dismiss(LogQuery())
        elif event.button.id == "apply-btn":
            self._handle_apply()

    def _handle_apply(self) -> None:
        level_select = self.query_one("#level-select", Select)
        appid_select = self.query_one("#appid-select", Select)
        start_input = self.query_one("#start-input", Input)
        end_input = self.query_one("#end-input", Input)

        filters = LogQuery()

        if level_select.value and level_select.value != Select.BLANK:
            filters.level = str(level_select.value)

        if appid_select.value and appid_select.value != Select.BLANK:
            filters.app_id = str(appid_select.value)

        start_text = start_input.value.strip()
        if start_text:
            try:
                filters.start_time = datetime.strptime(start_text, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.notify(
                    "Invalid start time format. Use YYYY-MM-DD HH:MM:SS",
                    severity="error",
                )
                return

        end_text = end_input.value.strip()
        if end_text:
            try:
                filters.end_time = datetime.strptime(end_text, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.notify(
                    "Invalid end time format. Use YYYY-MM-DD HH:MM:SS", severity="error"
                )
                return

        self.dismiss(filters)


class SearchModal(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Search Logs", id="search-title"),
            Input(placeholder="Search in log messages...", id="search-input"),
            Horizontal(
                Button("Search", variant="primary", id="search-btn"),
                Button("Cancel", variant="default", id="cancel-btn"),
                classes="button-row",
            ),
            id="search-container",
            classes="modal-container",
        )

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self._handle_search()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "search-btn":
            self._handle_search()

    def _handle_search(self) -> None:
        search_input = self.query_one("#search-input", Input)
        search_text = search_input.value.strip()
        self.dismiss(search_text if search_text else None)
