from ui.widgets.section_editor import SectionEditor
from ui.widgets.amiibo_preview import AmiiboPreview


class FighterPage(SectionEditor):
    def __init__(self):
        names = ("character", "owner", "amiibo name", "alternate skin", "journey", "learning")
        super().__init__("Fighter and owner", lambda s: any(n in str(s).lower() for n in names))
        self.preview = AmiiboPreview()
        self.preview.setMaximumHeight(340)
        self.layout.insertWidget(0, self.preview)
