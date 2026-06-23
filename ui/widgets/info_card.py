from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel


class InfoCard(QFrame):
    def __init__(self, title: str, text: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        heading = QLabel(title)
        heading.setStyleSheet("font-size: 16px; font-weight: 600")
        layout.addWidget(heading)
        self.body = QLabel(text)
        self.body.setObjectName("muted")
        self.body.setWordWrap(True)
        layout.addWidget(self.body)
