from ui.widgets.section_editor import SectionEditor


class StatsPage(SectionEditor):
    def __init__(self):
        names = ("stat", "experience", "personality")
        super().__init__("Stats and AI behavior", lambda s: any(n in str(s).lower() for n in names)
                         or not any(x in str(s).lower() for x in ("character", "owner", "amiibo name", "ability", "spirit", "mii", "alternate skin", "journey", "learning")),
                         use_sliders=True)
