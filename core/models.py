from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScanConfig:
    x_start: float
    x_stop: float
    x_step: float
    y_start: float
    y_stop: float
    y_step: float
    z_height: float
    snake_mode: bool = True
    dwell_time: float = 0.1
    marker_freq: float | None = None
