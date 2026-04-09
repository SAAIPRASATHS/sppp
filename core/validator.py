"""
Input validation logic for OpenModelica Simulation Runner.

Validates simulation parameters (start time, stop time) and
executable file selection before allowing execution.
"""

from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Holds the outcome of a validation check."""
    is_valid: bool
    message: str


class SimulationValidator:
    """Validates simulation parameters against OpenModelica constraints.

    Rules:
        - Start time must be an integer >= 0
        - Stop time must be an integer > start time
        - Both must satisfy: 0 <= start < stop < 5
    """

    MIN_TIME = 0
    MAX_TIME_EXCLUSIVE = 5

    @classmethod
    def validate_time_inputs(cls, start_text: str, stop_text: str) -> ValidationResult:
        """Validate start and stop time inputs.

        Args:
            start_text: Raw string from the start time input field.
            stop_text: Raw string from the stop time input field.

        Returns:
            ValidationResult with status and descriptive message.
        """
        # Check non-empty
        if not start_text.strip():
            return ValidationResult(False, "Start Time cannot be empty.")
        if not stop_text.strip():
            return ValidationResult(False, "Stop Time cannot be empty.")

        # Check integer conversion
        try:
            start = int(start_text.strip())
        except ValueError:
            return ValidationResult(False, f"Start Time '{start_text}' is not a valid integer.")

        try:
            stop = int(stop_text.strip())
        except ValueError:
            return ValidationResult(False, f"Stop Time '{stop_text}' is not a valid integer.")

        # Range checks
        if start < cls.MIN_TIME:
            return ValidationResult(
                False,
                f"Start Time must be ≥ {cls.MIN_TIME}. Got {start}."
            )

        if stop >= cls.MAX_TIME_EXCLUSIVE:
            return ValidationResult(
                False,
                f"Stop Time must be < {cls.MAX_TIME_EXCLUSIVE}. Got {stop}."
            )

        if start >= stop:
            return ValidationResult(
                False,
                f"Start Time ({start}) must be strictly less than Stop Time ({stop})."
            )

        return ValidationResult(True, "Parameters are valid.")

    @staticmethod
    def validate_file_path(path: str) -> ValidationResult:
        """Validate that a valid executable file path has been selected.

        Supports both Windows (.exe) and Linux/macOS (extensionless
        binaries with execute permission).

        Args:
            path: The executable file path string.

        Returns:
            ValidationResult with status and descriptive message.
        """
        if not path or not path.strip():
            return ValidationResult(
                False,
                "No executable file selected. Please choose a file.",
            )

        from pathlib import Path
        import platform
        import os

        file_path = Path(path)

        if not file_path.exists():
            return ValidationResult(False, f"File does not exist: {path}")

        if not file_path.is_file():
            return ValidationResult(
                False, "The selected path is a directory, not a file."
            )

        # Platform-specific executable checks
        if platform.system() == "Windows":
            if file_path.suffix.lower() != ".exe":
                return ValidationResult(
                    False,
                    f"Invalid file type: '{file_path.suffix}'. "
                    "Please select a Windows executable (.exe).",
                )
        else:
            # Linux / macOS — check execute permission
            if not os.access(file_path, os.X_OK):
                return ValidationResult(
                    False,
                    "The selected file does not have execute permission. "
                    "Run: chmod +x <file>",
                )

        return ValidationResult(True, "File path is valid.")
