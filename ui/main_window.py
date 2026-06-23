"""Main window and the thin bridge between Qt and the existing amiibo backend."""

import json
import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
                               QLabel, QLineEdit, QMainWindow, QMessageBox, QScrollArea,
                               QStackedWidget, QVBoxLayout, QWidget)

from utils import region_parse as parse
from utils.config import Config
from utils.virtual_amiibo_file import (AmiiboHMACDataError, AmiiboHMACTagError,
                                       InvalidAmiiboDump, InvalidMiiSizeError,
                                       JSONVirtualAmiiboFile, VirtualAmiiboFile)
from ui import theme
from ui.amiibo_images import AmiiboImageManager
from ui.pages.dashboard_page import DashboardPage
from ui.pages.emuiibo_page import EmuiiboPage
from ui.pages.fighter_page import FighterPage
from ui.pages.mii_page import MiiPage
from ui.pages.raw_json_page import RawJsonPage
from ui.pages.settings_page import SettingsPage
from ui.pages.spirits_page import SpiritsPage
from ui.pages.stats_page import StatsPage
from ui.widgets.sidebar import Sidebar


class MainWindow(QMainWindow):
    VERSION = "1.7.0"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smash Amiibo Editor")
        self.resize(1200, 780)
        self.setMinimumSize(900, 620)
        if Path("SAE.ico").exists(): self.setWindowIcon(QIcon("SAE.ico"))
        self.config = Config()
        self.amiibo = None
        self.current_path: Path | None = None
        self.is_json = False
        self.sections: list[object] = []
        self.save_buttons: list = []
        self.export_buttons: list = []
        self.editor_pages = []
        self.image_manager = AmiiboImageManager(self)
        self.image_manager.set_folder(self.setting("amiibo_images_folder", ""))
        self._original_fighter = ""
        self._load_sections()
        self._build_ui()
        self._build_menu()
        self.set_theme(self.setting("qt_theme", "dark"), persist=False)
        self._update_actions()
        self._startup_messages()

    def _build_ui(self):
        root = QWidget(); outer = QVBoxLayout(root); outer.setContentsMargins(0, 0, 0, 0)
        header = QWidget(); header_layout = QHBoxLayout(header)
        title = QLabel("Smash Amiibo Editor"); title.setStyleSheet("font-size: 18px; font-weight: 700")
        self.file_label = QLabel("No amiibo loaded"); self.file_label.setObjectName("muted")
        from PySide6.QtWidgets import QPushButton
        self.header_save = QPushButton("Save"); self.header_save.setObjectName("primary"); self.header_save.clicked.connect(self.save)
        self.header_export = QPushButton("Export"); self.header_export.clicked.connect(self.export_as)
        self.save_buttons.append(self.header_save); self.export_buttons.append(self.header_export)
        header_layout.addWidget(title); header_layout.addWidget(self.file_label, 1); header_layout.addWidget(self.header_save); header_layout.addWidget(self.header_export)
        outer.addWidget(header)
        body = QHBoxLayout(); names = ["Dashboard", "Fighter", "Stats", "Spirits", "Mii", "Raw JSON", "Emuiibo", "Settings"]
        self.sidebar = Sidebar(names); body.addWidget(self.sidebar)
        self.stack = QStackedWidget(); body.addWidget(self.stack, 1)
        self.dashboard = DashboardPage(self)
        self.fighter = FighterPage(); self.stats = StatsPage(); self.spirits = SpiritsPage(); self.mii = MiiPage(self)
        self.image_manager.bind(self.dashboard.preview, "file")
        self.image_manager.bind(self.fighter.preview, "fighter")
        self.editor_pages = [self.fighter, self.stats, self.spirits, self.mii]
        for page in self.editor_pages:
            page.set_sections(self.sections); page.changed.connect(self._editor_changed)
        self.raw = RawJsonPage(self); self.emuiibo = EmuiiboPage(); self.settings = SettingsPage(self)
        pages = [self.dashboard, self.fighter, self.stats, self.spirits, self.mii, self.raw, self.emuiibo, self.settings]
        for page in pages:
            if page in self.editor_pages:
                scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QScrollArea.Shape.NoFrame); scroll.setWidget(page); self.stack.addWidget(scroll)
            else: self.stack.addWidget(page)
        self.sidebar.pageSelected.connect(self.stack.setCurrentIndex)
        outer.addLayout(body, 1); self.setCentralWidget(root)
        self.statusBar().showMessage("Ready")

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        for text, shortcut, fn in (("Open…", "Ctrl+O", self.browse_file), ("Save", "Ctrl+S", self.save), ("Save As / Export…", "Ctrl+Shift+S", self.export_as)):
            action = QAction(text, self); action.setShortcut(shortcut); action.triggered.connect(fn); file_menu.addAction(action)
            if text == "Save": self.save_action = action
            if text.startswith("Save As"): self.export_action = action
        file_menu.addSeparator(); file_menu.addAction("Exit", self.close)
        tools = self.menuBar().addMenu("&Tools")
        tools.addAction("Copy editable values", self.copy_values)
        tools.addAction("View hex data", self.view_hex)
        tools.addAction("Randomize serial number", self.randomize_serial)
        tools.addAction("Metadata transplant…", self.metadata_transplant)
        template_menu = self.menuBar().addMenu("&Templates")
        template_menu.addAction("Load template…", self.load_template)
        template_menu.addAction("Create template from current values…", self.create_template)
        template_menu.addAction("Update existing template…", self.update_template)
        tools.addAction("Select encryption key(s)…", self.select_keys)
        tools.addAction("Select regions file…", self.select_regions)
        tools.addSeparator(); tools.addAction("Dump Mii…", self.dump_mii); tools.addAction("Load Mii…", self.load_mii)
        help_menu = self.menuBar().addMenu("&Help"); help_menu.addAction("About", lambda: QMessageBox.about(self, "About", f"Smash Amiibo Editor {self.VERSION}\nPySide6 interface"))

    def _load_sections(self):
        path = self.config.get_region_path()
        if not path or not Path(path).is_file(): return
        if self.config.get_region_type() == "json": self.sections, _ = parse.load_from_json(path)
        else: self.sections = parse.load_from_txt(path)

    def _startup_messages(self):
        if not self.sections: self.statusBar().showMessage("No regions file configured. Select one from Tools.")
        elif self.config.read_keys() is None: self.statusBar().showMessage("Encryption keys are not configured. Select them from Tools before opening a file.")

    def browse_file(self): self._browse("Amiibo files (*.bin *.json)")
    def browse_bin(self): self._browse("Amiibo dumps (*.bin)")
    def browse_json(self): self._browse("Amiibo JSON (*.json)")

    def _browse(self, file_filter):
        path, _ = QFileDialog.getOpenFileName(self, "Open amiibo", "", file_filter)
        if path: self.open_file(path)

    def open_file(self, path: str):
        path_obj = Path(path)
        if path_obj.suffix.lower() not in {".bin", ".json"}:
            self.show_error("Unsupported file", "Choose an amiibo .bin or .json file."); return
        keys = self.config.read_keys()
        if keys is None:
            self.show_error("Missing encryption keys", "Select key_retail.bin or the two amiibo key files from Tools > Select encryption key(s).")
            return
        try:
            amiibo = JSONVirtualAmiiboFile(str(path_obj), keys) if path_obj.suffix.lower() == ".json" else VirtualAmiiboFile(str(path_obj), keys)
            if path_obj.suffix.lower() == ".bin" and not amiibo.is_initialized():
                result = QMessageBox.question(self, "Uninitialized amiibo", "This amiibo has no owner data. Initialize it now?")
                if result == QMessageBox.StandardButton.Yes and not self._initialize(amiibo): return
            self.amiibo, self.current_path, self.is_json = amiibo, path_obj, path_obj.suffix.lower() == ".json"
            for page in self.editor_pages: page.load(amiibo)
            self._original_fighter = self._current_fighter()
            self.raw.reload(); self.dashboard.update_file(path_obj, amiibo, self._current_fighter())
            self._update_amiibo_preview()
            self.file_label.setText(path_obj.name); self.dashboard.message.setText(f"Loaded {path_obj.name}")
            self._remember(path_obj); self._update_actions(); self.statusBar().showMessage(f"Loaded {path_obj}", 6000)
        except (InvalidAmiiboDump, AmiiboHMACTagError, AmiiboHMACDataError) as exc:
            self.show_error("Invalid amiibo dump", "The dump is invalid or failed HMAC verification. Check the file and encryption keys.", exc)
        except (json.JSONDecodeError, KeyError, IndexError, ValueError, UnicodeError) as exc:
            self.show_error("Invalid amiibo JSON", "The JSON is malformed or missing required Ryujinx amiibo data.", exc)
        except (FileNotFoundError, PermissionError, OSError) as exc:
            self.show_error("Could not open file", str(exc))

    def _initialize(self, amiibo) -> bool:
        dialog = QDialog(self); dialog.setWindowTitle("Initialize amiibo"); layout = QVBoxLayout(dialog)
        name = QLineEdit(); name.setMaxLength(10); name.setPlaceholderText("Nickname")
        mii = QLineEdit(); mii.setPlaceholderText("96-byte Mii dump path")
        layout.addWidget(QLabel("Nickname")); layout.addWidget(name); layout.addWidget(QLabel("Mii dump")); layout.addWidget(mii)
        choose = QAction(dialog); mii.addAction(choose, QLineEdit.ActionPosition.TrailingPosition); choose.setText("…")
        choose.triggered.connect(lambda: mii.setText(QFileDialog.getOpenFileName(dialog, "Select Mii", "", "BIN files (*.bin)")[0]))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted: return False
        try: amiibo.initialize_amiibo(mii.text(), name.text() or "AMIIBO"); return True
        except InvalidMiiSizeError: self.show_error("Invalid Mii size", "A Mii dump must be exactly 96 bytes."); return False
        except OSError as exc: self.show_error("Could not load Mii", str(exc)); return False

    def save(self):
        if not self.amiibo or not self.current_path: return
        try:
            self._prepare_fighter_name_for_export()
            self.amiibo.save_bin(str(self.current_path)); self.statusBar().showMessage(f"Saved {self.current_path.name}", 5000)
        except OSError as exc: self.show_error("Save failed", str(exc))

    def export_as(self):
        if not self.amiibo: return
        extension = ".json" if self.is_json else ".bin"; folder = self.setting("output_folder", "")
        suggested = str(Path(folder) / self.current_path.name) if folder else str(self.current_path)
        path, _ = QFileDialog.getSaveFileName(self, "Export amiibo", suggested, f"{extension[1:].upper()} files (*{extension})")
        if path:
            try:
                self._prepare_fighter_name_for_export()
                self.amiibo.save_bin(path); self.statusBar().showMessage(f"Exported {Path(path).name}", 5000)
            except OSError as exc: self.show_error("Export failed", str(exc))

    def clear_file(self):
        self.amiibo = None; self.current_path = None
        self._original_fighter = ""
        self.image_manager.clear()
        for page in self.editor_pages: page.load(None)
        self.raw.editor.clear(); self.dashboard.update_file(None, None); self.file_label.setText("No amiibo loaded"); self._update_actions()

    def _update_actions(self):
        enabled = self.amiibo is not None
        for widget in self.save_buttons + self.export_buttons: widget.setEnabled(enabled)
        if hasattr(self, "save_action"): self.save_action.setEnabled(enabled); self.export_action.setEnabled(enabled)

    def _editor_changed(self):
        if self.amiibo:
            self.statusBar().showMessage("Unsaved changes", 3000)
            self.dashboard.update_file(self.current_path, self.amiibo, self._current_fighter())
            self._update_amiibo_preview()

    def _update_amiibo_preview(self):
        if not self.amiibo:
            self.image_manager.clear()
            return
        values = self.section_values()
        lowered = {key.casefold(): str(value) for key, value in values.items()}
        def first_value(*needles):
            return next((value for key, value in lowered.items() if any(needle in key for needle in needles)), "")
        name = first_value("amiibo name", "nickname")
        character = first_value("character", "fighter name")
        series = first_value("game series", "series")
        filename = self.current_path.stem if self.current_path else ""
        prefer_filename = self.setting("prefer_image_filename", False)
        file_series = self.current_path.parent.name if self.current_path else ""
        self.image_manager.select(name=name, series=file_series, filename=filename,
                                  prefer_filename=True, channel="file")

        # The Fighter preview follows the editable Smash fighter assignment.
        if prefer_filename and self.current_path:
            series = self.current_path.parent.name
        elif character and not series:
            series = "Super Smash Bros Amiibo"
        elif not series and self.current_path:
            series = self.current_path.parent.name
        self.image_manager.select(character, name, series, filename, prefer_filename, channel="fighter")

    def _current_fighter(self) -> str:
        for page in self.editor_pages:
            for section, _widget in page.bindings:
                if str(section).casefold() == "character" and self.amiibo:
                    return str(section.get_value_from_bin(self.amiibo))
        return ""

    def _prepare_fighter_name_for_export(self) -> None:
        """Use the new fighter's default name only when its assignment changed."""
        current = self._current_fighter()
        if not current or not self._original_fighter or current == self._original_fighter:
            return
        for section in self.sections:
            if str(section).casefold() == "amiibo name" and hasattr(section, "set_value_in_bin"):
                maximum = getattr(section, "characters", len(current))
                section.set_value_in_bin(self.amiibo, current[:maximum])
                break
        for page in self.editor_pages:
            page.load(self.amiibo)
        self.dashboard.update_file(self.current_path, self.amiibo, self._current_fighter())

    def set_images_folder(self, folder: str):
        self.save_setting("amiibo_images_folder", folder)
        self.image_manager.set_folder(folder)
        self._update_amiibo_preview()

    def set_prefer_image_filename(self, enabled: bool):
        self.save_setting("prefer_image_filename", enabled)
        self._update_amiibo_preview()

    def section_values(self):
        output = {}
        for page in self.editor_pages: output.update(page.values())
        return output

    def apply_section_values(self, values):
        if not self.amiibo: self.show_error("No amiibo loaded", "Open an amiibo before applying JSON."); return
        if not isinstance(values, dict): self.show_error("Invalid JSON", "The top-level JSON value must be an object."); return
        if QMessageBox.warning(self, "Apply raw edits", "Apply these values to the current amiibo? Invalid values may corrupt the dump.", QMessageBox.StandardButton.Apply | QMessageBox.StandardButton.Cancel) != QMessageBox.StandardButton.Apply: return
        bindings = {str(s): (s, w) for page in self.editor_pages for s, w in page.bindings}
        try:
            for name, value in values.items():
                if name in bindings: bindings[name][0].set_value_in_bin(self.amiibo, value)
            for page in self.editor_pages: page.load(self.amiibo)
            self.raw.reload()
            self.dashboard.update_file(self.current_path, self.amiibo, self._current_fighter())
            self._update_amiibo_preview()
            self.statusBar().showMessage("Raw JSON applied; changes are not saved yet", 5000)
        except (ValueError, TypeError, OverflowError, KeyError) as exc: self.show_error("Could not apply JSON", str(exc))

    def copy_values(self):
        if not self.amiibo: self.show_error("No amiibo loaded", "Open an amiibo first."); return
        QApplication.clipboard().setText(json.dumps(self.section_values(), indent=2, ensure_ascii=False))
        self.statusBar().showMessage("Editable values copied to clipboard", 4000)

    def view_hex(self):
        if not self.amiibo: self.show_error("No amiibo loaded", "Open an amiibo first."); return
        data = bytes(self.amiibo.get_data())
        lines = [f"{offset:04X}  " + " ".join(f"{byte:02X}" for byte in data[offset:offset + 16]) for offset in range(0, len(data), 16)]
        dialog = QDialog(self); dialog.setWindowTitle("Hex data"); dialog.resize(760, 620); layout = QVBoxLayout(dialog)
        from PySide6.QtWidgets import QPlainTextEdit
        editor = QPlainTextEdit("\n".join(lines)); editor.setReadOnly(True); editor.setStyleSheet("font-family: Consolas, monospace"); layout.addWidget(editor)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons); dialog.exec()

    def randomize_serial(self):
        if not self.amiibo: self.show_error("No amiibo loaded", "Open an amiibo first."); return
        if QMessageBox.question(self, "Randomize serial", "Randomize the current amiibo serial number? The change is not saved automatically.") == QMessageBox.StandardButton.Yes:
            self.amiibo.randomize_sn(); self.statusBar().showMessage("Serial number randomized; changes are not saved yet", 5000)

    def metadata_transplant(self):
        if not self.amiibo: self.show_error("No recipient loaded", "Open the recipient amiibo first."); return
        path, _ = QFileDialog.getOpenFileName(self, "Select donor amiibo", "", "Amiibo dumps (*.bin)")
        if not path: return
        try:
            donor = VirtualAmiiboFile(path, self.config.read_keys()); self.amiibo.recieve_metadata_transplant(donor)
            for page in self.editor_pages: page.load(self.amiibo)
            self.statusBar().showMessage("Metadata transplanted; changes are not saved yet", 5000)
        except (InvalidAmiiboDump, AmiiboHMACTagError, AmiiboHMACDataError) as exc: self.show_error("Metadata transplant failed", "Both donor and recipient must be valid, initialized BIN dumps.", exc)
        except OSError as exc: self.show_error("Metadata transplant failed", str(exc))

    def _template_files(self):
        folder = Path("templates"); folder.mkdir(exist_ok=True)
        return sorted(folder.glob("*.json"))

    def _choose_template(self):
        files = self._template_files()
        if not files: QMessageBox.information(self, "Templates", "No templates are available."); return None
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getItem(self, "Templates", "Template:", [p.stem for p in files], 0, False)
        return Path("templates") / f"{name}.json" if ok else None

    def load_template(self):
        if not self.amiibo: self.show_error("No amiibo loaded", "Open an amiibo before loading a template."); return
        path = self._choose_template()
        if not path: return
        try:
            values = json.loads(path.read_text(encoding="utf-8")); by_signature = {s.get_signature(): s for s in self.sections if hasattr(s, "set_value_in_bin")}
            for signature, value in values.items():
                section = by_signature.get(signature)
                if section:
                    if isinstance(section, parse.ByteWise): value = int(value)
                    elif isinstance(section, parse.percentage): value = float(value)
                    section.set_value_in_bin(self.amiibo, value)
            for page in self.editor_pages: page.load(self.amiibo)
            self.raw.reload()
            self.dashboard.update_file(self.current_path, self.amiibo, self._current_fighter())
            self._update_amiibo_preview()
            self.statusBar().showMessage(f"Loaded template {path.stem}; changes are not saved yet", 5000)
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc: self.show_error("Template load failed", str(exc))

    def create_template(self):
        if not self.amiibo: self.show_error("No amiibo loaded", "Open an amiibo first."); return
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Create template", "Template name:")
        if ok and name.strip(): self._write_template(Path("templates") / f"{Path(name.strip()).stem}.json")

    def update_template(self):
        if not self.amiibo: self.show_error("No amiibo loaded", "Open an amiibo first."); return
        path = self._choose_template()
        if path and QMessageBox.question(self, "Update template", f"Replace {path.name} with all current editable values?") == QMessageBox.StandardButton.Yes: self._write_template(path)

    def _write_template(self, path):
        values = {s.get_signature(): s.get_value_from_bin(self.amiibo) for s in self.sections if hasattr(s, "get_value_from_bin") and s.get_signature()}
        try: path.parent.mkdir(exist_ok=True); path.write_text(json.dumps(values, indent=2), encoding="utf-8"); self.statusBar().showMessage(f"Saved template {path.name}", 5000)
        except OSError as exc: self.show_error("Template save failed", str(exc))

    def dump_mii(self):
        if not self.amiibo: self.show_error("No amiibo loaded", "Open an amiibo first."); return
        path, _ = QFileDialog.getSaveFileName(self, "Dump Mii", "mii.bin", "BIN files (*.bin)")
        if path:
            try: self.amiibo.dump_mii(path)
            except OSError as exc: self.show_error("Mii export failed", str(exc))

    def load_mii(self):
        if not self.amiibo: self.show_error("No amiibo loaded", "Open an amiibo first."); return
        path, _ = QFileDialog.getOpenFileName(self, "Load Mii", "", "BIN files (*.bin)")
        if path:
            try: self.amiibo.set_mii(path); [p.load(self.amiibo) for p in self.editor_pages]
            except InvalidMiiSizeError: self.show_error("Invalid Mii size", "A Mii dump must be exactly 96 bytes.")
            except OSError as exc: self.show_error("Mii import failed", str(exc))

    def select_keys(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select encryption key(s)", "", "BIN files (*.bin)")
        if paths: self.config.write_key_paths(*paths); self.config.save_config(); self.statusBar().showMessage("Encryption key settings saved", 4000)

    def select_regions(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select regions file", "", "Region files (*.json *.txt)")
        if path: self.config.write_region_path(path); self.config.save_config(); QMessageBox.information(self, "Regions saved", "Restart the app to load the new regions file.")

    def setting(self, key, default=None): return self.config.config.get(key, default)
    def save_setting(self, key, value): self.config.config[key] = value; self.config.save_config()
    def set_theme(self, name, persist=True):
        app = QApplication.instance()
        if not app.styleSheet():
            app.setStyleSheet(theme.stylesheet())
        theme.apply_palette(app, name)
        if persist: self.save_setting("qt_theme", name)

    def reset_settings(self):
        for key in ("qt_theme", "output_folder", "amiibo_images_folder", "prefer_image_filename",
                    "recent_enabled", "advanced_mode", "recent_files"):
            self.config.config.pop(key, None)
        self.config.save_config()
        self.image_manager.set_folder("")
        self._update_amiibo_preview()
        self.set_theme("dark")
        self.statusBar().showMessage("UI settings reset", 4000)

    def _remember(self, path):
        if not self.setting("recent_enabled", True): return
        recent = [str(path)] + [p for p in self.setting("recent_files", []) if p != str(path)]
        self.save_setting("recent_files", recent[:8])

    def show_recent_files(self):
        recent = [p for p in self.setting("recent_files", []) if Path(p).exists()]
        if not recent: QMessageBox.information(self, "Recent files", "No recent files are available."); return
        from PySide6.QtWidgets import QInputDialog
        path, ok = QInputDialog.getItem(self, "Recent files", "Open:", recent, 0, False)
        if ok: self.open_file(path)

    def show_error(self, title: str, message: str, detail=None):
        box = QMessageBox(QMessageBox.Icon.Critical, title, message, parent=self)
        if detail: box.setDetailedText(f"{type(detail).__name__}: {detail}")
        box.exec(); self.statusBar().showMessage(message, 7000)
