"""
Parameter Sweep Runner for batch simulation execution.

Runs multiple simulations sequentially (one start time, multiple stop
times) in a background thread. Tracks progress, stores per-run results,
and detects CSV output files after each run completes.
"""

import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from core.validator import SimulationValidator


@dataclass
class SweepRunResult:
    """Result data from a single run within a parameter sweep."""

    index: int
    start_time: int
    stop_time: int
    return_code: int = -1
    elapsed: float = 0.0
    csv_path: str = ""
    status: str = "Pending"
    error_message: str = ""


class SweepRunner(QThread):
    """Executes multiple simulations sequentially in a background thread.

    Given a single start time and a list of stop times, runs each
    combination as a separate subprocess. Emits signals for real-time
    progress updates so the GUI stays responsive.

    Signals:
        progress_update: (current_index, total, message) — per-run progress.
        run_stdout: (line) — stdout from the current subprocess.
        run_completed: (SweepRunResult) — emitted after each run finishes.
        sweep_finished: (list[SweepRunResult]) — emitted when all runs done.
        sweep_error: (message) — emitted on fatal/unrecoverable error.
    """

    progress_update = pyqtSignal(int, int, str)
    run_stdout = pyqtSignal(str)
    run_completed = pyqtSignal(object)  # SweepRunResult
    sweep_finished = pyqtSignal(object)  # list[SweepRunResult]
    sweep_error = pyqtSignal(str)

    def __init__(
        self,
        executable_path: str,
        start_time: int,
        stop_times: list[int],
        parent=None,
    ):
        """Initialize the sweep runner.

        Args:
            executable_path: Absolute path to the simulation executable.
            start_time: The single start time for all runs.
            stop_times: List of stop times to sweep through.
            parent: Optional QObject parent.
        """
        super().__init__(parent)
        self._executable = Path(executable_path)
        self._start_time = start_time
        self._stop_times = stop_times
        self._results: list[SweepRunResult] = []

    @property
    def total_runs(self) -> int:
        """Return the number of simulations to execute."""
        return len(self._stop_times)

    @property
    def results(self) -> list[SweepRunResult]:
        """Return all collected run results."""
        return list(self._results)

    @staticmethod
    def parse_stop_times(text: str) -> list[int]:
        """Parse a comma-separated string of stop times.

        Args:
            text: Raw input string, e.g. "1, 2, 3, 4".

        Returns:
            Sorted list of unique integer stop times.

        Raises:
            ValueError: If any token is not a valid integer.
        """
        tokens = [t.strip() for t in text.split(",") if t.strip()]
        if not tokens:
            raise ValueError("No stop times provided.")

        values: list[int] = []
        for token in tokens:
            try:
                values.append(int(token))
            except ValueError:
                raise ValueError(
                    f"'{token}' is not a valid integer stop time."
                )

        # Remove duplicates and sort
        return sorted(set(values))

    @staticmethod
    def validate_sweep(
        start_time: int, stop_times: list[int]
    ) -> list[str]:
        """Validate all (start, stop) pairs against simulation rules.

        Args:
            start_time: The single start time.
            stop_times: List of stop times to validate.

        Returns:
            List of error messages (empty if all valid).
        """
        errors: list[str] = []
        for stop in stop_times:
            result = SimulationValidator.validate_time_inputs(
                str(start_time), str(stop)
            )
            if not result.is_valid:
                errors.append(f"stop={stop}: {result.message}")
        return errors

    def _build_command(self, stop_time: int) -> list[str]:
        """Construct the command for a specific stop time."""
        override = (
            f"-override=startTime={self._start_time},"
            f"stopTime={stop_time}"
        )
        return [str(self._executable), override]

    def _detect_csv_after_run(self) -> str:
        """Scan executable directory for the most recently modified CSV.

        Returns:
            Path to the newest CSV file, or empty string if none found.
        """
        exe_dir = self._executable.parent
        csv_files: list[Path] = []
        for f in exe_dir.iterdir():
            if (
                f.is_file()
                and f.suffix.lower() == ".csv"
                and not f.name.startswith(".")
            ):
                csv_files.append(f)

        if not csv_files:
            return ""

        # Return the most recently modified
        csv_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return str(csv_files[0].resolve())

    def run(self) -> None:
        """Execute all simulations sequentially.

        This method runs in a separate thread. For each stop time,
        it spawns a subprocess, streams output, and records results.
        """
        total = len(self._stop_times)
        self._results.clear()

        for idx, stop_time in enumerate(self._stop_times):
            run_num = idx + 1
            result = SweepRunResult(
                index=idx,
                start_time=self._start_time,
                stop_time=stop_time,
            )

            self.progress_update.emit(
                run_num,
                total,
                f"Running simulation {run_num} of {total}  "
                f"(start={self._start_time}, stop={stop_time})",
            )

            cmd = self._build_command(stop_time)
            start_wall = time.perf_counter()

            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=str(self._executable.parent),
                )

                # Stream stdout
                if process.stdout:
                    for line in process.stdout:
                        stripped = line.rstrip("\n\r")
                        if stripped:
                            self.run_stdout.emit(stripped)

                # Capture stderr
                if process.stderr:
                    for line in process.stderr:
                        stripped = line.rstrip("\n\r")
                        if stripped:
                            self.run_stdout.emit(f"[STDERR] {stripped}")

                return_code = process.wait()
                elapsed = time.perf_counter() - start_wall

                result.return_code = return_code
                result.elapsed = elapsed
                result.status = "Success" if return_code == 0 else "Failed"

                # Detect CSV output
                result.csv_path = self._detect_csv_after_run()

            except FileNotFoundError:
                result.elapsed = time.perf_counter() - start_wall
                result.status = "Failed"
                result.error_message = (
                    f"Executable not found: {self._executable}"
                )
            except PermissionError:
                result.elapsed = time.perf_counter() - start_wall
                result.status = "Failed"
                result.error_message = (
                    f"Permission denied: {self._executable}"
                )
            except OSError as exc:
                result.elapsed = time.perf_counter() - start_wall
                result.status = "Failed"
                result.error_message = f"OS error: {exc}"

            self._results.append(result)
            self.run_completed.emit(result)

        self.sweep_finished.emit(self._results)
