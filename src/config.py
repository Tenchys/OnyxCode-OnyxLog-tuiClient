from __future__ import annotations

import os
from pathlib import Path

import tomli
import tomli_w
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    onyxlog_url: str = "http://localhost:8000"
    db_path: str = "~/.onyxlog/keys.db"
    config_path: str = "~/.onyxlog/config.toml"

    model_config = SettingsConfigDict(env_prefix="ONYXLOG_", extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _apply_env_vars(cls, values: dict) -> dict:
        if not isinstance(values, dict):
            return values

        if "onyxlog_url" not in values:
            env_url = os.environ.get("ONYXLOG_URL")
            if env_url:
                values["onyxlog_url"] = env_url

        return values

    @model_validator(mode="after")
    def _apply_file_fallback(self) -> Settings:
        if os.environ.get("ONYXLOG_URL"):
            return self

        config_path = Path(self.config_path).expanduser()
        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    data = tomli.load(f)
                server = data.get("server", {})
                if "url" in server:
                    self.onyxlog_url = server["url"]
            except (OSError, tomli.TOMLDecodeError):
                pass

        return self

    def save_to_file(self) -> None:
        expanded = Path(self.config_path).expanduser()
        expanded.parent.mkdir(parents=True, exist_ok=True)

        data = {"server": {"url": self.onyxlog_url}}

        with open(expanded, "wb") as f:
            tomli_w.dump(data, f)

    @classmethod
    def load_from_file(cls, config_path: str | None = None) -> Settings:
        if config_path is None:
            config_path = "~/.onyxlog/config.toml"

        expanded = Path(config_path).expanduser()

        if not expanded.exists():
            return cls()

        try:
            with open(expanded, "rb") as f:
                data = tomli.load(f)
        except (OSError, tomli.TOMLDecodeError):
            return cls()

        server = data.get("server", {})
        url = server.get("url", "http://localhost:8000")

        return cls(onyxlog_url=url)

    @property
    def resolved_url(self) -> str:
        return self.onyxlog_url
