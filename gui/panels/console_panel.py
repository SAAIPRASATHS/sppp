"""
Terminal-style console panel for real-time simulation logs.
VS Code-inspired aesthetic (Dark-first).
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ConsolePanel(QWidget):
    """Bottom terminal console for simulation output."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """Construct the terminal layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # -- Header / Toolbar --
        header = QWidget()
        header.setObjectName("panelHeader")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(8, 2, 8, 2)
        
        icon_label = QLabel("\U0001f5b3")
        title = QLabel("TERMINAL")
        title.setObjectName("panelTitle")
        
        h_layout.addWidget(icon_label)
        h_layout.addWidget(title)
        h_layout.addStretch()
        
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("consoleClearBtn")
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.clicked.connect(self.clear)
        h_layout.addWidget(self._clear_btn)
        
        layout.addWidget(header)

        # -- Terminal Edit --
        self._terminal = QTextEdit()
        self._terminal.setReadOnly(True)
        self._terminal.setObjectName("terminalOutput")
        
        # Monospace font
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._terminal.setFont(font)
        
        self._terminal.setPlaceholderText("Simulation terminal ready...")
        layout.addWidget(self._terminal)

    def append_text(self, text: str) -> None:
        """Append text and auto-scroll to bottom."""
        self._terminal.append(text)
        self._auto_scroll()

    def clear(self) -> None:
        """Clear the console."""
        self._terminal.clear()

    def _auto_scroll(self) -> None:
        """Move cursor to the end to ensure visibility of new content."""
        self._terminal.moveCursor(QTextCursor.MoveOperation.End)
