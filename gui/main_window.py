"""
Main window UI for the OpenModelica Simulation Studio v5.0.

Professional-grade Workspace UI with resizable panels, terminal console,
real-time simulation results, and data inspector. Features seamless
dual-theme (dark/light) switching via ThemeManager.
"""

import json
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QLabel,
    QFileDialog,
)

# Panels
from gui.panels.control_panel import ControlPanel
from gui.panels.console_panel import ConsolePanel
from gui.panels.plot_panel import PlotPanel
from gui.panels.inspector_panel import InspectorPanel
from gui.panels.history_panel import HistoryPanel

# Core Logic
from core.history_manager import HistoryManager, HistoryEntry
from core.logger import LogLevel, SimulationLogger
from core.report_generator import ReportGenerator, SimulationReport
from core.result_parser import scan_result_files, parse_csv_preview
from core.simulation_runner import SimulationRunner
from core.sweep_runner import SweepRunner, SweepRunResult
from core.validator import SimulationValidator

from core.export_manager import ExportManager
from core.config_manager import ConfigManager, SimulationConfig
from core.output_manager import OutputManager

from gui.theme_manager import ThemeManager
from gui.compare_view import CompareView
from utils.file_handler import select_executable, inspect_file, FileInfo

# Settings
_SETTINGS_FILE = Path(__file__).resolve().parent.parent / ".sim_settings.json"
_MODEL_DIR = Path(__file__).resolve().parent.parent / "model"


