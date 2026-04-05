"""
Left sidebar control panel for simulation and sweep setup.
VS Code-inspired aesthetic (Dark-first).
Collapsible sections and unified inputs.
"""

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from gui.widgets.numeric_input import NumericInput


class ControlPanel(QWidget):
    """Left sidebar for simulation controls."""

    runClicked = pyqtSignal(int, int) # (start, stop)
    demoClicked = pyqtSignal()
    sweepClicked = pyqtSignal(int, list) # (start, stops)
    browseClicked = pyqtSignal()
    saveConfigRequested = pyqtSignal()
    loadConfigRequested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """Construct the sidebar layout with collapsible sections."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # -- File Selector Section --
        file_group = QGroupBox("FILES")
        file_layout = QVBoxLayout(file_group)
        file_layout.setContentsMargins(8, 12, 8, 8)
        
        self._exe_path_label = QLabel("No file selected")
        self._exe_path_label.setObjectName("sidebarFileLabel")
        self._exe_path_label.setWordWrap(True)
        file_layout.addWidget(self._exe_path_label)
        
        self._browse_btn = QPushButton("Select Executable...")
        self._browse_btn.setObjectName("sidebarBrowseBtn")
        self._browse_btn.clicked.connect(self.browseClicked.emit)
        file_layout.addWidget(self._browse_btn)
        
        layout.addWidget(file_group)

        # -- Simulation Setup Section --
        setup_group = QGroupBox("SIMULATION SETUP")
        setup_layout = QFormLayout(setup_group)
        setup_layout.setContentsMargins(8, 12, 8, 8)
        setup_layout.setSpacing(10)

        self._start_input = NumericInput(value=0, min_val=0, max_val=4)
        self._stop_input = NumericInput(value=4, min_val=1, max_val=4)
        
        setup_layout.addRow(QLabel("Start:"), self._start_input)
        setup_layout.addRow(QLabel("Stop:"), self._stop_input)
        
        # Config Buttons
        config_row = QHBoxLayout()
        self._save_config_btn = QPushButton("\U0001f4be Save Config")
        self._save_config_btn.setObjectName("sidebarConfigBtn")
        self._save_config_btn.clicked.connect(self.saveConfigRequested.emit)
        
        self._load_config_btn = QPushButton("\U0001f4c2 Load Config")
        self._load_config_btn.setObjectName("sidebarConfigBtn")
        self._load_config_btn.clicked.connect(self.loadConfigRequested.emit)
        
        config_row.addWidget(self._save_config_btn)
        config_row.addWidget(self._load_config_btn)
        setup_layout.addRow(config_row)
        
        self._run_btn = QPushButton("\u25b6  Run Simulation")
        self._run_btn.setObjectName("sidebarRunBtn")
        self._run_btn.setMinimumHeight(36)
        self._run_btn.clicked.connect(self._on_run_click)
        setup_layout.addRow(self._run_btn)
        
        self._demo_btn = QPushButton("\u26a1  Run Demo")
        self._demo_btn.setObjectName("sidebarDemoBtn")
        self._demo_btn.clicked.connect(self.demoClicked.emit)
        setup_layout.addRow(self._demo_btn)

        layout.addWidget(setup_group)

        # -- Collapsible Sweep Mode Section --
        self._sweep_toggle = QToolButton()
        self._sweep_toggle.setCheckable(True)
        self._sweep_toggle.setChecked(False)
        self._sweep_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._sweep_toggle.setText("  SWEEP MODE")
        self._sweep_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self._sweep_toggle.setObjectName("collapsibleToggle")
        self._sweep_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._sweep_toggle.toggled.connect(self._on_sweep_toggle)
        
        layout.addWidget(self._sweep_toggle)
        
        self._sweep_content = QFrame()
        self._sweep_content.setObjectName("collapsibleContent")
        self._sweep_content.setVisible(False)
        sweep_layout = QVBoxLayout(self._sweep_content)
        sweep_layout.setContentsMargins(8, 2, 8, 8)
        sweep_layout.setSpacing(8)
        
        sweep_layout.addWidget(QLabel("Stop Times (comma-separated):"))
        self._sweep_stops_input = QLineEdit()
        self._sweep_stops_input.setPlaceholderText("e.g. 1, 2.5, 4")
        sweep_layout.addWidget(self._sweep_stops_input)
        
        self._sweep_run_btn = QPushButton("\u2632  Run Sweep")
        self._sweep_run_btn.setObjectName("sidebarSweepBtn")
        self._sweep_run_btn.setMinimumHeight(32)
        self._sweep_run_btn.clicked.connect(self._on_sweep_click)
        sweep_layout.addWidget(self._sweep_run_btn)
        
        layout.addWidget(self._sweep_content)

        layout.addStretch(1)

    def update_exe_path(self, path: str) -> None:
        """Update the displayed executable path."""
        if not path:
            self._exe_path_label.setText("No file selected")
            return
        name = Path(path).name
        self._exe_path_label.setText(f"Active: {name}")
        self._exe_path_label.setToolTip(path)

    def _on_run_click(self) -> None:
        """Handle Run button click."""
        self.runClicked.emit(self._start_input.value(), self._stop_input.value())

    def _on_sweep_click(self) -> None:
        """Handle Sweep Run button click."""
        text = self._sweep_stops_input.text().strip()
        if not text:
            return
        try:
            from core.sweep_runner import SweepRunner
            stops = SweepRunner.parse_stop_times(text)
            self.sweepClicked.emit(self._start_input.value(), stops)
        except ValueError:
            pass

    def get_form_values(self) -> dict:
        """Return the current form configuration as a dictionary."""
        return {
            "start_time": self._start_input.value(),
            "stop_time": self._stop_input.value()
        }

    def set_form_values(self, start: int, stop: int) -> None:
        """Update the configuration values in the setup form."""
        self._start_input.setValue(start)
        self._stop_input.setValue(stop)

    def _on_sweep_toggle(self, checked: bool) -> None:
        """Toggle collapsible sweep section visibility."""
        self._sweep_content.setVisible(checked)
        self._sweep_toggle.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)

    def set_running_state(self, is_running: bool) -> None:
        """Disable inputs during simulation."""
        self._run_btn.setEnabled(not is_running)
        self._demo_btn.setEnabled(not is_running)
        self._sweep_run_btn.setEnabled(not is_running)
        self._start_input.setEnabled(not is_running)
        self._stop_input.setEnabled(not is_running)
        self._sweep_stops_input.setEnabled(not is_running)
        self._save_config_btn.setEnabled(not is_running)
        self._load_config_btn.setEnabled(not is_running)
