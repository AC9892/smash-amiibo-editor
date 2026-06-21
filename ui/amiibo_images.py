"""Offline lookup of amiibo artwork from user-owned local PNG files."""

import re
import random
from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtGui import QPixmap


def normalize(value: str) -> str:
    """Normalize names for matching while retaining letters and numbers."""
    return re.sub(r"[^a-z0-9]", "", value.casefold())


class AmiiboImageResolver:
    def __init__(self):
        self._indexed_folder: Path | None = None
        self._indexed = False
        self._images: list[Path] = []
        self._matches: dict[tuple[str, ...], Path | None] = {}

    def set_folder(self, folder: str) -> None:
        path = Path(folder).expanduser() if folder else None
        if path != self._indexed_folder:
            self._indexed_folder = path
            self._indexed = False
            self._images = []
            self._matches.clear()

    def find(self, name: str = "", character: str = "", series: str = "", filename: str = "",
             prefer_character: bool = False) -> Path | None:
        # The source filename is especially important for non-Smash figures,
        # whose Smash application-area character bytes do not identify the figure.
        order = (character, name, filename) if prefer_character else (filename, name, character)
        candidates = tuple(value.strip() for value in order if value and value.strip())
        key = (*candidates, series.strip())
        if key in self._matches:
            return self._matches[key]
        self._ensure_indexed()
        groups = self._series_groups(series)

        def choose(predicate):
            # Never mix series/type folders when that folder has a valid match.
            for group in groups:
                matches = [path for path in group if predicate(path)]
                if matches:
                    return random.choice(matches)
            return None

        # Treat exact names and appended styles as one figure family. If more
        # than one image exists in the preferred series/type folder, choose a
        # random one and retain it in the runtime match cache.
        for candidate in candidates:
            wanted = normalize(candidate)
            if len(wanted) < 3:
                continue
            match = choose(lambda path, value=wanted: normalize(path.stem) == value
                           or normalize(path.stem).startswith(value))
            if match:
                self._matches[key] = match
                return match

        # A conservative partial match handles filenames with an appended variant.
        result = None
        for group in groups:
            ranked = []
            for candidate in candidates:
                wanted = normalize(candidate)
                if len(wanted) < 3:
                    continue
                for path in group:
                    stem = normalize(path.stem)
                    if wanted in stem or stem in wanted:
                        ranked.append((abs(len(stem) - len(wanted)), path))
            if ranked:
                best_score = min(score for score, _path in ranked)
                result = random.choice([path for score, path in ranked if score == best_score])
                break
        self._matches[key] = result
        return result

    def _ensure_indexed(self) -> None:
        if self._indexed:
            return
        self._indexed = True
        if not self._indexed_folder or not self._indexed_folder.is_dir():
            return
        try:
            self._images = sorted(
                (path for path in self._indexed_folder.rglob("*") if path.is_file() and path.suffix.casefold() == ".png"),
                key=lambda path: str(path).casefold(),
            )
        except OSError:
            self._images = []

    def _series_groups(self, series: str) -> list[list[Path]]:
        wanted = normalize(series)
        if not wanted:
            return [self._images]
        preferred, remaining = [], []
        for path in self._images:
            parents = path.relative_to(self._indexed_folder).parts[:-1]
            (preferred if any(normalize(part) == wanted for part in parents) else remaining).append(path)
        return [preferred, remaining] if preferred else [remaining]


class AmiiboImageManager(QObject):
    """One cached image source with independent file and fighter channels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resolver = AmiiboImageResolver()
        self._pixmaps: dict[Path, QPixmap] = {}
        self._widgets: dict[str, list] = {}
        self._last_keys: dict[str, tuple] = {}
        self._current: dict[str, tuple] = {}

    def bind(self, widget, channel: str = "fighter") -> None:
        self._widgets.setdefault(channel, []).append(widget)
        widget.set_image_data(*self._current.get(channel, (QPixmap(), "Image Not Found", None)))

    def set_folder(self, folder: str) -> None:
        self.resolver.set_folder(folder)
        self._last_keys.clear()

    def select(self, character: str = "", name: str = "", series: str = "", filename: str = "",
               prefer_filename: bool = False, channel: str = "fighter") -> None:
        key = (character, name, series, filename, prefer_filename)
        if key == self._last_keys.get(channel):
            return
        self._last_keys[channel] = key
        # Fighter data is authoritative by default. Excluding the filename from
        # fallback prevents a renamed/modded BIN from showing the wrong fighter.
        lookup_filename = filename if prefer_filename or not character else ""
        path = self.resolver.find(name, character, series, lookup_filename,
                                  prefer_character=not prefer_filename)
        if path:
            pixmap = self._pixmaps.get(path)
            if pixmap is None:
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    self._pixmaps[path] = pixmap
            if pixmap is not None and not pixmap.isNull():
                self._set_channel(channel, (pixmap, character or path.stem, path))
                return
        self._set_channel(channel, (QPixmap(), "Image Not Found", None))

    def clear(self, channel: str | None = None) -> None:
        channels = [channel] if channel else list(self._widgets)
        for name in channels:
            self._last_keys.pop(name, None)
            self._set_channel(name, (QPixmap(), "Image Not Found", None))

    def _set_channel(self, channel: str, image_data: tuple) -> None:
        self._current[channel] = image_data
        for widget in self._widgets.get(channel, []):
            widget.set_image_data(*image_data)
