from ui.widgets.section_editor import SectionEditor


class SpiritsPage(SectionEditor):
    def __init__(self):
        super().__init__("Spirits", lambda s: "ability" in str(s).lower() or "spirit" in str(s).lower())
