"""
OpenModelica Simulation Runner — Entry Point.

Launches the PyQt6 desktop application for executing
OpenModelica-generated simulation executables.
"""

import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> None:
    """Initialize the application and show the main window."""
    app = QApplication(sys.argv)
    app.setApplicationName("OpenModelica Simulation Runner")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
