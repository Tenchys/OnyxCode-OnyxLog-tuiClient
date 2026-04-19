from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from src.cli import app

runner = CliRunner()


class TestCliRun:
    def test_run_with_debug_enables_logging(self):
        with patch("src.cli.OnyxLogApp") as mock_app_class:
            with patch("src.cli.logging") as mock_logging:
                mock_app_instance = MagicMock()
                mock_app_class.return_value = mock_app_instance

                from src.cli import _run

                _run(url=None, debug=True)

                mock_logging.basicConfig.assert_called_once_with(
                    level=mock_logging.DEBUG,
                    format="%(levelname)s: %(message)s",
                )
                mock_app_instance.run.assert_called_once()

    def test_run_sets_custom_url(self):
        with patch("src.cli.OnyxLogApp") as mock_app_class:
            with patch("src.cli.Settings") as mock_settings_class:
                mock_settings_instance = MagicMock()
                mock_settings_instance.onyxlog_url = "http://test:1234"
                mock_settings_class.return_value = mock_settings_instance

                mock_app_instance = MagicMock()
                mock_app_class.return_value = mock_app_instance

                from src.cli import _run

                _run(url="http://test:1234", debug=False)

                mock_settings_class.assert_called_once_with(
                    onyxlog_url="http://test:1234"
                )
                assert mock_app_instance._settings == mock_settings_instance
                mock_app_instance.run.assert_called_once()


class TestCliMain:
    def test_cli_main_runs_with_defaults(self):
        with patch("src.cli._run") as mock_run:
            result = runner.invoke(app, [])

        assert result.exit_code == 0
        mock_run.assert_called_once_with(url=None, debug=False)

    def test_cli_main_accepts_url_parameter(self):
        with patch("src.cli._run") as mock_run:
            result = runner.invoke(app, ["--url", "http://custom:9000"])

        assert result.exit_code == 0
        mock_run.assert_called_once_with(url="http://custom:9000", debug=False)

    def test_cli_main_accepts_debug_flag(self):
        with patch("src.cli._run") as mock_run:
            result = runner.invoke(app, ["--debug"])

        assert result.exit_code == 0
        mock_run.assert_called_once_with(url=None, debug=True)

    def test_cli_main_shows_version(self):
        with patch("src.cli._run") as mock_run:
            result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "onyxlog-tui 0.1.0" in result.stdout
        mock_run.assert_not_called()
