from pathlib import Path
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel


class FileDropArea(QFrame):
    fileDropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setAcceptDrops(True)
        self.setMinimumHeight(190)
        layout = QVBoxLayout(self)
        label = QLabel("Drop an amiibo .bin or .json file here")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 17px; font-weight: 600")
        layout.addWidget(label)

    def dragEnterEvent(self, event):
        urls = event.mimeData().urls()
        if urls and Path(urls[0].toLocalFile()).suffix.lower() in {".bin", ".json"}:
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.fileDropped.emit(event.mimeData().urls()[0].toLocalFile())
        event.acceptProposedAction()
