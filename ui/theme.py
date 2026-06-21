"""Fast palette-based themes with one shared structural stylesheet."""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


# This stylesheet is installed once. Theme changes only update QPalette, avoiding
# an expensive stylesheet reparse across the large editor widget tree.
BASE = """
QWidget { background: palette(window); color: palette(window-text); font-size: 14px; }
QMainWindow, QScrollArea, QStackedWidget { background: palette(window); }
QFrame#card { background: palette(alternate-base); border: 1px solid palette(mid); border-radius: 12px; }
QLabel#muted { color: #9ca3af; }
QLabel#title { font-size: 22px; font-weight: 700; }
QPushButton { background: palette(button); border: 1px solid palette(mid); border-radius: 7px; padding: 8px 13px; }
QPushButton:hover { background: palette(midlight); }
QPushButton:checked, QPushButton#primary { background: palette(highlight); border-color: palette(highlight); color: palette(highlighted-text); }
QPushButton:disabled { color: palette(mid); background: palette(alternate-base); }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit {
    background: palette(base); border: 2px solid palette(mid); border-radius: 6px;
    padding: 7px; selection-background-color: palette(highlight);
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QPlainTextEdit:focus { border-color: palette(highlight); }
QComboBox { background: palette(tool-tip-base); border-width: 4px; border-color: palette(dark); padding-right: 34px; }
QComboBox::drop-down { background: transparent; border: none; width: 30px; }
QComboBox::down-arrow { image: url(ui/assets/chevron-down.svg); width: 12px; height: 12px; }
QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 0px; height: 0px; border: none; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 3px 2px; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px 3px; }
QScrollBar::handle { background: palette(mid); border-radius: 4px; min-height: 28px; min-width: 28px; }
QScrollBar::handle:hover { background: palette(dark); }
QScrollBar::add-line, QScrollBar::sub-line { width: 0px; height: 0px; background: transparent; border: none; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
QSlider::groove:horizontal { height: 6px; background: palette(midlight); border-radius: 3px; }
QSlider::sub-page:horizontal { background: palette(highlight); border-radius: 3px; }
QSlider::handle:horizontal { background: palette(base); border: 2px solid palette(highlight); width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }
QToolTip { background: palette(tool-tip-base); color: palette(tool-tip-text); border: 1px solid palette(mid); }
"""

_system_palette: QPalette | None = None


def stylesheet(_name: str = "dark") -> str:
    return BASE


def apply_palette(app: QApplication, name: str) -> None:
    global _system_palette
    if _system_palette is None:
        _system_palette = QPalette(app.palette())
    if name == "system":
        app.setPalette(_system_palette)
        return

    palette = QPalette()
    if name == "light":
        colors = {
            QPalette.ColorRole.Window: "#eef2f7", QPalette.ColorRole.WindowText: "#172033",
            QPalette.ColorRole.Base: "#ffffff", QPalette.ColorRole.AlternateBase: "#ffffff",
            QPalette.ColorRole.Text: "#172033", QPalette.ColorRole.Button: "#e7edf5",
            QPalette.ColorRole.ButtonText: "#172033", QPalette.ColorRole.Mid: "#aab8ca",
            QPalette.ColorRole.Midlight: "#d7e0eb", QPalette.ColorRole.Dark: "#8293aa",
            QPalette.ColorRole.Highlight: "#2563eb", QPalette.ColorRole.HighlightedText: "#ffffff",
            QPalette.ColorRole.ToolTipBase: "#ffffff", QPalette.ColorRole.ToolTipText: "#172033",
        }
    else:
        colors = {
            QPalette.ColorRole.Window: "#202020", QPalette.ColorRole.WindowText: "#e5e7eb",
            QPalette.ColorRole.Base: "#353535", QPalette.ColorRole.AlternateBase: "#282828",
            QPalette.ColorRole.Text: "#e5e7eb", QPalette.ColorRole.Button: "#303030",
            QPalette.ColorRole.ButtonText: "#e5e7eb", QPalette.ColorRole.Mid: "#707070",
            QPalette.ColorRole.Midlight: "#383838", QPalette.ColorRole.Dark: "#555555",
            QPalette.ColorRole.Highlight: "#2563eb", QPalette.ColorRole.HighlightedText: "#ffffff",
            QPalette.ColorRole.ToolTipBase: "#1b1b1b", QPalette.ColorRole.ToolTipText: "#ffffff",
        }
    for role, color in colors.items():
        palette.setColor(role, QColor(color))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#64748b"))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#64748b"))
    app.setPalette(palette)
