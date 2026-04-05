"""
Central workspace for simulation visualization.
Matplotlib-based plot area with theme-reactive styling.
Automatically redraws when the theme is switched.
"""

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.result_parser import CsvPreview, get_numeric_columns, get_column_data
from gui.theme_manager import ThemeManager


class PlotPanel(QWidget):
    """Main visualization workspace with theme-reactive matplotlib plots."""

    plotRequested = pyqtSignal(str, str)  # (x_col, y_col)

    def __init__(self, theme_mgr: ThemeManager, parent: QWidget | None = None):
        super().__init__(parent)
        self._theme_mgr = theme_mgr
        self._preview: CsvPreview | None = None
        self._init_ui()

        # React to theme changes
        self._theme_mgr.themeChanged.connect(self._on_theme_changed)

    def _init_ui(self) -> None:
        """Construct the plot layout with workspace controls and canvas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # -- Workspace Header / Toolbar --
        header = QWidget()
        header.setObjectName("panelHeader")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(8, 2, 8, 2)
        h_layout.setSpacing(10)

        h_layout.addWidget(QLabel("\U0001f4c8"))
        title = QLabel("WORKSPACE")
        title.setObjectName("panelTitle")
        h_layout.addWidget(title)
        h_layout.addStretch()

        # -- Axis Selectors --
        h_layout.addWidget(QLabel("X:"))
        self._x_combo = QComboBox()
        self._x_combo.setMinimumWidth(120)
        h_layout.addWidget(self._x_combo)

        h_layout.addWidget(QLabel("Y:"))
        self._y_combo = QComboBox()
        self._y_combo.setMinimumWidth(120)
        h_layout.addWidget(self._y_combo)

        self._plot_btn = QPushButton("Plot")
        self._plot_btn.setObjectName("workspacePlotBtn")
        self._plot_btn.clicked.connect(self._on_plot_click)
        h_layout.addWidget(self._plot_btn)

        self._clear_btn = QPushButton("Reset")
        self._clear_btn.setObjectName("workspaceClearBtn")
        self._clear_btn.clicked.connect(self.reset)
        h_layout.addWidget(self._clear_btn)

        layout.addWidget(header)

        # -- Plot Area --
        self._display_container = QWidget()
        self._display_layout = QVBoxLayout(self._display_container)
        self._display_layout.setContentsMargins(0, 0, 0, 0)

        # Matplotlib Canvas
        tc = self._theme_mgr.get_plot_colors()
        self._figure = Figure(figsize=(5, 4), dpi=100)
        self._figure.patch.set_facecolor(tc["bg"])
        self._canvas = FigureCanvas(self._figure)
        
        # Navigation toolbar
        self._toolbar = NavigationToolbar(self._canvas, self)
        
        # Placeholder Label
        self._placeholder = QLabel("Run a simulation to visualize results")
        self._placeholder.setObjectName("plotPlaceholder")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._display_layout.addWidget(self._placeholder)
        self._display_layout.addWidget(self._toolbar)
        self._display_layout.addWidget(self._canvas, 1)

        # Hide toolbar and canvas initially
        self._toolbar.setVisible(False)
        self._canvas.setVisible(False)

        layout.addWidget(self._display_container, 1)

    def load_preview(self, preview: CsvPreview) -> None:
        """Load and plot CSV preview data."""
        self._preview = preview
        numeric_cols = get_numeric_columns(preview)
        
        self._x_combo.clear()
        self._y_combo.clear()
        
        if not numeric_cols:
            self.reset()
            self._placeholder.setText("No plottable numeric columns found in this file.")
            self._placeholder.setVisible(True)
            return

        self._x_combo.addItems(numeric_cols)
        self._y_combo.addItems(numeric_cols)
        
        # Auto-select "time"
        for tc_name in ("time", "Time", "TIME", "t"):
            if tc_name in numeric_cols:
                self._x_combo.setCurrentIndex(numeric_cols.index(tc_name))
                break
        
        if len(numeric_cols) > 1:
            y_idx = 1 if self._x_combo.currentIndex() == 0 else 0
            self._y_combo.setCurrentIndex(y_idx)

        # Reveal plot
        self._placeholder.setVisible(False)
        self._toolbar.setVisible(True)
        self._canvas.setVisible(True)
        
        self.draw_plot(self._x_combo.currentText(), self._y_combo.currentText())

    def draw_plot(self, x_col: str, y_col: str) -> None:
        """Plot the chosen columns on the canvas."""
        if not self._preview:
            return
        
        x_data = get_column_data(self._preview, x_col)
        y_data = get_column_data(self._preview, y_col)
        
        if not x_data or not y_data:
            return

        min_len = min(len(x_data), len(y_data))
        x_data = x_data[:min_len]
        y_data = y_data[:min_len]

        tc = self._theme_mgr.get_plot_colors()
        self._figure.clear()
        self._figure.patch.set_facecolor(tc["bg"])
        ax = self._figure.add_subplot(111)

        ax.set_facecolor(tc["bg"])
        ax.tick_params(colors=tc["text_dim"], which="both", labelsize=8)
        ax.xaxis.label.set_color(tc["text"])
        ax.yaxis.label.set_color(tc["text"])
        ax.title.set_color(tc["title"])
        
        for spine in ax.spines.values():
            spine.set_color(tc["border"])
        
        ax.grid(True, color=tc["grid"], linestyle="--", linewidth=0.5, alpha=0.6)

        line_color = tc["line"]

        ax.plot(x_data, y_data, color=line_color, linewidth=1.8, label=y_col,
                marker="o", markersize=2, markeredgecolor=line_color,
                markerfacecolor=tc["marker_bg"], alpha=0.95)
        ax.fill_between(x_data, y_data, alpha=0.08, color=line_color)

        ax.set_xlabel(x_col, fontsize=10, fontweight="bold")
        ax.set_ylabel(y_col, fontsize=10, fontweight="bold")
        ax.set_title(f"{y_col}  vs  {x_col}", fontsize=12, fontweight="bold", pad=10)
        ax.legend(facecolor=tc["card"], edgecolor=tc["border"],
                  labelcolor=tc["text"], loc="best", fontsize=8, framealpha=0.9)

        self._figure.tight_layout(pad=1.2)
        self._canvas.draw()

    def _on_plot_click(self) -> None:
        """Handle context plot click."""
        self.draw_plot(self._x_combo.currentText(), self._y_combo.currentText())

    def _on_theme_changed(self, theme: str) -> None:
        """Redraw the plot when the theme changes."""
        if self._preview and self._canvas.isVisible():
            self.draw_plot(self._x_combo.currentText(), self._y_combo.currentText())
        else:
            # Update placeholder / empty canvas background
            tc = self._theme_mgr.get_plot_colors()
            self._figure.patch.set_facecolor(tc["bg"])
            self._canvas.draw()

    def reset(self) -> None:
        """Clear the plot and show placeholder."""
        self._preview = None
        self._x_combo.clear()
        self._y_combo.clear()
        self._toolbar.setVisible(False)
        self._canvas.setVisible(False)
        self._placeholder.setText("Run a simulation to visualize results")
        self._placeholder.setVisible(True)
