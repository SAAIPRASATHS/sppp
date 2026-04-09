"""
Subprocess execution handler for OpenModelica simulations.

Runs the selected executable with override parameters in a
separate thread to keep the GUI responsive. Streams output
line-by-line and tracks execution duration.
"""

import subprocess
import time
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal


class SimulationRunner(QThread):
    """Runs an OpenModelica executable in a background thread.

    Emits signals for stdout lines, stderr lines, completion,
    execution time, and errors so the GUI can update in real time.

    Signals:
        stdout_ready: Emitted for each line of standard output.
        stderr_ready: Emitted for each line of standard error.
        finished_signal: Emitted when process completes (return code).
        error_occurred: Emitted if the process fails to start.
        execution_time: Emitted with elapsed seconds on completion.
    """

    stdout_ready = pyqtSignal(str)
    stderr_ready = pyqtSignal(str)
    finished_signal = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    execution_time = pyqtSignal(float)

    def __init__(
        self,
        executable_path: str,
        start_time: int,
        stop_time: int,
        parent=None,
    ):
        """Initialize the runner.

        Args:
            executable_path: Absolute path to the simulation executable.
            start_time: Simulation start time parameter.
            stop_time: Simulation stop time parameter.
            parent: Optional QObject parent.
        """
        super().__init__(parent)
        self._executable = Path(executable_path)
        self._start_time = start_time
        self._stop_time = stop_time
        self._elapsed: float = 0.0

    @property
    def elapsed_seconds(self) -> float:
        """Return the last measured execution duration."""
        return self._elapsed

    @property
    def working_directory(self) -> str:
        """Return the executable's parent directory."""
        return str(self._executable.parent)

    def build_command(self) -> list[str]:
        """Construct the command-line argument list.

        Returns:
            List of strings forming the full command.
        """
        override_arg = (
            f"-override=startTime={self._start_time},"
            f"stopTime={self._stop_time}"
        )
        return [str(self._executable), override_arg]

    def get_command_preview(self) -> str:
        """Return a human-readable command string for preview.

        Returns:
            The command as it would appear in a terminal.
        """
        return " ".join(self.build_command())

    def run(self) -> None:
        """Execute the simulation subprocess.

        This method runs in a separate thread. It reads stdout and
        stderr line-by-line, emits signals for each line, and tracks
        total execution time.
        """
        start_wall = time.perf_counter()
        try:
            process = subprocess.Popen(
                self.build_command(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self._executable.parent),
            )

            # Stream stdout line-by-line in real time
            if process.stdout:
                for line in process.stdout:
                    stripped = line.rstrip("\n\r")
                    if stripped:
                        self.stdout_ready.emit(stripped)

            # Stream stderr line-by-line
            if process.stderr:
                for line in process.stderr:
                    stripped = line.rstrip("\n\r")
                    if stripped:
                        self.stderr_ready.emit(stripped)

            return_code = process.wait()
            self._elapsed = time.perf_counter() - start_wall
            self.execution_time.emit(self._elapsed)
            self.finished_signal.emit(return_code)

        except FileNotFoundError:
            self._elapsed = time.perf_counter() - start_wall
            self.execution_time.emit(self._elapsed)
            self.error_occurred.emit(
                f"Executable not found: {self._executable}"
            )
        except PermissionError:
            self._elapsed = time.perf_counter() - start_wall
            self.execution_time.emit(self._elapsed)
            self.error_occurred.emit(
                f"Permission denied: {self._executable}\n"
                "Ensure the file has execute permissions."
            )
        except OSError as exc:
            self._elapsed = time.perf_counter() - start_wall
            self.execution_time.emit(self._elapsed)
            self.error_occurred.emit(
                f"OS error while running simulation: {exc}"
            )
