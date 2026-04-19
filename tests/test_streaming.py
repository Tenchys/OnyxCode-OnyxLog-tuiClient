from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID

import httpx
import pytest
from textual.app import App

from src.api.client import ApiClientError, OnyxLogClient
from src.api.logs import stream_logs
from src.models.schemas import LogRead
from src.screens.logs import LogsScreen


def make_log(message: str, level: str = "INFO") -> dict:
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2026-01-01T00:00:00Z",
        "level": level,
        "app_id": "test-app",
        "message": message,
        "metadata": None,
    }


class FakeStreamResponse:
    def __init__(self, lines: list[str], status_code: int = 200) -> None:
        self._lines = lines
        self.status_code = status_code

    async def aiter_lines(self):
        for line in self._lines:
            yield line


class FakeHttpClient:
    def __init__(self, outcomes: list[FakeStreamResponse | Exception]) -> None:
        self._outcomes = outcomes
        self.calls: list[dict] = []

    @asynccontextmanager
    async def stream(self, method: str, path: str, **kwargs):
        self.calls.append({"method": method, "path": path, **kwargs})
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        yield outcome


def make_client(outcomes: list[FakeStreamResponse | Exception]) -> OnyxLogClient:
    client = MagicMock(spec=OnyxLogClient)
    client.BASE_PATH = "/api/v1"
    client._headers = {"X-API-Key": "test-key"}
    client._client = FakeHttpClient(outcomes)
    return client


class TestStreamLogs:
    @pytest.mark.asyncio
    async def test_stream_logs_yields_log_events(self) -> None:
        client = make_client(
            [
                FakeStreamResponse(
                    [
                        "event: heartbeat",
                        "data: {}",
                        "",
                        "event: log",
                        f"data: {json.dumps(make_log('hello'))}",
                        "",
                    ]
                )
            ]
        )

        stream = stream_logs(client, max_retries=0)
        first_log = await anext(stream)

        assert first_log.message == "hello"
        assert first_log.level == "INFO"

    @pytest.mark.asyncio
    async def test_stream_logs_sends_levels_and_accept_headers(self) -> None:
        client = make_client([FakeStreamResponse([""])])

        with pytest.raises(ApiClientError):
            await anext(stream_logs(client, levels=["ERROR"], max_retries=0))

        assert len(client._client.calls) == 1
        call = client._client.calls[0]
        assert call["params"]["levels"] == "ERROR"
        assert call["headers"]["Accept"] == "text/event-stream"

    @pytest.mark.asyncio
    async def test_stream_logs_reconnects_after_connection_error(self) -> None:
        client = make_client(
            [
                httpx.ConnectError("offline"),
                FakeStreamResponse(
                    [
                        "event: log",
                        f"data: {json.dumps(make_log('after-reconnect'))}",
                        "",
                    ]
                ),
            ]
        )

        log = await anext(stream_logs(client, max_retries=1))

        assert log.message == "after-reconnect"
        assert len(client._client.calls) == 2

    @pytest.mark.asyncio
    async def test_stream_logs_fails_after_max_retries(self) -> None:
        client = make_client(
            [
                httpx.ConnectError("offline-1"),
                httpx.ConnectError("offline-2"),
                httpx.ConnectError("offline-3"),
            ]
        )

        with pytest.raises(ApiClientError) as exc_info:
            await anext(stream_logs(client, max_retries=2))

        assert exc_info.value.error_code == "CONNECTION_ERROR"
        assert len(client._client.calls) == 3


class LogsTestApp(App):
    CSS_PATH = None

    def __init__(self) -> None:
        super().__init__()
        self.client = MagicMock()

    def on_mount(self) -> None:
        self.push_screen(LogsScreen())


def log_read(message: str, level: str = "INFO") -> LogRead:
    return LogRead(
        id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        level=level,
        app_id="test-app",
        message=message,
        metadata=None,
    )


class TestLogsScreenStreaming:
    @pytest.mark.asyncio
    async def test_toggle_stream_calls_start_and_stop(self, monkeypatch) -> None:
        screen = LogsScreen()
        started = False
        stopped = False

        def _start() -> None:
            nonlocal started
            started = True
            screen._stream_enabled = True

        def _stop() -> None:
            nonlocal stopped
            stopped = True
            screen._stream_enabled = False

        monkeypatch.setattr(screen, "_start_stream", _start)
        monkeypatch.setattr(screen, "_stop_stream", _stop)

        screen.action_toggle_stream()
        screen.action_toggle_stream()

        assert started is True
        assert stopped is True

    @pytest.mark.asyncio
    async def test_stream_worker_updates_pending_logs(self, monkeypatch) -> None:
        app = LogsTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            screen = app.screen
            assert isinstance(screen, LogsScreen)

            async def fake_stream_logs(*args, **kwargs):
                yield log_read("first")
                yield log_read("second")
                screen._stream_enabled = False

            async def no_sleep(*args, **kwargs) -> None:
                return None

            monkeypatch.setattr("src.screens.logs.stream_logs", fake_stream_logs)
            monkeypatch.setattr("src.screens.logs.asyncio.sleep", no_sleep)

            screen._stream_enabled = True
            await screen._stream_logs_worker()

            assert len(screen._pending_logs) == 2
            assert screen._pending_logs[0].message == "second"
            assert screen._pending_logs[1].message == "first"
            assert screen._stream_status == "Disconnected"

    @pytest.mark.asyncio
    async def test_stream_worker_reconnects_after_error(self, monkeypatch) -> None:
        app = LogsTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            screen = app.screen
            assert isinstance(screen, LogsScreen)

            calls = 0

            async def fake_stream_logs(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise ApiClientError("CONNECTION_ERROR", 0, "offline")
                yield log_read("reconnected")
                screen._stream_enabled = False

            async def no_sleep(*args, **kwargs) -> None:
                return None

            monkeypatch.setattr("src.screens.logs.stream_logs", fake_stream_logs)
            monkeypatch.setattr("src.screens.logs.asyncio.sleep", no_sleep)

            screen._stream_enabled = True
            await screen._stream_logs_worker()

            assert calls == 2
            assert screen._pending_logs[0].message == "reconnected"
            assert screen._stream_status == "Disconnected"
