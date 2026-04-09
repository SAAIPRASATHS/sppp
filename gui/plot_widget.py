"""
Matplotlib-based plot widget for displaying simulation results.

Embeds a matplotlib figure inside a PyQt6 widget with column
selection, zoom/pan toolbar, and theme-aware styling via ThemeManager.
"""

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
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


def get_plot_colors_from_theme_mgr(theme_mgr) -> dict[str, str]:
    """Get plot colors from ThemeManager if available.

    Args:
        theme_mgr: A ThemeManager instance, or None.

    Returns:
        Dict of color tokens for matplotlib styling.
    """
    if theme_mgr is not None:
        return theme_mgr.get_plot_colors()
    # Fallback dark colors
    return {
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


class PlotWidget(QWidget):
    """Embeddable matplotlib plot with column selection controls.

    Displays simulation CSV data as line charts with an interactive
    toolbar for zoom, pan, and save. Uses ThemeManager for colors.
    """

    def __init__(self, theme_mgr=None, parent: QWidget | None = None):
        super().__init__(parent)
        self._theme_mgr = theme_mgr
        self._preview: CsvPreview | None = None
        self._numeric_cols: list[str] = []
        self._init_ui()

    def _get_colors(self) -> dict[str, str]:
        """Get the current theme colors."""
        return get_plot_colors_from_theme_mgr(self._theme_mgr)

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
        tc = self._get_colors()
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

        # Aggressive auto-select "time" for X if available
        found_x = False
        time_variants = ("time", "t", "Time", "TIME", "t (s)", "time (s)", "Time [s]")
        
        # Exact matching first
        for tc_name in time_variants:
            if tc_name in self._numeric_cols:
                self._x_combo.setCurrentIndex(self._numeric_cols.index(tc_name))
                found_x = True
                break
        
        # Substring matching if still not found
        if not found_x:
            for idx, col in enumerate(self._numeric_cols):
                if "time" in col.lower() or col.lower() == "t":
                    self._x_combo.setCurrentIndex(idx)
                    found_x = True
                    break

        # Y defaults to something different from X
        if len(self._numeric_cols) > 1:
            x_idx = self._x_combo.currentIndex()
            # Try to pick a column that is NOT X
            y_idx = 1 if x_idx == 0 else 0
            # If there are many columns, avoid picking 'time' for Y too
            if len(self._numeric_cols) > 2 and y_idx == x_idx:
                y_idx = 2
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
        tc = self._get_colors()
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
        tc = self._get_colors()
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

        line_color = tc.get("line", _PLOT_COLORS[0])

        ax.plot(
            x_data, y_data,
            color=line_color,
            linewidth=2.0,
            marker="o",
            markersize=3,
            markeredgecolor=line_color,
            markerfacecolor=tc["marker_bg"],
            alpha=0.95,
            label=y_col,
        )

        ax.fill_between(
            x_data, y_data,
            alpha=0.08,
            color=line_color,
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
        tc = self._get_colors()
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
