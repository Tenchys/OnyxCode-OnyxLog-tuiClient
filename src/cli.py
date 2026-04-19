from __future__ import annotations

import logging
from typing import Annotated

import typer

from src.app import OnyxLogApp
from src.config import Settings

__version__ = "0.1.0"

app = typer.Typer(
    name="onyxlog-tui",
    help="Terminal UI client for OnyxLog log management system.",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"onyxlog-tui {__version__}")
        raise typer.Exit(0)


def _run(url: str | None, debug: bool) -> None:
    if debug:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    settings = Settings(onyxlog_url=url) if url is not None else Settings()

    app_instance = OnyxLogApp()
    app_instance._settings = settings
    app_instance.run()


@app.callback(invoke_without_command=True)
def main(
    url: Annotated[
        str | None,
        typer.Option("--url", help="OnyxLog server URL (overrides config and env)."),
    ] = None,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable verbose debug logging."),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            is_eager=True,
            callback=_version_callback,
            help="Show version and exit.",
        ),
    ] = False,
) -> None:
    del version
    _run(url=url, debug=debug)


if __name__ == "__main__":
    app()
