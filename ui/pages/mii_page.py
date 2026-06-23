from PySide6.QtWidgets import QHBoxLayout, QPushButton
from ui.widgets.section_editor import SectionEditor


class MiiPage(SectionEditor):
    def __init__(self, window):
        super().__init__("Mii data", lambda s: "mii" in str(s).lower())
        controls = QHBoxLayout()
        dump = QPushButton("Dump Mii")
        load = QPushButton("Load Mii")
        dump.clicked.connect(window.dump_mii)
        load.clicked.connect(window.load_mii)
        controls.addWidget(dump); controls.addWidget(load); controls.addStretch()
        self.layout.insertLayout(1, controls)
