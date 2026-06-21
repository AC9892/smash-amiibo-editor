"""Qt controls backed by the existing region section objects."""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QAbstractSpinBox, QComboBox, QDoubleSpinBox, QHBoxLayout, QLineEdit, QSlider, QSpinBox, QVBoxLayout, QWidget

from utils import region_parse as parse
from ui.widgets.form_row import FormRow
from ui.widgets.info_card import InfoCard


class SliderEditor(QWidget):
    """A clean slider paired with a directly editable numeric field."""

    valueChanged = Signal(object)

    def __init__(self, minimum: float, maximum: float, decimals: int = 0, suffix: str = "", parent=None):
        super().__init__(parent)
        self.decimals = decimals
        self.scale = 10 ** decimals
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(round(minimum * self.scale), round(maximum * self.scale))
        if decimals:
            self.input = QDoubleSpinBox()
            self.input.setDecimals(decimals)
        else:
            self.input = QSpinBox()
        self.input.setRange(minimum, maximum)
        self.input.setSuffix(suffix)
        self.input.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.input.setKeyboardTracking(False)
        self.input.setFixedWidth(112)
        self.input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.slider.valueChanged.connect(self._from_slider)
        self.input.editingFinished.connect(self._from_input)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.input)

    def value(self):
        return self.input.value()

    def setValue(self, value):
        numeric = float(value or 0)
        self.slider.setValue(round(numeric * self.scale))
        self.input.setValue(numeric)

    def _set_text(self, value):
        self.input.blockSignals(True)
        self.input.setValue(value)
        self.input.blockSignals(False)

    def _from_slider(self, raw_value):
        value = raw_value / self.scale
        self._set_text(value)
        self.valueChanged.emit(value if self.decimals else int(value))

    def _from_input(self):
        value = self.input.value()
        self.slider.blockSignals(True)
        self.slider.setValue(round(value * self.scale))
        self.slider.blockSignals(False)
        self.valueChanged.emit(value)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.slider.setEnabled(enabled)
        self.input.setEnabled(enabled)


class SectionEditor(QWidget):
    changed = Signal()

    def __init__(self, title: str, predicate, parent=None, use_sliders: bool = False):
        super().__init__(parent)
        self.predicate = predicate
        self.bindings: list[tuple[object, QWidget]] = []
        self.amiibo = None
        self.use_sliders = use_sliders
        self.layout = QVBoxLayout(self)
        self.card = InfoCard(title)
        self.card.layout().removeWidget(self.card.body)
        self.card.body.deleteLater()
        self.form = self.card.layout()
        self.layout.addWidget(self.card)
        self.layout.addStretch()

    def set_sections(self, sections: list[object]):
        for section in sections:
            if self.predicate(section) and hasattr(section, "get_value_from_bin"):
                editor = self._make_editor(section)
                self.bindings.append((section, editor))
                self.form.addWidget(FormRow(str(section), editor, getattr(section, "description", "")))

    def _make_editor(self, section):
        if isinstance(section, parse.ENUM):
            editor = QComboBox()
            editor.addItems(section.options.keys())
            editor.currentTextChanged.connect(lambda value, s=section: self._write(s, value))
        elif self.use_sliders and isinstance(section, parse.percentage):
            editor = SliderEditor(0, 100, 5, " %")
            editor.valueChanged.connect(lambda value, s=section: self._write(s, value))
        elif self.use_sliders and isinstance(section, parse.ByteWise):
            editor = SliderEditor(section.min, section.max)
            editor.valueChanged.connect(lambda value, s=section: self._write(s, value))
        elif isinstance(section, parse.percentage):
            editor = QDoubleSpinBox()
            editor.setRange(0, 100)
            editor.setDecimals(5)
            editor.setSuffix(" %")
            editor.valueChanged.connect(lambda value, s=section: self._write(s, value))
        elif isinstance(section, parse.ByteWise):
            editor = QSpinBox()
            editor.setRange(section.min, section.max)
            editor.valueChanged.connect(lambda value, s=section: self._write(s, value))
        else:
            editor = QLineEdit()
            if isinstance(section, parse.Text):
                editor.setMaxLength(section.characters)
            editor.editingFinished.connect(lambda s=section, e=editor: self._write(s, e.text()))
        editor.setEnabled(False)
        return editor

    def load(self, amiibo):
        self.amiibo = amiibo
        for section, editor in self.bindings:
            editor.blockSignals(True)
            value = section.get_value_from_bin(amiibo) if amiibo else ""
            if isinstance(editor, QComboBox):
                editor.setCurrentText(str(value))
            elif isinstance(editor, (QSpinBox, QDoubleSpinBox, SliderEditor)):
                editor.setValue(value or 0)
            else:
                editor.setText(str(value))
            editor.setEnabled(amiibo is not None)
            editor.blockSignals(False)

    def _write(self, section, value):
        if self.amiibo is None:
            return
        try:
            if isinstance(section, parse.bits):
                value = section.validate_input(str(value)) or "0"
            section.set_value_in_bin(self.amiibo, value)
            self.changed.emit()
        except (ValueError, OverflowError) as exc:
            self.window().show_error("Invalid value", str(exc))

    def values(self) -> dict:
        return {str(section): section.get_value_from_bin(self.amiibo) for section, _ in self.bindings} if self.amiibo else {}
