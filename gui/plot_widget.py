"""
Matplotlib-based plot widget for displaying simulation results.

Embeds a matplotlib figure inside a PyQt6 widget with column
selection, zoom/pan toolbar, and theme-aware styling.
"""

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.result_parser import CsvPreview, get_column_data, get_numeric_columns


# Premium plot color palette
_PLOT_COLORS = [
    "#58a6ff", "#3fb950", "#f85149", "#d29922",
    "#bc8cff", "#39d2c0", "#f78166", "#79c0ff",
]


def _get_theme_colors() -> dict[str, str]:
    """Detect current theme from the application and return plot colors.

    Returns a dict with keys: bg, card, grid, text, text_dim, border, title.
    """
    app = QApplication.instance()
    if app:
        ss = app.activeWindow()
        if ss:
            bg_color = ss.palette().color(ss.backgroundRole())
            lightness = bg_color.lightnessF()
            if lightness > 0.5:
                # Light theme
                return {
                    "bg": "#ffffff",
                    "card": "#f6f8fa",
                    "grid": "#d0d7de",
                    "text": "#1f2328",
                    "text_dim": "#656d76",
                    "border": "#d0d7de",
                    "title": "#1f2328",
                    "marker_bg": "#ffffff",
                }
    # Dark theme (default)
    return {
        "bg": "#0d1117",
        "card": "#161b22",
        "grid": "#21262d",
        "text": "#c9d1d9",
        "text_dim": "#8b949e",
        "border": "#30363d",
        "title": "#f0f6fc",
        "marker_bg": "#0d1117",
    }


