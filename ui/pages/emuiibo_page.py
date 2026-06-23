from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from ui.widgets.info_card import InfoCard


class EmuiiboPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Emuiibo Export"); title.setObjectName("title"); layout.addWidget(title)
        layout.addWidget(InfoCard("Coming soon", "Emuiibo folder export is not implemented yet. This page is isolated so the converter can be added without changing the editor."))
        button = QPushButton("Export Emuiibo folder"); button.setEnabled(False); layout.addWidget(button)
        layout.addStretch()
