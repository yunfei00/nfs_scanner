from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple


class MotionStatus:
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    ERROR = "ERROR"


class IMotionController(ABC):
    """运动控制抽象接口。"""

    @abstractmethod
    def connect(self, port: str, baudrate: int) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def home(self) -> None: ...

    @abstractmethod
    def move_abs(
        self,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
        feed: float = 1000.0,
    ) -> None: ...

    @abstractmethod
    def query_position(self) -> Tuple[float, float, float]: ...

    @abstractmethod
    def get_status(self) -> str: ...
