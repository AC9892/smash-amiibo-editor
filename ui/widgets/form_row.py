from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel


class FormRow(QWidget):
    def __init__(self, label: str, editor: QWidget, help_text: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        text = QVBoxLayout()
        title = QLabel(label)
        title.setStyleSheet("font-weight: 600")
        text.addWidget(title)
        if help_text:
            hint = QLabel(help_text)
            hint.setObjectName("muted")
            hint.setWordWrap(True)
            text.addWidget(hint)
        layout.addLayout(text, 1)
        editor.setMinimumWidth(220)
        layout.addWidget(editor)
