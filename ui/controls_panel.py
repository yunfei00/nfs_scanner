from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QDoubleSpinBox,
    QCheckBox,
)

from infra.config_manager import ConfigManager
from core.device_manager import DeviceManager
from core.scan_manager import ScanManager
from core.models import ScanConfig


class ControlsPanel(QWidget):
    """左侧控制面板：串口、运动控制、扫描参数（阶段1）。"""

    def __init__(
        self,
        config_manager: ConfigManager,
        device_manager: DeviceManager,
        scan_manager: ScanManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._config_manager = config_manager
        self._device_manager = device_manager
        self._scan_manager = scan_manager

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        serial_group = QGroupBox("串口 / 运动平台", self)
        serial_layout = QFormLayout(serial_group)
        self.edt_port = QLineEdit()
        self.edt_baud = QLineEdit("115200")
        self.btn_connect_motion = QPushButton("连接")
        self.btn_home = QPushButton("回零")
        serial_layout.addRow("串口号:", self.edt_port)
        serial_layout.addRow("波特率:", self.edt_baud)
        serial_layout.addRow(self.btn_connect_motion)
        serial_layout.addRow(self.btn_home)
        layout.addWidget(serial_group)

        scan_group = QGroupBox("扫描参数", self)
        scan_layout = QFormLayout(scan_group)

        self.spn_x_start = QDoubleSpinBox()
        self.spn_x_stop = QDoubleSpinBox()
        self.spn_x_step = QDoubleSpinBox()
        self.spn_y_start = QDoubleSpinBox()
        self.spn_y_stop = QDoubleSpinBox()
        self.spn_y_step = QDoubleSpinBox()
        self.spn_z_height = QDoubleSpinBox()
        self.spn_dwell = QDoubleSpinBox()
        self.chk_snake = QCheckBox("蛇形扫描")
        self.spn_marker_freq = QDoubleSpinBox()
        self.spn_marker_freq.setDecimals(3)

        for spn in [
            self.spn_x_start,
            self.spn_x_stop,
            self.spn_x_step,
            self.spn_y_start,
            self.spn_y_stop,
            self.spn_y_step,
            self.spn_z_height,
            self.spn_dwell,
            self.spn_marker_freq,
        ]:
            spn.setRange(-1e6, 1e6)

        scan_layout.addRow("X 起点:", self.spn_x_start)
        scan_layout.addRow("X 终点:", self.spn_x_stop)
        scan_layout.addRow("X 步长:", self.spn_x_step)
        scan_layout.addRow("Y 起点:", self.spn_y_start)
        scan_layout.addRow("Y 终点:", self.spn_y_stop)
        scan_layout.addRow("Y 步长:", self.spn_y_step)
        scan_layout.addRow("Z 高度:", self.spn_z_height)
        scan_layout.addRow("驻留时间(s):", self.spn_dwell)
        scan_layout.addRow(self.chk_snake)
        scan_layout.addRow("Marker 频率(Hz):", self.spn_marker_freq)

        layout.addWidget(scan_group)

        btn_layout = QHBoxLayout()
        self.btn_start_scan = QPushButton("开始扫描")
        self.btn_stop_scan = QPushButton("停止")
        btn_layout.addWidget(self.btn_start_scan)
        btn_layout.addWidget(self.btn_stop_scan)
        layout.addLayout(btn_layout)
        layout.addStretch(1)

    def _connect_signals(self) -> None:
        self.btn_connect_motion.clicked.connect(self._on_connect_motion)
        self.btn_home.clicked.connect(self._on_home)
        self.btn_start_scan.clicked.connect(self._on_start_scan)
        self.btn_stop_scan.clicked.connect(self._on_stop_scan)

    def _on_connect_motion(self) -> None:
        port = self.edt_port.text().strip()
        baud = int(self.edt_baud.text() or "115200")
        motion = self._device_manager.ensure_motion()
        motion.connect(port=port, baudrate=baud)

    def _on_home(self) -> None:
        motion = self._device_manager.ensure_motion()
        motion.home()

    def _on_start_scan(self) -> None:
        cfg = ScanConfig(
            x_start=self.spn_x_start.value(),
            x_stop=self.spn_x_stop.value(),
            x_step=self.spn_x_step.value(),
            y_start=self.spn_y_start.value(),
            y_stop=self.spn_y_stop.value(),
            y_step=self.spn_y_step.value(),
            z_height=self.spn_z_height.value(),
            snake_mode=self.chk_snake.isChecked(),
            dwell_time=self.spn_dwell.value(),
            marker_freq=self.spn_marker_freq.value()
            if self.spn_marker_freq.value() != 0
            else None,
        )
        self._scan_manager.start_scan(cfg)

    def _on_stop_scan(self) -> None:
        self._scan_manager.stop_scan()
