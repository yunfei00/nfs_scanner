from __future__ import annotations

from pathlib import Path

APP_NAME = "NFSScanner"


def get_base_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def get_config_dir() -> Path:
    return get_base_dir() / "config"


def get_log_dir() -> Path:
    log_dir = get_base_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
