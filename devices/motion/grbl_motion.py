from __future__ import annotations

import logging
from typing import Tuple

from infra.serial_helper import SerialHelper
from .base_motion import IMotionController, MotionStatus

logger = logging.getLogger(__name__)


class GrblLikeMotionController(IMotionController):
    """基于 Grbl 协议的串口运动控制实现（阶段1基础版）。"""

    def __init__(self) -> None:
        self._serial = SerialHelper()
        self._status = MotionStatus.IDLE
        self._position = (0.0, 0.0, 0.0)

    def connect(self, port: str, baudrate: int) -> None:
        self._serial.open(port=port, baudrate=baudrate)
        logger.info("Motion connected on %s", port)

    def disconnect(self) -> None:
        self._serial.close()
        logger.info("Motion disconnected")

    def home(self) -> None:
        self._serial.write_line("$H")
        logger.info("Home command sent")

    def move_abs(
        self,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
        feed: float = 1000.0,
    ) -> None:
        parts = []
        if x is not None:
            parts.append(f"X{x:.3f}")
        if y is not None:
            parts.append(f"Y{y:.3f}")
        if z is not None:
            parts.append(f"Z{z:.3f}")
        if not parts:
            return
        cmd = "G1 " + " ".join(parts) + f" F{feed:.1f}"
        self._serial.write_line(cmd)
        logger.info("Move abs: %s", cmd)

    def query_position(self) -> Tuple[float, float, float]:
        return self._position

    def get_status(self) -> str:
        return self._status
