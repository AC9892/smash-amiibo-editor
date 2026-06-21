from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class AmiiboPreview(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumWidth(250)
        layout = QVBoxLayout(self)
        title = QLabel("Amiibo Preview")
        title.setStyleSheet("font-size: 16px; font-weight: 600")
        layout.addWidget(title)
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setMinimumSize(210, 230)
        layout.addWidget(self.image, 1)
        self.caption = QLabel("Image Not Found")
        self.caption.setObjectName("muted")
        self.caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.caption)
        self._source = self._placeholder()
        self._render()

    def set_image(self, path: Path | None) -> None:
        pixmap = QPixmap(str(path)) if path else QPixmap()
        self.set_image_data(pixmap, path.stem if path else "Image Not Found", path)

    def set_image_data(self, pixmap: QPixmap, caption: str, path: Path | None) -> None:
        if pixmap.isNull():
            self._source = self._placeholder()
            self.caption.setText("Image Not Found")
            self.caption.setToolTip("")
        else:
            self._source = pixmap
            self.caption.setText(caption)
            self.caption.setToolTip(str(path) if path else "")
        self._render()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._render()

    def _render(self):
        if self._source.isNull() or self.image.width() < 1 or self.image.height() < 1:
            return
        self.image.setPixmap(self._source.scaled(self.image.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation))

    @staticmethod
    def _placeholder() -> QPixmap:
        pixmap = QPixmap(210, 230)
        pixmap.fill(QColor("#242424"))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#707070"), 4))
        painter.drawRoundedRect(28, 22, 154, 186, 16, 16)
        painter.drawEllipse(75, 50, 60, 60)
        painter.drawLine(55, 178, 98, 132)
        painter.drawLine(98, 132, 155, 178)
        painter.end()
        return pixmap
