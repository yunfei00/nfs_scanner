from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout,
    QComboBox,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QDoubleSpinBox,
    QSpinBox,
    QTabWidget,
    QFrame,
)


class SerialDebugPage(QWidget):
    """串口调试页面（独立页签）。"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        header = QFrame(self)
        header.setObjectName("debugHeader")
        header_layout = QHBoxLayout(header)
        title = QLabel("串口连接与运动系统 / 扫描范围设置", header)
        title.setObjectName("debugTitle")
        subtitle = QLabel("独立调试模块", header)
        subtitle.setObjectName("debugSubtitle")
        version = QLabel("v0.1.0", header)
        version.setObjectName("debugVersion")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch(1)
        header_layout.addWidget(version)
        root.addWidget(header)

        protocol = QLabel(
            "协议: 115200 波特率 · 命令: $H(回零) ?(查询) G1X..Z.. · 坐标范围: X[0~200] Y[0~-300] Z[0~10]"
        )
        protocol.setObjectName("protocolHint")
        root.addWidget(protocol)

        content = QHBoxLayout()
        content.setSpacing(10)

        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        left_col.addWidget(self._build_serial_group())
        left_col.addWidget(self._build_system_cmd_group())
        left_col.addWidget(self._build_jog_group())
        content.addLayout(left_col, 1)

        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        right_col.addWidget(self._build_scan_config_group())
        right_col.addWidget(self._build_path_preview_group())
        content.addLayout(right_col, 1)

        root.addLayout(content, 1)
        root.addWidget(self._build_log_group())

        self.setStyleSheet(
            """
            QFrame#debugHeader { background: #194d88; border-radius: 8px; }
            QLabel#debugTitle { color: white; font-size: 22px; font-weight: 700; }
            QLabel#debugSubtitle { color: #9fd2ff; font-size: 14px; padding: 4px 8px; background: rgba(255,255,255,0.15); border-radius: 10px; }
            QLabel#debugVersion { color: #d2e6ff; background: rgba(255,255,255,0.15); border-radius: 10px; padding: 4px 10px; }
            QLabel#protocolHint { color: #365a84; font-size: 13px; padding: 4px 2px; }
            QGroupBox { font-size: 18px; font-weight: 700; border: 1px solid #d9dfe8; border-radius: 8px; margin-top: 10px; }
            QGroupBox::title { left: 12px; padding: 0 4px; }
            QLabel.state-red { color: #d42d2d; font-weight: 700; }
            QLabel.coord { font-size: 30px; font-weight: 700; color: #2a61cf; }
            QTextEdit#terminal { background: #08121f; color: #d4e2ff; font-family: Consolas, monospace; }
            """
        )

    def _build_serial_group(self) -> QGroupBox:
        group = QGroupBox("串口连接", self)
        layout = QGridLayout(group)
        layout.addWidget(QLabel("串口端口"), 0, 0)
        ports = QComboBox(group)
        ports.addItems(["COM3 - USB-SERIAL CH340 (可用)", "COM5 - CP210x (可用)"])
        layout.addWidget(ports, 1, 0)
        layout.addWidget(QPushButton("刷新", group), 1, 1)

        connect_btn = QPushButton("连接串口", group)
        connect_btn.setMinimumHeight(36)
        connect_btn.setStyleSheet("background:#1f9f56;color:white;font-weight:700;")
        layout.addWidget(connect_btn, 2, 0)

        state = QLabel("状态: ● 未连接", group)
        state.setProperty("class", "state-red")
        state.setStyleSheet("color:#d42d2d;font-weight:700;")
        layout.addWidget(state, 2, 1)

        layout.addWidget(QPushButton("读取版本  $I", group), 3, 0, 1, 2)
        return group

    def _build_system_cmd_group(self) -> QGroupBox:
        group = QGroupBox("系统命令", self)
        layout = QVBoxLayout(group)
        row = QHBoxLayout()
        for text, color in [
            ("放回零点  $H", "#f0a436"),
            ("位置查询  ?", "#2a74e3"),
            ("紧急停止", "#de4040"),
        ]:
            btn = QPushButton(text, group)
            btn.setStyleSheet(f"background:{color};color:white;font-weight:700;")
            btn.setMinimumHeight(34)
            row.addWidget(btn)
        layout.addLayout(row)

        cmd_row = QHBoxLayout()
        cmd_row.addWidget(QLineEdit("", group))
        cmd_row.itemAt(0).widget().setPlaceholderText("输入原始命令，如: $I 或 G1X10Y-10Z5F1000")
        cmd_row.addWidget(QPushButton("发送", group))
        layout.addLayout(cmd_row)
        return group

    def _build_jog_group(self) -> QGroupBox:
        group = QGroupBox("运动控制", self)
        layout = QVBoxLayout(group)
        pos = QLabel("X: 0.000      Y: 0.000      Z: 0.000      F: 0")
        pos.setObjectName("coords")
        layout.addWidget(pos)

        step_row = QHBoxLayout()
        step_row.addWidget(QLabel("点动步距"))
        for label in ["0.1", "1.0", "5.0", "10.0"]:
            step_row.addWidget(QPushButton(label, group))
        step_row.addWidget(QLabel("mm"))
        layout.addLayout(step_row)

        grid = QGridLayout()
        controls = [("X+", 0, 0, "#ef8d1f"), ("Y+", 0, 1, "#2f77e5"), ("Z+", 0, 2, "#1f9f56"),
                    ("X-", 1, 0, "#ef8d1f"), ("Y-", 1, 1, "#2f77e5"), ("Z-", 1, 2, "#1f9f56")]
        for text, r, c, color in controls:
            b = QPushButton(text, group)
            b.setStyleSheet(f"background:{color};color:white;font-weight:700;")
            b.setMinimumHeight(42)
            grid.addWidget(b, r, c)
        layout.addLayout(grid)
        return group

    def _build_scan_config_group(self) -> QGroupBox:
        group = QGroupBox("扫描范围设置", self)
        layout = QVBoxLayout(group)

        tabs = QTabWidget(group)
        tabs.addTab(self._build_axis_config_tab(), "配置")
        tabs.addTab(QWidget(), "路径预览")
        layout.addWidget(tabs)
        return group

    def _build_axis_config_tab(self) -> QWidget:
        page = QWidget()
        layout = QGridLayout(page)

        def axis_row(row: int, name: str, end_default: float, step_default: float) -> None:
            layout.addWidget(QLabel(f"{name} 起点"), row, 0)
            s = QDoubleSpinBox(page)
            s.setRange(-9999, 9999)
            layout.addWidget(s, row, 1)

            layout.addWidget(QLabel(f"{name} 终点"), row, 2)
            e = QDoubleSpinBox(page)
            e.setRange(-9999, 9999)
            e.setValue(end_default)
            layout.addWidget(e, row, 3)

            layout.addWidget(QLabel("步长"), row, 4)
            st = QDoubleSpinBox(page)
            st.setRange(-9999, 9999)
            st.setValue(step_default)
            layout.addWidget(st, row, 5)

        axis_row(0, "X", 100.0, 5.0)
        axis_row(1, "Y", -100.0, -5.0)

        layout.addWidget(QLabel("Z 扫描高度"), 2, 0)
        z = QDoubleSpinBox(page)
        z.setValue(5.0)
        z.setRange(0, 10)
        layout.addWidget(z, 2, 1)

        layout.addWidget(QLabel("驻留时间"), 2, 2)
        dwell = QSpinBox(page)
        dwell.setRange(1, 10000)
        dwell.setValue(100)
        layout.addWidget(dwell, 2, 3)
        layout.addWidget(QLabel("ms"), 2, 4)

        layout.addWidget(QLabel("扫描模式"), 3, 0)
        mode = QComboBox(page)
        mode.addItems(["蛇形扫描 (推荐)", "往返扫描"])
        layout.addWidget(mode, 3, 1, 1, 5)

        info = QLabel("路径预览（计算结果）\nX: 0→100 步长 5   |   Y: 0→-100 步长 -5\n预计扫描点数: 441")
        info.setStyleSheet("background:#eaf4ff;border:1px solid #84b7ff;border-radius:6px;padding:8px;")
        layout.addWidget(info, 4, 0, 1, 6)
        return page

    def _build_path_preview_group(self) -> QGroupBox:
        group = QGroupBox("扫描路径预览", self)
        layout = QVBoxLayout(group)
        placeholder = QLabel("路径预览图\n连接设备并设置范围后显示蛇形扫描路径")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setMinimumHeight(180)
        placeholder.setStyleSheet("border:2px dashed #ccd5e2;border-radius:6px;color:#6b7a90;")
        layout.addWidget(placeholder)
        return group

    def _build_log_group(self) -> QGroupBox:
        group = QGroupBox("模块日志 (串口与运动系统)", self)
        layout = QVBoxLayout(group)

        self.log_text = QTextEdit(group)
        self.log_text.setObjectName("terminal")
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(190)
        self.log_text.setPlainText(
            "[15:30:45.123] [INFO] 模块初始化完成 - 串口运动控制面板已就绪\n"
            "[15:30:45.456] [INFO] 坐标范围: X[0~200] Y[0~-300] Z[0~10]\n"
            "[15:30:46.789] [DEBUG] 扫描参数已配置为默认值\n"
            "[15:30:50.000] [WARN] 请先连接串口设备"
        )
        layout.addWidget(self.log_text)

        cmd = QHBoxLayout()
        inp = QLineEdit(group)
        inp.setPlaceholderText("输入命令直接发送（如: ? 或 $I）")
        cmd.addWidget(inp)
        send = QPushButton("发送", group)
        send.setStyleSheet("background:#2a74e3;color:white;font-weight:700;")
        cmd.addWidget(send)
        layout.addLayout(cmd)

        return group
