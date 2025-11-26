from __future__ import annotations

import logging
from dataclasses import dataclass
from threading import Thread, Event
from typing import List

from PySide6.QtCore import QObject, Signal

from .models import ScanConfig
from .device_manager import DeviceManager

logger = logging.getLogger(__name__)


@dataclass
class ScanPoint:
    x: float
    y: float
    z: float


class ScanManager(QObject):
    """扫描流程管理（阶段1先实现路径规划 + 空跑线程）。"""

    progress_changed = Signal(int)
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, device_manager: DeviceManager) -> None:
        super().__init__()
        self._device_manager = device_manager
        self._thread: Thread | None = None
        self._stop_event = Event()

    def generate_points(self, config: ScanConfig) -> List[ScanPoint]:
        xs: List[float] = []
        x = config.x_start
        while x <= config.x_stop + 1e-6:
            xs.append(x)
            x += config.x_step

        ys: List[float] = []
        y = config.y_start
        step = config.y_step
        if step == 0:
            step = -1.0
        if step > 0:
            while y <= config.y_stop + 1e-6:
                ys.append(y)
                y += step
        else:
            while y >= config.y_stop - 1e-6:
                ys.append(y)
                y += step

        points: List[ScanPoint] = []
        for i, y in enumerate(ys):
            row = xs if i % 2 == 0 or not config.snake_mode else list(reversed(xs))
            for x in row:
                points.append(ScanPoint(x=x, y=y, z=config.z_height))
        return points

    def start_scan(self, config: ScanConfig) -> None:
        if self._thread and self._thread.is_alive():
            logger.warning("Scan already running")
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._run_scan, args=(config,), daemon=True)
        self._thread.start()

    def stop_scan(self) -> None:
        self._stop_event.set()

    def _run_scan(self, config: ScanConfig) -> None:
        try:
            motion = self._device_manager.ensure_motion()
            points = self.generate_points(config)
            total = len(points) or 1

            for idx, p in enumerate(points):
                if self._stop_event.is_set():
                    break
                motion.move_abs(x=p.x, y=p.y, z=p.z)
                self.progress_changed.emit(int(idx * 100 / total))

            self.progress_changed.emit(100)
            self.finished.emit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Scan error: %s", exc)
            self.error_occurred.emit(str(exc))
