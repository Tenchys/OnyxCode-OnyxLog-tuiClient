from __future__ import annotations

from pathlib import Path

import pytest

from src.config import Settings


class TestSettingsDefaults:
    def test_default_url(self):
        settings = Settings()
        assert settings.onyxlog_url == "http://localhost:8000"

    def test_default_db_path(self):
        settings = Settings()
        assert settings.db_path == "~/.onyxlog/keys.db"

    def test_default_config_path(self):
        settings = Settings()
        assert settings.config_path == "~/.onyxlog/config.toml"


class TestSettingsEnvVars:
    def test_env_url_overrides_default(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("ONYXLOG_URL", "http://env-server:9000")
        settings = Settings()
        assert settings.onyxlog_url == "http://env-server:9000"

    def test_env_db_path_overrides_default(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("ONYXLOG_DB_PATH", "/custom/path/keys.db")
        settings = Settings()
        assert settings.db_path == "/custom/path/keys.db"

    def test_env_config_path_overrides_default(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("ONYXLOG_CONFIG_PATH", "/custom/config.toml")
        settings = Settings()
        assert settings.config_path == "/custom/config.toml"


class TestConfigFile:
    def test_load_from_nonexistent_file(self, tmp_path: Path):
        settings = Settings.load_from_file(str(tmp_path / "nonexistent.toml"))
        assert settings.onyxlog_url == "http://localhost:8000"

    def test_load_from_valid_file(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('[server]\nurl = "http://file-server:7000"\n')

        settings = Settings.load_from_file(str(config_file))
        assert settings.onyxlog_url == "http://file-server:7000"

    def test_load_from_corrupt_file(self, tmp_path: Path):
        config_file = tmp_path / "corrupt.toml"
        config_file.write_text("invalid toml content {[[\n")

        settings = Settings.load_from_file(str(config_file))
        assert settings.onyxlog_url == "http://localhost:8000"


class TestSaveToFile:
    def test_save_creates_directory(self, tmp_path: Path):
        config_file = tmp_path / ".onyxlog" / "config.toml"

        settings = Settings(
            onyxlog_url="http://save-server:5000", config_path=str(config_file)
        )
        settings.save_to_file()

        assert config_file.exists()

    def test_save_writes_correct_content(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"

        settings = Settings(
            onyxlog_url="http://save-server:5000", config_path=str(config_file)
        )
        settings.save_to_file()

        content = config_file.read_text()
        assert "http://save-server:5000" in content
        assert "[server]" in content

    def test_save_overwrites_existing(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text("old content")

        settings = Settings(
            onyxlog_url="http://new-server:5000", config_path=str(config_file)
        )
        settings.save_to_file()

        content = config_file.read_text()
        assert "old content" not in content
        assert "http://new-server:5000" in content


class TestPriority:
    def test_cli_over_env(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("ONYXLOG_URL", "http://env-server:9000")

        settings = Settings(onyxlog_url="http://cli-server:8000")
        assert settings.resolved_url == "http://cli-server:8000"

    def test_env_over_file(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('[server]\nurl = "http://file-server:7000"\n')

        monkeypatch.setenv("ONYXLOG_URL", "http://env-server:9000")

        settings = Settings(config_path=str(config_file))
        assert settings.resolved_url == "http://env-server:9000"

    def test_file_over_default(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('[server]\nurl = "http://file-server:7000"\n')

        settings = Settings(config_path=str(config_file))
        assert settings.resolved_url == "http://file-server:7000"

    def test_default_when_nothing_set(self):
        settings = Settings()
        assert settings.resolved_url == "http://localhost:8000"


class TestDirectoryCreation:
    def test_expanduser_path(self):
        settings = Settings()
        expanded = Path(settings.config_path).expanduser()
        assert expanded.is_absolute()

    def test_save_creates_onyxlog_directory(self, tmp_path: Path):
        config_file = tmp_path / ".onyxlog" / "config.toml"

        settings = Settings(
            onyxlog_url="http://server:5000", config_path=str(config_file)
        )
        settings.save_to_file()

        assert config_file.parent.exists()


class TestResolvedUrl:
    def test_resolved_url_property(self):
        settings = Settings(onyxlog_url="http://localhost:8000")
        assert settings.resolved_url == "http://localhost:8000"

    def test_resolved_url_with_env_override(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("ONYXLOG_URL", "http://env-url:3000")
        settings = Settings()
        assert settings.resolved_url == "http://env-url:3000"


class TestSettingsValidation:
    def test_settings_accepts_valid_url(self):
        settings = Settings(onyxlog_url="http://valid:8000")
        assert settings.onyxlog_url == "http://valid:8000"

    def test_settings_accepts_custom_paths(self):
        settings = Settings(
            db_path="/custom/db/path.db", config_path="/custom/config.toml"
        )
        assert settings.db_path == "/custom/db/path.db"
        assert settings.config_path == "/custom/config.toml"
