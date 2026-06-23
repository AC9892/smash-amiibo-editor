from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from ui.widgets.file_drop_area import FileDropArea
from ui.widgets.info_card import InfoCard
from ui.widgets.amiibo_preview import AmiiboPreview


class DashboardPage(QWidget):
    def __init__(self, window):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Smash Amiibo Editor")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addWidget(QLabel("Version 1.7.0"))
        actions = QHBoxLayout()
        for text, handler in (("Open .bin", window.browse_bin), ("Open .json", window.browse_json),
                              ("Save", window.save), ("Export", window.export_as)):
            button = QPushButton(text)
            button.clicked.connect(handler)
            if text == "Save": window.save_buttons.append(button)
            if text == "Export": window.export_buttons.append(button)
            actions.addWidget(button)
        actions.addStretch()
        layout.addLayout(actions)
        drop = FileDropArea()
        drop.fileDropped.connect(window.open_file)
        layout.addWidget(drop)
        file_actions = QHBoxLayout()
        for text, handler in (("Browse file", window.browse_file), ("Recent files", window.show_recent_files),
                              ("Clear loaded file", window.clear_file)):
            button = QPushButton(text)
            button.clicked.connect(handler)
            file_actions.addWidget(button)
        file_actions.addStretch()
        layout.addLayout(file_actions)
        self.message = QLabel("")
        self.message.setObjectName("muted")
        layout.addWidget(self.message)
        details = QHBoxLayout()
        self.summary = InfoCard("Current amiibo", "No amiibo loaded. Open a BIN or JSON file to begin.")
        details.addWidget(self.summary, 1)
        self.preview = AmiiboPreview()
        details.addWidget(self.preview)
        layout.addLayout(details, 1)
        layout.addStretch()

    def update_file(self, path, amiibo, fighter: str = ""):
        if not amiibo:
            self.summary.body.setText("No amiibo loaded. Open a BIN or JSON file to begin.")
            self.message.clear()
            self.preview.set_image(None)
            return
        fighter_line = f"\nFighter: {fighter}" if fighter else ""
        self.summary.body.setText(f"File: {path.name}\nFormat: {path.suffix.upper()[1:]}{fighter_line}\nPersonality: {amiibo.get_personality()}")
