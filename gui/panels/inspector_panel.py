"""
Right sidebar inspector panel for execution details and generated outputs.
VS Code-inspired aesthetic (Dark-first).
Status cards and detailed informational lists.
"""

from pathlib import Path

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


class InspectorPanel(QWidget):
    """Right sidebar for simulation status and output file inspection."""

    downloadClicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """Construct the inspector layout with status cards."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        # -- Status Section --
        status_group = QGroupBox("EXECUTION STATUS")
        status_layout = QVBoxLayout(status_group)
        status_layout.setContentsMargins(8, 12, 8, 8)
        
        self._status_card = QWidget()
        self._status_card.setObjectName("statusCard")
        status_card_layout = QHBoxLayout(self._status_card)
        
        self._status_dot = QLabel("\u25cf")
        self._status_dot.setObjectName("statusDotLarge")
        self._status_label = QLabel("Ready")
        self._status_label.setObjectName("statusLabelLarge")
        
        status_card_layout.addWidget(self._status_dot)
        status_card_layout.addWidget(self._status_label, 1)
        
        status_layout.addWidget(self._status_card)
        
        self._exec_time_label = QLabel("Duration: 0.000s")
        self._exec_time_label.setObjectName("inspectorDetail")
        status_layout.addWidget(self._exec_time_label)

        # Quick Insight Label
        self._insight_label = QLabel("")
        self._insight_label.setObjectName("insightLabel")
        self._insight_label.setWordWrap(True)
        self._insight_label.setStyleSheet("font-style: italic; color: #969696; font-size: 11px;")
        status_layout.addWidget(self._insight_label)

        layout.addWidget(status_group)

        # -- Current Setup Info --
        info_group = QGroupBox("RUN PARAMETERS")
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(4)
        
        self._params_label = QLabel("Start: 0 | Stop: 4")
        self._params_label.setObjectName("inspectorDetailLong")
        info_layout.addWidget(self._params_label)
        
        self._exe_name_label = QLabel("Executable: ---")
        self._exe_name_label.setObjectName("inspectorDetailLong")
        self._exe_name_label.setWordWrap(True)
        info_layout.addWidget(self._exe_name_label)
        
        layout.addWidget(info_group)

        # -- Generated Files Section --
        files_group = QGroupBox("GENERATED FILES")
        files_layout = QVBoxLayout(files_group)
        files_layout.setContentsMargins(8, 12, 8, 8)
        
        self._files_list = QListWidget()
        self._files_list.setObjectName("inspectorFilesList")
        self._files_list.setToolTip("Click to view file details")
        files_layout.addWidget(self._files_list)

        # Download Button
        self._download_btn = QPushButton("\u2913  Download Results")
        self._download_btn.setObjectName("downloadBtn")
        self._download_btn.setEnabled(False)
        self._download_btn.clicked.connect(self.downloadClicked.emit)
        files_layout.addWidget(self._download_btn)
        
        layout.addWidget(files_group)

        layout.addStretch(1)

    def update_status(self, text: str, color: str) -> None:
        """Update the status label and dot color."""
        self._status_label.setText(text)
        self._status_dot.setStyleSheet(f"color: {color};")
        self._status_label.setStyleSheet(f"color: {color};")

    def update_exec_info(self, elapsed: float, start: int, stop: int, exe_path: str) -> None:
        """Update execution time and parameter info."""
        self._exec_time_label.setText(f"Duration: {elapsed:.3f}s")
        self._params_label.setText(f"Start: {start} | Stop: {stop}")
        self._exe_name_label.setText(f"Executable: {Path(exe_path).name if exe_path else '---'}")

    def update_insight(self, message: str) -> None:
        """Update the quick insight text."""
        self._insight_label.setText(message)

    def update_files_list(self, files: list) -> None:
        """Populate the generated files list."""
        self._files_list.clear()
        self._download_btn.setEnabled(len(files) > 0)
        for rf in files:
            item = QListWidgetItem(f" \U0001f4c4 {rf.name}")
            item.setToolTip(f"{rf.full_path} ({rf.size_display})")
            self._files_list.addItem(item)
