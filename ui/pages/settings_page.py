from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLineEdit, QPushButton, QCheckBox, QFileDialog, QLabel
from ui.widgets.form_row import FormRow
from ui.widgets.info_card import InfoCard


class SettingsPage(QWidget):
    def __init__(self, window):
        super().__init__(); self.window_ref = window
        layout = QVBoxLayout(self)
        title = QLabel("Settings"); title.setObjectName("title"); layout.addWidget(title)
        card = InfoCard("Application")
        card.layout().removeWidget(card.body); card.body.deleteLater()
        self.theme = QComboBox(); self.theme.addItems(["dark", "light", "system"])
        self.theme.setCurrentText(window.setting("qt_theme", "dark")); self.theme.currentTextChanged.connect(window.set_theme)
        card.layout().addWidget(FormRow("Theme", self.theme))
        self.folder = QLineEdit(window.setting("output_folder", "")); self.folder.setPlaceholderText("Use source file folder")
        self.folder.editingFinished.connect(lambda: window.save_setting("output_folder", self.folder.text()))
        card.layout().addWidget(FormRow("Default output folder", self.folder))
        pick = QPushButton("Choose folder"); pick.clicked.connect(self.choose_folder); card.layout().addWidget(pick)
        self.images_folder = QLineEdit(window.setting("amiibo_images_folder", ""))
        self.images_folder.setPlaceholderText("Local folder containing amiibo PNG files")
        self.images_folder.editingFinished.connect(self.save_images_folder)
        card.layout().addWidget(FormRow("Amiibo Images Folder", self.images_folder,
                                        "Searched recursively for matching PNG files. No network access is used."))
        pick_images = QPushButton("Choose Amiibo Images Folder")
        pick_images.clicked.connect(self.choose_images_folder)
        card.layout().addWidget(pick_images)
        self.prefer_filename = QCheckBox("Prefer BIN filename for image matching")
        self.prefer_filename.setChecked(window.setting("prefer_image_filename", False))
        self.prefer_filename.setToolTip("Override fighter data and match artwork from the opened file's name.")
        self.prefer_filename.toggled.connect(window.set_prefer_image_filename)
        card.layout().addWidget(self.prefer_filename)
        self.recent = QCheckBox("Keep recent files"); self.recent.setChecked(window.setting("recent_enabled", True)); self.recent.toggled.connect(lambda v: window.save_setting("recent_enabled", v)); card.layout().addWidget(self.recent)
        self.advanced = QCheckBox("Advanced mode"); self.advanced.setChecked(window.setting("advanced_mode", False)); self.advanced.toggled.connect(lambda v: window.save_setting("advanced_mode", v)); card.layout().addWidget(self.advanced)
        reset = QPushButton("Reset settings"); reset.clicked.connect(window.reset_settings); card.layout().addWidget(reset)
        layout.addWidget(card); layout.addStretch()

    def choose_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Default output folder", self.folder.text())
        if path: self.folder.setText(path); self.window_ref.save_setting("output_folder", path)

    def choose_images_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Amiibo Images Folder", self.images_folder.text())
        if path:
            self.images_folder.setText(path)
            self.save_images_folder()

    def save_images_folder(self):
        self.window_ref.set_images_folder(self.images_folder.text().strip())
