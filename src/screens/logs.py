from __future__ import annotations

import asyncio
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
from textual.worker import Worker, WorkerState

from src import db
from src.api.client import ApiClientError
from src.api.logs import get_logs, query_logs, stream_logs
from src.models.schemas import LogQuery, LogRead

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
    "INVALID_API_KEY": (
        "Invalid API key. Create an application key in Applications and try again."
    ),
    "TIMEOUT": "Server is taking too long to respond.",
}

STREAM_STATUS_STYLES = {
    "Disconnected": "dim",
    "Streaming": "green",
    "Reconnecting...": "yellow",
}


class LogsScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "go_back", "Back"),
        ("r", "refresh", "Refresh"),
        ("f", "filter", "Filter"),
        ("/", "search", "Search"),
        ("c", "clear", "Clear"),
        ("t", "toggle_stream", "Stream"),
    ]

    MAX_STREAMED_LOGS = 1000
    MAX_STREAM_RECONNECT_ATTEMPTS = 5

    def __init__(self) -> None:
        super().__init__()
        self._current_filters: LogQuery | None = None
        self._search_text: str | None = None
        self._app_ids: list[str] = []
        self._stream_enabled = False
        self._stream_worker: Worker | None = None
        self._stream_status = "Disconnected"
        self._pending_logs: list[LogRead] = []
        self._displayed_logs: list[LogRead] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Static("Logs", id="logs-title", classes="section-title"),
                Static(self._stream_status, id="stream-status"),
                id="logs-header-row",
            ),
            DataTable(id="logs-table", cursor_type="row"),
            id="logs-container",
        )
        yield Footer()

    async def on_mount(self) -> None:
        table = self.query_one("#logs-table", DataTable)
        table.add_columns("Timestamp", "Level", "App", "Message")
        self._update_stream_status_display()
        self.run_worker(self._load_logs())

    def _update_stream_status_display(self) -> None:
        status_widget = self.query_one("#stream-status", Static)
        style = STREAM_STATUS_STYLES.get(self._stream_status, "dim")
        status_widget.update(f"[{style}]{self._stream_status}[/{style}]")

    def action_toggle_stream(self) -> None:
        if self._stream_enabled:
            self._stop_stream()
        else:
            self._start_stream()

    def _start_stream(self) -> None:
        if self._stream_worker is not None:
            return
        self._stream_enabled = True
        self._stream_status = "Streaming"
        self._update_stream_status_display()
        self._stream_worker = self.run_worker(
            self._stream_logs_worker(), name="stream_logs", exclusive=True
        )
        self.notify("Stream started", severity="information")

    def _stop_stream(self) -> None:
        self._stream_enabled = False
        self._stream_status = "Disconnected"
        self._update_stream_status_display()
        if self._stream_worker is not None:
            self._stream_worker.cancel()
            self._stream_worker = None
        self.notify("Stream stopped", severity="information")

    async def _stream_logs_worker(self) -> None:
        client: OnyxLogClient = self.app.client
        levels = None
        if self._current_filters and self._current_filters.level:
            levels = [self._current_filters.level]

        reconnect_attempts = 0

        while self._stream_enabled:
            try:
                async for log in stream_logs(client, levels=levels, max_retries=0):
                    if not self._stream_enabled:
                        break

                    reconnect_attempts = 0
                    if self._stream_status != "Streaming":
                        self._stream_status = "Streaming"
                        self._update_stream_status_display()

                    self._pending_logs.insert(0, log)
                    if len(self._pending_logs) > self.MAX_STREAMED_LOGS:
                        self._pending_logs.pop()

                    self._displayed_logs.insert(0, log)
                    if len(self._displayed_logs) > self.MAX_STREAMED_LOGS:
                        self._displayed_logs.pop()

                    self._add_streamed_log_to_table()

                if not self._stream_enabled:
                    break

                reconnect_attempts += 1
                if reconnect_attempts > self.MAX_STREAM_RECONNECT_ATTEMPTS:
                    self.notify(
                        "Streaming reconnection limit reached", severity="error"
                    )
                    break

                self._stream_status = "Reconnecting..."
                self._update_stream_status_display()
                await asyncio.sleep(2 ** (reconnect_attempts - 1))
            except ApiClientError as e:
                if not self._stream_enabled:
                    break

                reconnect_attempts += 1
                if reconnect_attempts > self.MAX_STREAM_RECONNECT_ATTEMPTS:
                    self.notify(
                        ERROR_MESSAGES.get(e.error_code, e.message), severity="error"
                    )
                    break

                self._stream_status = "Reconnecting..."
                self._update_stream_status_display()
                self.notify("Stream disconnected, reconnecting...", severity="warning")
                await asyncio.sleep(2 ** (reconnect_attempts - 1))
            except Exception:
                if not self._stream_enabled:
                    break

                reconnect_attempts += 1
                if reconnect_attempts > self.MAX_STREAM_RECONNECT_ATTEMPTS:
                    self.notify("Stream connection lost", severity="error")
                    break

                self._stream_status = "Reconnecting..."
                self._update_stream_status_display()
                await asyncio.sleep(2 ** (reconnect_attempts - 1))

        self._stream_enabled = False
        self._stream_worker = None
        self._stream_status = "Disconnected"
        self._update_stream_status_display()

    def _add_streamed_log_to_table(self) -> None:
        table = self.query_one("#logs-table", DataTable)
        self._populate_table(table, self._displayed_logs)

    async def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name == "stream_logs":
            if event.state == WorkerState.ERROR:
                self._stream_status = "Disconnected"
                self._update_stream_status_display()
                self._stream_enabled = False
                self._stream_worker = None

    async def _load_logs(self) -> None:
        table = self.query_one("#logs-table", DataTable)
        table.loading = True
        try:
            client: OnyxLogClient = self.app.client

            try:
                app_key = await db.get_active_key(
                    server_url=self.app.settings.onyxlog_url,
                    key_type="application",
                )
            except Exception:
                app_key = None
            app_api_key = app_key["key"] if app_key else None

            if self._current_filters:
                result = await query_logs(
                    client,
                    self._current_filters,
                    api_key=app_api_key,
                )
            else:
                result = await get_logs(client, limit=200, api_key=app_api_key)
            self._app_ids = sorted({log.app_id for log in result.items})
            logs_to_display = result.items
            if self._search_text:
                logs_to_display = [
                    log
                    for log in result.items
                    if self._search_text in log.message.lower()
                ]
            self._displayed_logs = list(logs_to_display)
            self._populate_table(table, logs_to_display)
            count = len(logs_to_display)
            self.notify(f"{count} logs loaded", severity="information")
        except ApiClientError as e:
            self.notify(ERROR_MESSAGES.get(e.error_code, e.message), severity="error")
        except Exception:
            self.notify("Unable to load logs", severity="error")
        finally:
            table.loading = False

    def _populate_table(self, table: DataTable, logs: list[LogRead]) -> None:
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
