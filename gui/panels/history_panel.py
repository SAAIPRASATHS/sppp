"""
History panel for managing, reviewing, and comparing past simulation runs.
VS Code-themed side drawer style (Dark-first).
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.history_manager import HistoryEntry, HistoryManager


class HistoryPanel(QWidget):
    """Sidebar component for simulation run history and comparison."""

    reloadRequested = pyqtSignal(HistoryEntry)
    compareRequested = pyqtSignal()

    def __init__(self, history_manager: HistoryManager, parent: QWidget | None = None):
        super().__init__(parent)
        self._history_mgr = history_manager
        self._init_ui()

    def _init_ui(self) -> None:
        """Construct the history layout with action buttons."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # -- History List Section --
        hist_group = QGroupBox("RUN HISTORY")
        hist_layout = QVBoxLayout(hist_group)
        hist_layout.setContentsMargins(8, 12, 8, 8)
        
        self._history_list = QListWidget()
        self._history_list.setObjectName("historyListSidebar")
        self._history_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        hist_layout.addWidget(self._history_list)

        # -- Action Buttons --
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        
        self._compare_btn = QPushButton("\U0001f504  Compare")
        self._compare_btn.setObjectName("sidebarCompareBtn")
        self._compare_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._compare_btn.clicked.connect(self.compareRequested.emit)
        btn_layout.addWidget(self._compare_btn)
        
        self._clear_btn = QPushButton("\U0001f5d1")
        self._clear_btn.setObjectName("sidebarClearBtn")
        self._clear_btn.setToolTip("Clear History")
        self._clear_btn.clicked.connect(self._on_clear_click)
        btn_layout.addWidget(self._clear_btn)
        
        hist_layout.addLayout(btn_layout)
        
        layout.addWidget(hist_group)
        layout.addStretch(1)

    def refresh(self) -> None:
        """Reload history list from the history manager."""
        self._history_list.clear()
        for entry in self._history_mgr.entries:
            item = QListWidgetItem(f" \U0001f4c1 {entry.timestamp} ({entry.duration:.2f}s)")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            item.setToolTip(f"{entry.executable}\nStart: {entry.start_time} | Stop: {entry.stop_time}\nStatus: {entry.status}")
            self._history_list.addItem(item)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle run reload when double-clicking an item."""
        entry = item.data(Qt.ItemDataRole.UserRole)
        if entry:
            self.reloadRequested.emit(entry)

    def _on_clear_click(self) -> None:
        """Clear the history data."""
        self._history_mgr.clear()
        self.refresh()
