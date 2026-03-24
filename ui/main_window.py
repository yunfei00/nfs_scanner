from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QWidget,
    QStatusBar,
    QTextEdit,
    QTabWidget,
)
from PySide6.QtCore import Qt

from infra.config_manager import ConfigManager
from infra.license_manager import LicenseManager
from core.device_manager import DeviceManager
from core.scan_manager import ScanManager
from .controls_panel import ControlsPanel
from .serial_debug_page import SerialDebugPage


class MainWindow(QMainWindow):
    def __init__(
        self,
        config_manager: ConfigManager,
        license_manager: LicenseManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("近场扫描系统 - 阶段0-1")

        self._config_manager = config_manager
        self._license_manager = license_manager

        self._device_manager = DeviceManager()
        self._scan_manager = ScanManager(self._device_manager)

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.resize(1000, 700)

        tabs = QTabWidget(self)

        center = QTextEdit(self)
        center.setReadOnly(True)
        center.setPlainText("阶段0/1：这里将来是热力图视图")
        tabs.addTab(center, "主扫描视图")

        serial_debug = SerialDebugPage(self)
        tabs.addTab(serial_debug, "串口调试页面")

        self.setCentralWidget(tabs)

        controls = ControlsPanel(
            config_manager=self._config_manager,
            device_manager=self._device_manager,
            scan_manager=self._scan_manager,
        )
        left_dock = QDockWidget("控制面板", self)
        left_dock.setWidget(controls)
        left_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, left_dock)

        log_widget = QTextEdit(self)
        log_widget.setReadOnly(True)
        log_dock = QDockWidget("日志", self)
        log_dock.setWidget(log_widget)
        log_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, log_dock)

        self.setStatusBar(QStatusBar(self))
