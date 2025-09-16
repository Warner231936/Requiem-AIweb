from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "settings.json"


class Settings:
    """Lightweight accessor for the shared configuration file."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    def __getattr__(self, item: str) -> Any:
        value = self._data.get(item)
        if isinstance(value, dict):
            return Settings(value)
        return value

    def get(self, *keys: str, default: Any | None = None) -> Any:
        current: Any = self._data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file not found at {CONFIG_PATH}. Expected a single settings file."
        )
    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        data = json.load(config_file)
    return Settings(data)


settings = get_settings()
