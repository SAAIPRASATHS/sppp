"""
Premium custom numeric input component with distinct [+] and [-] buttons.

Designed to replace standard QSpinBox for better UI control, specific
alignment, and a more interactive UX consistent with premium dashboards.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class NumericInput(QWidget):
    """Custom control: [-] [ 10 ] [+]

    Signals:
        valueChanged (int): Emitted whenever the numeric value changes.
    """

    valueChanged = pyqtSignal(int)

    def __init__(
        self,
        value: int = 0,
        min_val: int = 0,
        max_val: int = 100,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._min_val = min_val
        self._max_val = max_val
        self._current_value = value
        self._init_ui()

    def _init_ui(self) -> None:
        """Construct the horizontal UI layout."""
        self.setMinimumHeight(44)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # -- Decrement Button --
        self._minus_btn = QPushButton("-")
        self._minus_btn.setObjectName("minusBtn")
        self._minus_btn.setFixedSize(40, 40)
        self._minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._minus_btn.clicked.connect(self._on_decrement)
        layout.addWidget(self._minus_btn)

        # -- Central Input Field --
        self._edit = QLineEdit(str(self._current_value))
        self._edit.setObjectName("numericEdit")
        self._edit.setFixedSize(70, 40)
        self._edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._edit.setValidator(QIntValidator(self._min_val, self._max_val))
        self._edit.editingFinished.connect(self._on_editing_finished)
        layout.addWidget(self._edit)

        # -- Increment Button --
        self._plus_btn = QPushButton("+")
        self._plus_btn.setObjectName("plusBtn")
        self._plus_btn.setFixedSize(40, 40)
        self._plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._plus_btn.clicked.connect(self._on_increment)
        layout.addWidget(self._plus_btn)



    # -- Public API (Matched to QSpinBox) ----------------------------

    def value(self) -> int:
        """Get the current numeric value."""
        return self._current_value

    def setValue(self, val: int) -> None:
        """Set the value programmatically (clamped to range)."""
        val = max(self._min_val, min(val, self._max_val))
        if val != self._current_value:
            self._current_value = val
            self._edit.setText(str(val))
            self.valueChanged.emit(val)

    def setRange(self, min_val: int, max_val: int) -> None:
        """Update the range constraint."""
        self._min_val = min_val
        self._max_val = max_val
        self._edit.setValidator(QIntValidator(min_val, max_val))
        # Ensure current value is still valid
        self.setValue(self._current_value)

    # -- Internal Handlers -------------------------------------------

    def _on_increment(self) -> None:
        if self._current_value < self._max_val:
            self.setValue(self._current_value + 1)

    def _on_decrement(self) -> None:
        if self._current_value > self._min_val:
            self.setValue(self._current_value - 1)

    def _on_editing_finished(self) -> None:
        try:
            val = int(self._edit.text())
            self.setValue(val)
        except ValueError:
            self._edit.setText(str(self._current_value))