class PlotWidget(QWidget):
    """Embeddable matplotlib plot with column selection controls.

    Displays simulation CSV data as line charts with an interactive
    toolbar for zoom, pan, and save. Auto-detects theme.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._preview: CsvPreview | None = None
        self._numeric_cols: list[str] = []
        self._init_ui()

    def _init_ui(self) -> None:
        """Build the plot layout with controls and canvas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # -- Controls Bar --
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(4, 4, 4, 4)
        controls_layout.setSpacing(8)

        x_label = QLabel("X-Axis:")
        x_label.setObjectName("fieldLabel")
        controls_layout.addWidget(x_label)

        self._x_combo = QComboBox()
        self._x_combo.setMinimumWidth(140)
        self._x_combo.setObjectName("plotCombo")
        self._x_combo.setToolTip("Select the column for the horizontal axis")
        controls_layout.addWidget(self._x_combo)

        y_label = QLabel("Y-Axis:")
        y_label.setObjectName("fieldLabel")
        controls_layout.addWidget(y_label)

        self._y_combo = QComboBox()
        self._y_combo.setMinimumWidth(140)
        self._y_combo.setObjectName("plotCombo")
        self._y_combo.setToolTip("Select the column for the vertical axis")
        controls_layout.addWidget(self._y_combo)

        self._plot_btn = QPushButton("\U0001f4c8  Plot Graph")
        self._plot_btn.setObjectName("plotBtn")
        self._plot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._plot_btn.setToolTip("Draw the graph with selected columns")
        self._plot_btn.clicked.connect(self._on_plot)
        controls_layout.addWidget(self._plot_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("clearPlotBtn")
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.setToolTip("Clear the current graph")
        self._clear_btn.clicked.connect(self._on_clear)
        controls_layout.addWidget(self._clear_btn)

        controls_layout.addStretch()
        layout.addWidget(controls)

        # -- Matplotlib Figure --
        tc = _get_theme_colors()
        self._figure = Figure(figsize=(6, 3.5), dpi=100)
        self._figure.patch.set_facecolor(tc["bg"])
        self._canvas = FigureCanvas(self._figure)
        self._canvas.setMinimumHeight(250)

        # Navigation toolbar
        self._toolbar = NavigationToolbar(self._canvas, self)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._canvas, 1)

        # -- Status --
        self._status_label = QLabel(
            "Load a CSV file with numeric data to enable plotting."
        )
        self._status_label.setObjectName("plotStatus")
        layout.addWidget(self._status_label)

    def load_csv_data(self, preview: CsvPreview) -> None:
        """Populate column selectors from parsed CSV data."""
        self._preview = preview
        self._numeric_cols = get_numeric_columns(preview)

        self._x_combo.clear()
        self._y_combo.clear()

        if not self._numeric_cols:
            self._status_label.setText(
                "No numeric columns found in this file. "
                "Graph requires numeric data (e.g. time, level, flow)."
            )
            self._show_no_data_message()
            return

        self._x_combo.addItems(self._numeric_cols)
        self._y_combo.addItems(self._numeric_cols)

        # Auto-select "time" for X if available
        for tc in ("time", "Time", "TIME", "t"):
            if tc in self._numeric_cols:
                self._x_combo.setCurrentIndex(self._numeric_cols.index(tc))
                break

        # Y defaults to second column
        if len(self._numeric_cols) > 1:
            y_idx = 1 if self._x_combo.currentIndex() == 0 else 0
            self._y_combo.setCurrentIndex(y_idx)

        self._status_label.setText(
            f"Ready \u2014 {len(self._numeric_cols)} numeric columns available. "
            "Select axes and click Plot."
        )

        # Auto-plot if we have good defaults
        if len(self._numeric_cols) >= 2:
            self._on_plot()

    def _show_no_data_message(self) -> None:
        """Display a styled message on the canvas when no numeric data."""
        tc = _get_theme_colors()
        self._figure.clear()
        ax = self._figure.add_subplot(111)
        ax.set_facecolor(tc["bg"])
        ax.text(
            0.5, 0.55,
            "No Numeric Data Available",
            transform=ax.transAxes,
            fontsize=16, fontweight="bold",
            color="#f85149",
            ha="center", va="center",
        )
        ax.text(
            0.5, 0.40,
            "This file does not contain plottable numeric columns.\n"
            "Load a simulation output CSV with columns like:\n"
            "time, tank1.level, tank2.level, valve.flow",
            transform=ax.transAxes,
            fontsize=10,
            color=tc["text_dim"],
            ha="center", va="center",
        )
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(tc["border"])
        self._canvas.draw()

    def _on_plot(self) -> None:
        """Plot the selected X vs Y columns."""
        if not self._preview or not self._numeric_cols:
            self._status_label.setText("No data loaded.")
            return

        x_col = self._x_combo.currentText()
        y_col = self._y_combo.currentText()
        if not x_col or not y_col:
            self._status_label.setText("Select both X and Y columns.")
            return

        x_data = get_column_data(self._preview, x_col)
        y_data = get_column_data(self._preview, y_col)
        if not x_data or not y_data:
            self._status_label.setText("Selected columns contain no valid data.")
            return

        min_len = min(len(x_data), len(y_data))
        x_data = x_data[:min_len]
        y_data = y_data[:min_len]

        # -- Theme-aware Draw --
        tc = _get_theme_colors()
        self._figure.clear()
        self._figure.patch.set_facecolor(tc["bg"])
        ax = self._figure.add_subplot(111)

        ax.set_facecolor(tc["bg"])
        ax.tick_params(colors=tc["text_dim"], which="both", labelsize=9)
        ax.xaxis.label.set_color(tc["text"])
        ax.yaxis.label.set_color(tc["text"])
        ax.title.set_color(tc["title"])
        for spine in ax.spines.values():
            spine.set_color(tc["border"])
        ax.grid(
            True, color=tc["grid"], linestyle="--",
            linewidth=0.6, alpha=0.8
        )

        ax.plot(
            x_data, y_data,
            color=_PLOT_COLORS[0],
            linewidth=2.0,
            marker="o",
            markersize=3,
            markeredgecolor=_PLOT_COLORS[0],
            markerfacecolor=tc["marker_bg"],
            alpha=0.95,
            label=y_col,
        )

        ax.fill_between(
            x_data, y_data,
            alpha=0.08,
            color=_PLOT_COLORS[0],
        )

        ax.set_xlabel(x_col, fontsize=11, fontweight="bold")
        ax.set_ylabel(y_col, fontsize=11, fontweight="bold")
        ax.set_title(
            f"{y_col}  vs  {x_col}",
            fontsize=13, fontweight="bold", pad=12,
        )
        ax.legend(
            facecolor=tc["card"],
            edgecolor=tc["border"],
            labelcolor=tc["text"],
            fontsize=9,
            framealpha=0.9,
        )

        self._figure.tight_layout(pad=1.5)
        self._canvas.draw()

        self._status_label.setText(
            f"Plotted {y_col} vs {x_col}  \u2502  {min_len} data points"
        )

    def _on_clear(self) -> None:
        """Clear the current plot."""
        tc = _get_theme_colors()
        self._figure.clear()
        self._figure.patch.set_facecolor(tc["bg"])
        self._canvas.draw()
        self._status_label.setText("Plot cleared.")

    def reset(self) -> None:
        """Reset to initial state."""
        self._preview = None
        self._numeric_cols.clear()
        self._x_combo.clear()
        self._y_combo.clear()
        self._on_clear()
        self._status_label.setText(
            "Load a CSV file with numeric data to enable plotting."
        )