class MainWindow(QMainWindow):
    """Primary application window for Simulation Studio (v5.0).

    Multi-panel Layout:
    - Sidebar (Left): Control & Setup
    - Workspace (Center): Visualization & Terminal
    - Inspector (Right): Details & Status
    - Toolbar (Top): Action items + Theme toggle
    """

    def __init__(self) -> None:
        super().__init__()
        self._runner = None
        self._sweep_runner = None
        self._logger = SimulationLogger()
        self._exe_path = ""
        self._last_elapsed = 0.0
        self._last_csv_path = ""
        self._current_run_folder = None

        # Theme Manager
        self._theme_mgr = ThemeManager(parent=self)

        # Managers
        self._history_mgr = HistoryManager()
        self._report_gen = ReportGenerator()
        self._output_mgr = OutputManager(Path.cwd())

        self._init_ui()
        self._load_settings()
        self._auto_load_model()
        self._apply_theme()
        self._update_status("Ready", "#3fb950")

    def _init_ui(self) -> None:
        """Construct the workspace with splitters and panels."""
        self.setWindowTitle("Simulation Studio \u2014 OpenModelica")
        self.setMinimumSize(QSize(1200, 800))

        # -- Core Panels (pass theme_mgr to plot panel) --
        self._control_panel = ControlPanel()
        self._console_panel = ConsolePanel()
        self._plot_panel = PlotPanel(self._theme_mgr)
        self._inspector_panel = InspectorPanel()
        self._history_panel = HistoryPanel(self._history_mgr)

        # -- Workspace Layout (Horizontal Splitter) --
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left Sidebar (Controls + History)
        side_container = QWidget()
        side_layout = QVBoxLayout(side_container)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)
        side_layout.addWidget(self._control_panel)
        side_layout.addWidget(self._history_panel)
        self._main_splitter.addWidget(side_container)

        # 2. Central Workspace (Vertical Splitter: Plot + Console)
        self._work_splitter = QSplitter(Qt.Orientation.Vertical)
        self._work_splitter.addWidget(self._plot_panel)
        self._work_splitter.addWidget(self._console_panel)
        self._work_splitter.setStretchFactor(0, 3)
        self._work_splitter.setStretchFactor(1, 1)
        self._main_splitter.addWidget(self._work_splitter)

        # 3. Right Sidebar (Inspector)
        self._main_splitter.addWidget(self._inspector_panel)

        # Proportions
        self._main_splitter.setStretchFactor(0, 1)
        self._main_splitter.setStretchFactor(1, 4)
        self._main_splitter.setStretchFactor(2, 1)

        self.setCentralWidget(self._main_splitter)

        # -- Tools & Status --
        self._init_toolbar()
        self._init_status()
        self._connect_signals()

    def _init_toolbar(self) -> None:
        """Create the top action toolbar."""
        toolbar = QToolBar("Studio Actions")
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Run Action
        self._run_act = QAction("\u25b6 Run", self)
        self._run_act.setToolTip("Execute Simulation")
        self._run_act.triggered.connect(self._on_run_requested_toolbar)
        toolbar.addAction(self._run_act)

        # Stop Action
        self._stop_act = QAction("\u23f9 Stop", self)
        self._stop_act.setToolTip("Abort Active Run")
        self._stop_act.setEnabled(False)
        self._stop_act.triggered.connect(self._on_stop_requested)
        toolbar.addAction(self._stop_act)

        toolbar.addSeparator()

        # Plot Action (Manual Trigger)
        self._plot_act = QAction("\U0001f4c8 Plot", self)
        self._plot_act.setToolTip("Visualize Last Simulation Output")
        self._plot_act.triggered.connect(self._scan_and_plot_latest)
        toolbar.addAction(self._plot_act)

        # Compare Action
        self._compare_act = QAction("\U0001f504 Compare", self)
        self._compare_act.setToolTip("Launch Comparison Studio")
        self._compare_act.triggered.connect(self._on_compare_requested)
        toolbar.addAction(self._compare_act)

        toolbar.addSeparator()

        # Dark/Light Toggle
        self._theme_act = QAction("\U0001f319 Dark", self)
        self._theme_act.setToolTip("Toggle between Dark and Light themes")
        self._theme_act.triggered.connect(self._toggle_theme)
        toolbar.addAction(self._theme_act)

    def _init_status(self) -> None:
        """Setup the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_label = QLabel("Studio Ready")
        self._status_bar.addWidget(self._status_label)

    def _connect_signals(self) -> None:
        """Connect panel signals to runners and internal logic."""
        # Control Panel
        self._control_panel.runClicked.connect(self._on_run_requested)
        self._control_panel.demoClicked.connect(self._on_demo_requested)
        self._control_panel.sweepClicked.connect(self._on_sweep_requested)
        self._control_panel.browseClicked.connect(self._on_browse_requested)
        self._control_panel.saveConfigRequested.connect(self._on_save_config)
        self._control_panel.loadConfigRequested.connect(self._on_load_config)

        # Inspector Panel
        self._inspector_panel.downloadClicked.connect(self._on_download_requested)

        # History Panel
        self._history_panel.reloadRequested.connect(self._on_history_reload)
        self._history_panel.compareRequested.connect(self._on_compare_requested)

    # -- Configuration Handlers -------------------------------------

    def _on_save_config(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Simulation Configuration", "", "JSON Config (*.json)")
        if not path:
            return
        
        vals = self._control_panel.get_form_values()
        config = SimulationConfig(self._exe_path, vals["start_time"], vals["stop_time"])
        if ConfigManager.save_config(config.to_dict(), Path(path)):
            self._log(f"Configuration saved to {Path(path).name}", LogLevel.SUCCESS)
        else:
            QMessageBox.critical(self, "Save Error", "Failed to save configuration file.")

    def _on_load_config(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open Simulation Configuration", "", "JSON Config (*.json)")
        if not path:
            return
        
        data = ConfigManager.load_config(Path(path))
        if data:
            config = SimulationConfig.from_dict(data)
            if config.exe_path and Path(config.exe_path).exists():
                self._exe_path = config.exe_path
                self._control_panel.update_exe_path(config.exe_path)
            self._control_panel.set_form_values(config.start_time, config.stop_time)
            self._log(f"Configuration loaded from {Path(path).name}", LogLevel.INFO)
        else:
            QMessageBox.critical(self, "Load Error", "Failed to load configuration or file is invalid.")

    # -- Event Handlers ---------------------------------------------

    def _on_browse_requested(self) -> None:
        path = select_executable(self)
        if path:
            self._exe_path = path
            self._control_panel.update_exe_path(path)
            self._inspector_panel.update_exec_info(0, 0, 0, path)
            self._log(f"Studio active: {path}", LogLevel.INFO)
            self._save_settings()

    def _on_run_requested(self, start, stop) -> None:
        validation = SimulationValidator.validate_file_path(self._exe_path)
        if not validation.is_valid:
            QMessageBox.warning(self, "Invalid Executable", validation.message)
            return
        self._execute_simulation(start, stop)

    def _on_run_requested_toolbar(self) -> None:
        """Triggered from toolbar Run button."""
        self._control_panel._run_btn.click()

    def _on_demo_requested(self) -> None:
        validation = SimulationValidator.validate_file_path(self._exe_path)
        if not validation.is_valid:
            QMessageBox.warning(self, "Invalid Executable", validation.message)
            return
        self._execute_simulation(0, 4)

    def _execute_simulation(self, start: int, stop: int) -> None:
        """Launch the runner thread."""
        self._set_running_state(True)
        self._console_panel.clear()
        self._plot_panel.reset()
        self._update_status("Running Simulation...", "#d29922")
        self._last_elapsed = 0.0
        self._inspector_panel.update_insight("Running...")

        # Organization: Create run folder
        self._current_run_folder = self._output_mgr.make_run_folder()

        self._runner = SimulationRunner(self._exe_path, start, stop, parent=self)
        self._runner.stdout_ready.connect(lambda l: self._console_panel.append_text(self._logger.format_entry(l, LogLevel.OUTPUT)))
        self._runner.stderr_ready.connect(lambda l: self._console_panel.append_text(self._logger.format_entry(l, LogLevel.WARNING)))
        self._runner.execution_time.connect(self._on_exec_time_updated)
        self._runner.finished_signal.connect(self._on_run_finished)
        self._runner.error_occurred.connect(self._on_run_error)

        self._runner.start()
        self._save_settings()

    def _on_exec_time_updated(self, elapsed: float) -> None:
        self._last_elapsed = elapsed
        self._inspector_panel.update_exec_info(elapsed, 0, 0, self._exe_path)

    def _on_run_finished(self, return_code: int) -> None:
        self._set_running_state(False)
        status = "Success" if return_code == 0 else "Failed"
        color = "#3fb950" if return_code == 0 else "#f85149"
        
        self._update_status(f"Completed ({status})", color)
        self._inspector_panel.update_status(status, color)
        self._log(f"Simulation {status.lower()} with code {return_code}", LogLevel.SUCCESS if return_code == 0 else LogLevel.ERROR)

        # Organization: Move files to run folder and scan
        exe_dir = Path(self._exe_path).parent
        gen_files = scan_result_files(str(exe_dir), smart_filter=True)
        
        if self._current_run_folder:
            for rf in gen_files:
                try:
                    dest = self._current_run_folder / Path(rf.full_path).name
                    # Move if not already there (which it isn't yet)
                    import shutil
                    shutil.move(rf.full_path, dest)
                    rf.full_path = str(dest) # Update path in FileInfo
                except OSError: pass
            
            # Re-scan in run folder
            gen_files = scan_result_files(str(self._current_run_folder), smart_filter=False)

        self._inspector_panel.update_files_list(gen_files)

        # Quick Insight
        insight = f"Simulation {status.lower()} in {self._last_elapsed:.2f}s. "
        if gen_files:
            insight += f"Found {len(gen_files)} output files."
        else:
            insight += "No result files detected."
        self._inspector_panel.update_insight(insight)

        # Add to history (use actual runner params, not hardcoded)
        runner_start = self._runner._start_time if self._runner else 0
        runner_stop = self._runner._stop_time if self._runner else 0
        self._history_mgr.add(
            executable=Path(self._exe_path).name,
            start_time=runner_start,
            stop_time=runner_stop,
            status=status,
            duration=self._last_elapsed,
            return_code=return_code,
            output_file=str(gen_files[0].full_path) if gen_files else ""
        )
        self._history_panel.refresh()

        # Auto-plot if successful
        if return_code == 0 and gen_files:
            self._plot_latest_csv(gen_files[0].full_path)

    def _on_run_error(self, message: str) -> None:
        self._set_running_state(False)
        self._update_status("Error", "#f85149")
        self._inspector_panel.update_status("Error", "#f85149")
        self._inspector_panel.update_insight(f"Error: {message}")
        self._log(message, LogLevel.ERROR)

    def _on_stop_requested(self) -> None:
        """Abort simulation."""
        if self._runner and self._runner.isRunning():
            self._runner.terminate()
            self._log("Simulation aborted by user.", LogLevel.WARNING)
            self._set_running_state(False)

    def _on_download_requested(self) -> None:
        """Export results to a chosen folder or ZIP."""
        if not self._current_run_folder:
            return
        
        files = [p for p in self._current_run_folder.iterdir() if p.is_file()]
        if not files:
            QMessageBox.information(self, "Export results", "No result files were found for this run.")
            return

        choice = QMessageBox.question(self, "Export Results", "Would you like to export as a ZIP archive?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        
        if choice == QMessageBox.StandardButton.Cancel:
            return

        if choice == QMessageBox.StandardButton.Yes:
            path, _ = QFileDialog.getSaveFileName(self, "Export as ZIP", "simulation_results.zip", "ZIP Archive (*.zip)")
            if path:
                if ExportManager.create_zip(files, Path(path)):
                    self._log(f"Results zipped to {Path(path).name}", LogLevel.SUCCESS)
                else:
                    QMessageBox.warning(self, "Export Error", "Failed to create ZIP archive.")
        else:
            path = QFileDialog.getExistingDirectory(self, "Select Export Directory")
            if path:
                if ExportManager.copy_results(files, Path(path)):
                    self._log(f"Results exported to {Path(path).name}", LogLevel.SUCCESS)
                else:
                    QMessageBox.warning(self, "Export Error", "Failed to copy result files.")

    # -- Sweep Logic ------------------------------------------------

    def _on_sweep_requested(self, start: int, stops: list) -> None:
        if not self._exe_path:
            QMessageBox.warning(self, "No Executable", "Select a file first.")
            return

        self._set_running_state(True)
        self._console_panel.clear()
        self._update_status(f"Running Sweep (0/{len(stops)})...", "#8957e5")
        self._inspector_panel.update_insight("Running Parameter Sweep...")
        
        self._sweep_runner = SweepRunner(self._exe_path, start, stops, parent=self)
        self._sweep_runner.run_stdout.connect(self._console_panel.append_text)
        self._sweep_runner.run_completed.connect(self._on_sweep_run_completed)
        self._sweep_runner.sweep_finished.connect(self._on_sweep_finished)
        self._sweep_runner.start()

    def _on_sweep_run_completed(self, result: SweepRunResult) -> None:
        self._log(f"Sweep run {result.index+1} finished: {result.status}", LogLevel.INFO)
        self._history_mgr.add(
            executable=Path(self._exe_path).name,
            start_time=result.start_time,
            stop_time=result.stop_time,
            status=result.status,
            duration=result.elapsed,
            return_code=result.return_code,
            output_file=result.csv_path
        )
        self._history_panel.refresh()

    def _on_sweep_finished(self, results: list) -> None:
        self._set_running_state(False)
        self._update_status("Sweep Completed", "#3fb950")
        self._log("Parameter sweep completed.", LogLevel.SUCCESS)
        self._inspector_panel.update_insight(f"Sweep completed with {len(results)} runs.")

    # -- Analysis ---------------------------------------------------

    def _on_compare_requested(self) -> None:
        """Launch the Compare runs dialog/view."""
        self._compare_view = CompareView(self._history_mgr, self._theme_mgr)
        self._compare_view.setWindowTitle("Compare Studio")
        self._compare_view.resize(1000, 600)
        # Apply current theme to the new window
        self._compare_view.setStyleSheet(self._theme_mgr.get_qss())
        self._compare_view.refresh_runs()
        self._compare_view.show()

    def _scan_and_plot_latest(self) -> None:
        if not self._exe_path: return
        exe_dir = str(Path(self._exe_path).parent)
        files = scan_result_files(exe_dir, smart_filter=True)
        if files:
            self._plot_latest_csv(files[0].full_path)

    def _plot_latest_csv(self, path: str) -> None:
        preview = parse_csv_preview(path)
        if not preview.error:
            self._plot_panel.load_preview(preview)

    def _on_history_reload(self, entry: HistoryEntry) -> None:
        """Reload run setup from history."""
        self._log(f"Reloading Setup: {entry.executable} (start={entry.start_time}, stop={entry.stop_time})", LogLevel.INFO)

    # -- System -----------------------------------------------------

    def _apply_theme(self) -> None:
        """Apply the current theme to the window and update UI text."""
        self._theme_mgr.apply(self)
        # Update the toolbar toggle text
        if self._theme_mgr.is_dark():
            self._theme_act.setText("\U0001f319 Dark")
        else:
            self._theme_act.setText("\u2600\ufe0f Light")

    def _toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        self._theme_mgr.toggle()
        self._apply_theme()
        self._log(f"Theme: {'Dark' if self._theme_mgr.is_dark() else 'Light'} mode", LogLevel.INFO)
        self._save_settings()

    def _set_running_state(self, running: bool) -> None:
        self._run_act.setEnabled(not running)
        self._stop_act.setEnabled(running)
        self._control_panel.set_running_state(running)

    def _update_status(self, text: str, color: str = None) -> None:
        self._status_label.setText(text)
        # Status bar text is always white per QSS, so inline color
        # only for the widget-specific label when needed
        if color:
            self._status_label.setStyleSheet(f"color: {color}; background: transparent;")

    def _log(self, text: str, level: LogLevel) -> None:
        self._console_panel.append_text(self._logger.log(text, level))

    def _save_settings(self) -> None:
        data = {
            "exe_path": self._exe_path,
            "theme": self._theme_mgr.current_theme,
        }
        try:
            _SETTINGS_FILE.write_text(json.dumps(data, indent=2))
        except OSError: pass

    def _load_settings(self) -> None:
        if not _SETTINGS_FILE.exists(): return
        try:
            data = json.loads(_SETTINGS_FILE.read_text())
            path = data.get("exe_path", "")
            if path and Path(path).exists():
                self._exe_path = path
                self._control_panel.update_exe_path(path)
            theme = data.get("theme", "dark")
            # Also support legacy "dark_mode" boolean key
            if "dark_mode" in data and "theme" not in data:
                theme = "dark" if data["dark_mode"] else "light"
            self._theme_mgr.switch_theme(theme)
        except (json.JSONDecodeError, OSError): pass

    def _auto_load_model(self) -> None:
        """Auto-detect and load an executable from the model/ directory.

        If no executable has been loaded from settings, scans the
        model/ folder for .exe files and loads the first one found.
        This allows evaluators to run the app without manual setup.
        """
        if self._exe_path:
            return  # Already loaded from settings

        if not _MODEL_DIR.is_dir():
            return

        import platform
        for candidate in sorted(_MODEL_DIR.iterdir()):
            if not candidate.is_file():
                continue
            # Windows: look for .exe files
            if platform.system() == "Windows" and candidate.suffix.lower() == ".exe":
                self._exe_path = str(candidate.resolve())
                break
            # Linux/macOS: look for files without extension that are executable
            if platform.system() != "Windows" and not candidate.suffix:
                import os
                if os.access(candidate, os.X_OK):
                    self._exe_path = str(candidate.resolve())
                    break

        if self._exe_path:
            self._control_panel.update_exe_path(self._exe_path)
            self._log(
                f"Auto-loaded model: {Path(self._exe_path).name}",
                LogLevel.SUCCESS,
            )
            self._save_settings()
