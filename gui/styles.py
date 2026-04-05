"""
Theme manager for the OpenModelica Simulation Runner.

Loads stylesheets from external QSS files for easy customization.
Provides DARK_THEME and LIGHT_THEME strings plus a helper to
load from file at runtime.
"""

from pathlib import Path

# Directory containing the QSS files
_STYLE_DIR = Path(__file__).resolve().parent

_DARK_QSS = _STYLE_DIR / "styles.qss"
_LIGHT_QSS = _STYLE_DIR / "styles_light.qss"


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


# Pre-load both themes at import time for backward compatibility
DARK_THEME: str = _load_qss(_DARK_QSS)
LIGHT_THEME: str = _load_qss(_LIGHT_QSS)


def reload_themes() -> tuple[str, str]:
    """Reload themes from disk (useful during development).

    Returns:
        Tuple of (dark_theme, light_theme) stylesheet strings.
    """
    global DARK_THEME, LIGHT_THEME
    DARK_THEME = _load_qss(_DARK_QSS)
    LIGHT_THEME = _load_qss(_LIGHT_QSS)
    return DARK_THEME, LIGHT_THEME
