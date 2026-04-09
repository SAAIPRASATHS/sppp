"""
Compare Runs view for side-by-side simulation result analysis.

Provides a UI to select multiple historical simulation runs and
overlay their outputs on a single matplotlib graph for comparison.
Uses distinct colors and labels for clarity. Theme-aware via ThemeManager.
"""

from pathlib import Path

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.history_manager import HistoryManager, HistoryEntry
from core.result_parser import (
    CsvPreview,
    get_column_data,
    get_numeric_columns,
    parse_csv_preview,
)
from gui.theme_manager import ThemeManager

# Premium plot color palette (12 distinct colors)
_COMPARE_COLORS = [
    "#58a6ff", "#3fb950", "#f85149", "#d29922",
    "#bc8cff", "#39d2c0", "#f78166", "#79c0ff",
    "#a371f7", "#56d364", "#ff7b72", "#e3b341",
]


class CompareView(QWidget):
    """Widget for comparing multiple simulation runs on a single plot.

    Features:
    - Checkbox list of history entries with valid CSV output files
    - Shared X/Y axis column selectors
    - Overlay plot with distinct colors and clear legend
    - Refresh and clear controls
    - Theme-aware matplotlib styling via ThemeManager
    """

    def __init__(
        self,
        history_manager: HistoryManager,
        theme_mgr: ThemeManager | None = None,
        parent: QWidget | None = None,
    ):
        """Initialize the compare view.

        Args:
            history_manager: Shared HistoryManager for accessing run data.
            theme_mgr: Optional ThemeManager for plot colors.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._history_mgr = history_manager
        self._theme_mgr = theme_mgr
        self._loaded_previews: dict[int, CsvPreview] = {}
        self._init_ui()

    def _get_colors(self) -> dict[str, str]:
        """Get the current plot colors from ThemeManager."""
        if self._theme_mgr:
            return self._theme_mgr.get_plot_colors()
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

    def _init_ui(self) -> None:
        """Build the compare view layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 10, 6, 6)
        layout.setSpacing(6)

        # -- Info banner --
        info = QLabel(
            "\U0001f504  Select two or more runs with CSV outputs, choose "
            "columns, then click Compare to overlay results."
        )
        info.setObjectName("hintLabel")
        info.setWordWrap(True)
        layout.addWidget(info)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # =============== LEFT: Run Selection ===============
        left_group = QGroupBox("Available Runs")
        left_layout = QVBoxLayout(left_group)

        self._run_list = QListWidget()
        self._run_list.setObjectName("compareRunList")
        self._run_list.setToolTip(
            "Check the runs you want to compare"
        )
        left_layout.addWidget(self._run_list)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        refresh_btn = QPushButton("\U0001f504  Refresh")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setToolTip("Reload available runs from history")
        refresh_btn.clicked.connect(self.refresh_runs)
        btn_row.addWidget(refresh_btn)

        select_all_btn = QPushButton("Select All")
        select_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        select_all_btn.setToolTip("Check all available runs")
        select_all_btn.clicked.connect(self._select_all)
        btn_row.addWidget(select_all_btn)

        deselect_btn = QPushButton("Deselect All")
        deselect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        deselect_btn.setToolTip("Uncheck all runs")
        deselect_btn.clicked.connect(self._deselect_all)
        btn_row.addWidget(deselect_btn)

        left_layout.addLayout(btn_row)
        splitter.addWidget(left_group)

        # =============== RIGHT: Plot Area ===============
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        # -- Column selectors --
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
        self._x_combo.setToolTip("Horizontal axis column for comparison")
        controls_layout.addWidget(self._x_combo)

        y_label = QLabel("Y-Axis:")
        y_label.setObjectName("fieldLabel")
        controls_layout.addWidget(y_label)

        self._y_combo = QComboBox()
        self._y_combo.setMinimumWidth(140)
        self._y_combo.setObjectName("plotCombo")
        self._y_combo.setToolTip("Vertical axis column for comparison")
        controls_layout.addWidget(self._y_combo)

        self._compare_btn = QPushButton("\U0001f504  Compare")
        self._compare_btn.setObjectName("compareBtn")
        self._compare_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._compare_btn.setToolTip(
            "Overlay selected runs on a single graph"
        )
        self._compare_btn.clicked.connect(self._on_compare)
        controls_layout.addWidget(self._compare_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("clearPlotBtn")
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.setToolTip("Clear the comparison graph")
        self._clear_btn.clicked.connect(self._on_clear)
        controls_layout.addWidget(self._clear_btn)

        controls_layout.addStretch()
        right_layout.addWidget(controls)

        # -- Matplotlib Figure --
        tc = self._get_colors()
        self._figure = Figure(figsize=(7, 4), dpi=100)
        self._figure.patch.set_facecolor(tc["bg"])
        self._canvas = FigureCanvas(self._figure)
        self._canvas.setMinimumHeight(300)

        self._toolbar = NavigationToolbar(self._canvas, self)
        right_layout.addWidget(self._toolbar)
        right_layout.addWidget(self._canvas, 1)

        # -- Status --
        self._status_label = QLabel(
            "Select runs and click Compare to overlay results."
        )
        self._status_label.setObjectName("plotStatus")
        right_layout.addWidget(self._status_label)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout.addWidget(splitter)

    # ==========================================================
    #  PUBLIC API
    # ==========================================================

    def refresh_runs(self) -> None:
        """Reload the list of comparable runs from history."""
        self._run_list.clear()
        self._loaded_previews.clear()
        self._x_combo.clear()
        self._y_combo.clear()

        entries = self._history_mgr.get_entries_with_files()
        if not entries:
            self._status_label.setText(
                "No runs with CSV output files found. "
                "Run a simulation first, then return here."
            )
            return

        columns_set: set[str] | None = None

        for idx, entry in enumerate(entries):
            preview = parse_csv_preview(entry.output_file, max_rows=50)
            if preview.error or not preview.headers:
                continue

            self._loaded_previews[idx] = preview

            numeric = set(get_numeric_columns(preview))
            if columns_set is None:
                columns_set = numeric
            else:
                columns_set = columns_set.intersection(numeric)

            csv_name = Path(entry.output_file).name
            label = (
                f"start={entry.start_time} stop={entry.stop_time}  "
                f"{entry.duration:.2f}s  \u2502  {csv_name}  "
                f"[{entry.timestamp}]"
            )
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, idx)

            checkbox = QCheckBox(label)
            checkbox.setObjectName("compareCheckbox")
            checkbox.setStyleSheet("padding: 2px 5px;")
            
            # Ensure the row is tall enough for the text
            sh = checkbox.sizeHint()
            item.setSizeHint(QSize(sh.width(), sh.height() + 10))

            self._run_list.addItem(item)
            self._run_list.setItemWidget(item, checkbox)

        if columns_set:
            shared_cols = sorted(columns_set)
            self._x_combo.addItems(shared_cols)
            self._y_combo.addItems(shared_cols)

            # Aggressive auto-select "time" for X if available
            found_x = False
            time_variants = ("time", "t", "Time", "TIME", "t (s)", "time (s)", "Time [s]")
            
            # Exact matching first
            for tc_name in time_variants:
                if tc_name in shared_cols:
                    self._x_combo.setCurrentIndex(shared_cols.index(tc_name))
                    found_x = True
                    break
            
            # Substring matching if still not found
            if not found_x:
                for idx, col in enumerate(shared_cols):
                    if "time" in col.lower() or col.lower() == "t":
                        self._x_combo.setCurrentIndex(idx)
                        found_x = True
                        break

            # Y defaults to something different from X
            if len(shared_cols) > 1:
                x_idx = self._x_combo.currentIndex()
                # Try to pick a column that is NOT X
                y_idx = 1 if x_idx == 0 else 0
                # If there are many columns, avoid picking 'time' for Y too
                if len(shared_cols) > 2 and y_idx == x_idx:
                    y_idx = 2
                self._y_combo.setCurrentIndex(y_idx)

            self._status_label.setText(
                f"{self._run_list.count()} comparable runs found  \u2502  "
                f"{len(shared_cols)} shared numeric columns."
            )
        else:
            self._status_label.setText(
                "No shared numeric columns found across runs."
            )

    # ==========================================================
    #  INTERNAL HANDLERS
    # ==========================================================

    def _get_selected_indices(self) -> list[int]:
        """Return preview indices of all checked runs."""
        selected: list[int] = []
        for row in range(self._run_list.count()):
            item = self._run_list.item(row)
            widget = self._run_list.itemWidget(item)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                idx = item.data(Qt.ItemDataRole.UserRole)
                if idx in self._loaded_previews:
                    selected.append(idx)
        return selected

    def _select_all(self) -> None:
        """Check all items in the run list."""
        for row in range(self._run_list.count()):
            item = self._run_list.item(row)
            widget = self._run_list.itemWidget(item)
            if isinstance(widget, QCheckBox):
                widget.setChecked(True)

    def _deselect_all(self) -> None:
        """Uncheck all items in the run list."""
        for row in range(self._run_list.count()):
            item = self._run_list.item(row)
            widget = self._run_list.itemWidget(item)
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)

    def _on_compare(self) -> None:
        """Overlay selected runs on a single plot."""
        selected = self._get_selected_indices()
        if len(selected) < 2:
            QMessageBox.information(
                self,
                "Compare Runs",
                "Please select at least 2 runs to compare.",
            )
            return

        x_col = self._x_combo.currentText()
        y_col = self._y_combo.currentText()
        if not x_col or not y_col:
            QMessageBox.information(
                self,
                "Compare Runs",
                "Please select both X and Y axis columns.",
            )
            return

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
            linewidth=0.6, alpha=0.8,
        )

        plotted = 0
        entries = self._history_mgr.get_entries_with_files()

        for sel_idx, preview_idx in enumerate(selected):
            preview = self._loaded_previews.get(preview_idx)
            if not preview:
                continue

            x_data = get_column_data(preview, x_col)
            y_data = get_column_data(preview, y_col)
            if not x_data or not y_data:
                continue

            min_len = min(len(x_data), len(y_data))
            x_data = x_data[:min_len]
            y_data = y_data[:min_len]

            color = _COMPARE_COLORS[sel_idx % len(_COMPARE_COLORS)]

            entry = (
                entries[preview_idx]
                if preview_idx < len(entries)
                else None
            )
            if entry:
                label = (
                    f"start={entry.start_time} stop={entry.stop_time} "
                    f"({entry.duration:.1f}s)"
                )
            else:
                label = f"Run {sel_idx + 1}"

            ax.plot(
                x_data, y_data,
                color=color,
                linewidth=2.0,
                marker="o",
                markersize=3,
                markeredgecolor=color,
                markerfacecolor=tc["marker_bg"],
                alpha=0.9,
                label=label,
            )
            plotted += 1

        if plotted == 0:
            self._status_label.setText(
                "No valid data found in selected runs."
            )
            self._canvas.draw()
            return

        ax.set_xlabel(x_col, fontsize=11, fontweight="bold")
        ax.set_ylabel(y_col, fontsize=11, fontweight="bold")
        ax.set_title(
            f"Comparison: {y_col}  vs  {x_col}  "
            f"({plotted} runs)",
            fontsize=13, fontweight="bold", pad=12,
        )
        ax.legend(
            facecolor=tc["card"],
            edgecolor=tc["border"],
            labelcolor=tc["text"],
            fontsize=9,
            framealpha=0.9,
            loc="best",
        )

        self._figure.tight_layout(pad=1.5)
        self._canvas.draw()

        self._status_label.setText(
            f"Compared {plotted} runs  \u2502  {y_col} vs {x_col}"
        )

    def _on_clear(self) -> None:
        """Clear the comparison plot."""
        tc = self._get_colors()
        self._figure.clear()
        self._figure.patch.set_facecolor(tc["bg"])
        self._canvas.draw()
        self._status_label.setText("Plot cleared.")
