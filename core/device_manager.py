from __future__ import annotations

from devices.motion.base_motion import IMotionController
from devices.motion.grbl_motion import GrblLikeMotionController


class DeviceManager:
    """统一管理运动设备（阶段1先只做运动平台）。"""

    def __init__(self) -> None:
        self.motion: IMotionController | None = None

    def ensure_motion(self) -> IMotionController:
        if self.motion is None:
            self.motion = GrblLikeMotionController()
        return self.motion
