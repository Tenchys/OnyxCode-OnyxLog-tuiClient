from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.ONYXLOG_URL = "http://localhost:8000"
    settings.ONYXLOG_DB_PATH = str(Path.home() / ".onyxlog" / "keys.db")
    return settings
