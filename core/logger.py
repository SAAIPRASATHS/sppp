"""
Output formatting and logging for the Simulation Runner.

Provides structured, timestamped log entries for the console widget
and optional file-based logging.
"""

import logging
from datetime import datetime
from enum import Enum, auto
from pathlib import Path


class LogLevel(Enum):
    """Log severity levels with visual prefixes."""
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    OUTPUT = auto()


# Color mapping for HTML-formatted log output
_LEVEL_COLORS: dict[LogLevel, str] = {
    LogLevel.INFO: "#5DADE2",
    LogLevel.SUCCESS: "#2ECC71",
    LogLevel.WARNING: "#F39C12",
    LogLevel.ERROR: "#E74C3C",
    LogLevel.OUTPUT: "#BDC3C7",
}

_LEVEL_PREFIXES: dict[LogLevel, str] = {
    LogLevel.INFO: "ℹ INFO",
    LogLevel.SUCCESS: "✔ SUCCESS",
    LogLevel.WARNING: "⚠ WARNING",
    LogLevel.ERROR: "✖ ERROR",
    LogLevel.OUTPUT: "▸ OUTPUT",
}


class SimulationLogger:
    """Formats and manages log output for the simulation runner.

    Generates HTML-formatted log entries with timestamps to display
    in the QTextEdit console widget. Optionally writes to a log file.
    """

    def __init__(self, log_file: Path | None = None):
        """Initialize the logger.

        Args:
            log_file: Optional path to write plain-text logs.
        """
        self._file_logger: logging.Logger | None = None
        if log_file:
            self._setup_file_logger(log_file)

    def _setup_file_logger(self, log_file: Path) -> None:
        """Configure a file-based logger."""
        log_file.parent.mkdir(parents=True, exist_ok=True)
        self._file_logger = logging.getLogger("SimulationRunner")
        self._file_logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(str(log_file), encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        self._file_logger.addHandler(handler)

    @staticmethod
    def format_entry(message: str, level: LogLevel = LogLevel.INFO) -> str:
        """Create an HTML-formatted log entry.

        Args:
            message: The log message text.
            level: Severity level for color-coding.

        Returns:
            HTML string ready for QTextEdit.append().
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = _LEVEL_COLORS[level]
        prefix = _LEVEL_PREFIXES[level]
        escaped = message.replace("<", "&lt;").replace(">", "&gt;")

        return (
            f'<span style="color:#888;">[{timestamp}]</span> '
            f'<span style="color:{color};font-weight:bold;">{prefix}</span> '
            f'<span style="color:{color};">{escaped}</span>'
        )

    def log(self, message: str, level: LogLevel = LogLevel.INFO) -> str:
        """Format a log entry and optionally write to file.

        Args:
            message: The log message text.
            level: Severity level.

        Returns:
            HTML-formatted string for display.
        """
        if self._file_logger:
            log_map = {
                LogLevel.INFO: self._file_logger.info,
                LogLevel.SUCCESS: self._file_logger.info,
                LogLevel.WARNING: self._file_logger.warning,
                LogLevel.ERROR: self._file_logger.error,
                LogLevel.OUTPUT: self._file_logger.debug,
            }
            log_map[level](message)

        return self.format_entry(message, level)

    @staticmethod
    def separator() -> str:
        """Return an HTML horizontal rule for visual log separation."""
        return '<hr style="border:1px solid #444;">'
