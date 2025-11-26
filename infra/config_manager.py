from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

import yaml

from .paths import get_config_dir


@dataclass
class AppConfig:
    motion_port: str | None = None
    motion_baudrate: int = 115200
    data_dir: str | None = None
    extra: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    def __init__(self, filename: str = "app_config.yaml") -> None:
        self._config_dir = get_config_dir()
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._path = self._config_dir / filename
        self._config = AppConfig()
        self.load()

    @property
    def config(self) -> AppConfig:
        return self._config

    def load(self) -> None:
        if not self._path.exists():
            self.save()
            return
        with self._path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        self._config = AppConfig(**data)

    def save(self) -> None:
        data = self._config.__dict__
        with self._path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True)
