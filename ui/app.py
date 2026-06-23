"""Qt application bootstrap."""

import sys

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractSpinBox, QApplication, QComboBox, QSlider

from ui.main_window import MainWindow


class WheelGuard(QObject):
    """Prevent accidental value changes while scrolling editor pages."""

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Wheel and isinstance(watched, (QComboBox, QAbstractSpinBox, QSlider)):
            event.ignore()
            return True
        return super().eventFilter(watched, event)


def run() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Smash Amiibo Editor")
    app.setOrganizationName("Smash Amiibo Editor")
    app.wheel_guard = WheelGuard(app)
    app.installEventFilter(app.wheel_guard)
    window = MainWindow()
    window.show()
    return app.exec()
