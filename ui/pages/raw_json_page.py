import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QPlainTextEdit


class RawJsonPage(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window_ref = window
        layout = QVBoxLayout(self)
        title = QLabel("Raw JSON / Advanced")
        title.setObjectName("title")
        layout.addWidget(title)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Load an amiibo to inspect its editable region values as JSON.")
        layout.addWidget(self.editor, 1)
        buttons = QHBoxLayout()
        for text, fn in (("Validate JSON", self.validate), ("Reload from amiibo", self.reload), ("Apply JSON", self.apply)):
            button = QPushButton(text); button.clicked.connect(fn); buttons.addWidget(button)
        buttons.addStretch(); layout.addLayout(buttons)

    def reload(self):
        self.editor.setPlainText(json.dumps(self.window_ref.section_values(), indent=2, ensure_ascii=False))

    def validate(self):
        try:
            json.loads(self.editor.toPlainText())
            self.window_ref.statusBar().showMessage("JSON is valid", 4000)
        except json.JSONDecodeError as exc:
            self.window_ref.show_error("Invalid JSON", f"Line {exc.lineno}, column {exc.colno}: {exc.msg}")

    def apply(self):
        try: values = json.loads(self.editor.toPlainText())
        except json.JSONDecodeError as exc:
            self.window_ref.show_error("Invalid JSON", str(exc)); return
        self.window_ref.apply_section_values(values)
