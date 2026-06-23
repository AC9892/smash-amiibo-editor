from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class Sidebar(QWidget):
    pageSelected = Signal(int)

    def __init__(self, pages: list[str], parent=None):
        super().__init__(parent)
        self.setFixedWidth(205)
        layout = QVBoxLayout(self)
        brand = QLabel("SAE")
        brand.setObjectName("title")
        layout.addWidget(brand)
        self.buttons = []
        for index, title in enumerate(pages):
            button = QPushButton(title)
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, i=index: self.select(i))
            layout.addWidget(button)
            self.buttons.append(button)
        layout.addStretch()
        self.select(0)

    def select(self, index: int):
        for i, button in enumerate(self.buttons):
            button.setChecked(i == index)
        self.pageSelected.emit(index)
