"""
OpenModelica Simulation Studio — Application Entry Point.

This module serves as the primary entry point for the Simulation Studio.
It initializes the Qt application environment, sets project metadata,
and launches the main graphical interface.

Application: OpenModelica Simulation Studio
Framework: PyQt6
Author: FOSSEE Summer Fellowship 2026 Submission
"""

import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> None:
    """
    Initialize the application, configure global settings, and show the main window.

    This function sets up the QApplication instance, which manages the application's
    control flow and main settings. It then instantiates the MainWindow and enters
    the main event loop.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("OpenModelica Simulation Runner")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
