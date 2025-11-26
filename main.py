from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication
from infra.logging_config import setup_logging
from infra.config_manager import ConfigManager
from infra.license_manager import LicenseManager
from ui.main_window import MainWindow


def main() -> None:
    setup_logging()
    app = QApplication(sys.argv)

    config_manager = ConfigManager()
    license_manager = LicenseManager(config_manager=config_manager)

    if not license_manager.check_license():
        print("License check failed, running in demo mode.")

    window = MainWindow(
        config_manager=config_manager,
        license_manager=license_manager,
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
