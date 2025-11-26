from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Dict

from .paths import get_base_dir
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class LicenseInfo:
    machine_id: str
    license_id: str
    expires_at: str | None = None
    extra: Dict[str, Any] | None = None


class LicenseManager:
    def __init__(self, config_manager: ConfigManager) -> None:
        self._config_manager = config_manager
        self._license_path = (
            get_base_dir().parent / "license" / "license.json"
        )
        self._license: LicenseInfo | None = None

    def get_machine_id(self) -> str:
        return str(uuid.getnode())

    def load_license(self) -> None:
        if not self._license_path.exists():
            logger.warning("License file not found: %s", self._license_path)
            return
        with self._license_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self._license = LicenseInfo(**data)

    def check_license(self) -> bool:
        if self._license is None:
            self.load_license()
        if self._license is None:
            return False
        if self._license.machine_id != self.get_machine_id():
            logger.error("License machine_id mismatch")
            return False
        return True
