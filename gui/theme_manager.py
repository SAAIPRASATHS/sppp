"""
Theme Manager for the OpenModelica Simulation Studio.

Provides a centralized, singleton-style theme controller that loads
QSS stylesheets, emits change signals, and supplies consistent
matplotlib plot color palettes for both dark and light modes.
"""

from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMainWindow


# ── QSS file locations ─────────────────────────────────────────
_STYLE_DIR = Path(__file__).resolve().parent / "styles"
_DARK_QSS_PATH = _STYLE_DIR / "dark_theme.qss"
_LIGHT_QSS_PATH = _STYLE_DIR / "light_theme.qss"


# ── Plot color palettes ────────────────────────────────────────
_DARK_PLOT_COLORS: dict[str, str] = {
    "bg": "#1E1E1E",
    "card": "#252526",
    "grid": "#333333",
    "text": "#C5C5C5",
    "text_dim": "#969696",
    "border": "#444444",
    "title": "#FFFFFF",
    "marker_bg": "#1E1E1E",
    "accent": "#007ACC",
    "line": "#58A6FF",
}

_LIGHT_PLOT_COLORS: dict[str, str] = {
    "bg": "#FFFFFF",
    "card": "#FAFAFA",
    "grid": "#E0E0E0",
    "text": "#222222",
    "text_dim": "#888888",
    "border": "#DDDDDD",
    "title": "#222222",
    "marker_bg": "#FFFFFF",
    "accent": "#0066CC",
    "line": "#0969DA",
}


def _load_qss(path: Path) -> str:
    """Load a QSS file and return its content as a string.

    Args:
        path: Path to the .qss stylesheet file.

    Returns:
        Contents of the QSS file, or empty string on error.
    """
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


class ThemeManager(QObject):
    """Centralized theme controller for the Simulation Studio.

    Emits ``themeChanged`` whenever the active theme is switched,
    allowing all connected components (panels, plots, etc.) to
    react accordingly without hard-coded color logic.

    Signals:
        themeChanged (str): Emitted with ``"dark"`` or ``"light"``.
    """

    themeChanged = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._current: str = "dark"  # default theme
        self._dark_qss: str = _load_qss(_DARK_QSS_PATH)
        self._light_qss: str = _load_qss(_LIGHT_QSS_PATH)

    # ── Public API ──────────────────────────────────────────────

    @property
    def current_theme(self) -> str:
        """Return the current theme name (``"dark"`` or ``"light"``)."""
        return self._current

    def is_dark(self) -> bool:
        """Return ``True`` if the current theme is dark."""
        return self._current == "dark"

    def switch_theme(self, theme: str) -> None:
        """Switch to the specified theme.

        Args:
            theme: ``"dark"`` or ``"light"``.
        """
        if theme not in ("dark", "light"):
            return
        self._current = theme
        self.themeChanged.emit(theme)

    def toggle(self) -> None:
        """Toggle between dark and light themes."""
        self.switch_theme("light" if self.is_dark() else "dark")

    def apply(self, window: QMainWindow) -> None:
        """Apply the current theme stylesheet to a QMainWindow.

        Args:
            window: The main window to apply the stylesheet to.
        """
        qss = self._dark_qss if self.is_dark() else self._light_qss
        window.setStyleSheet(qss)

    def get_plot_colors(self) -> dict[str, str]:
        """Return the matplotlib color palette for the active theme.

        Returns:
            A dict with keys: bg, card, grid, text, text_dim,
            border, title, marker_bg, accent, line.
        """
        return dict(_DARK_PLOT_COLORS if self.is_dark() else _LIGHT_PLOT_COLORS)

    def get_qss(self) -> str:
        """Return the raw QSS string for the active theme."""
        return self._dark_qss if self.is_dark() else self._light_qss

    def reload(self) -> None:
        """Reload QSS files from disk (useful during development)."""
        self._dark_qss = _load_qss(_DARK_QSS_PATH)
        self._light_qss = _load_qss(_LIGHT_QSS_PATH)
