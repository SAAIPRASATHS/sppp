"""
Run history manager for the Simulation Runner.

Tracks simulation runs in memory and provides persistence
via a JSON file so history survives application restarts.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class HistoryEntry:
    """A single simulation run record."""
    executable: str
    start_time: int
    stop_time: int
    status: str  # "Success" | "Failed"
    duration: float  # seconds
    timestamp: str  # ISO format
    return_code: int = 0
    output_file: str = ""  # Path to CSV output for comparison

    @property
    def display_text(self) -> str:
        """Human-readable summary for the history list."""
        status_icon = "✔" if self.status == "Success" else "✖"
        csv_icon = " 📊" if self.output_file else ""
        return (
            f"{status_icon} [{self.timestamp}]  "
            f"start={self.start_time} stop={self.stop_time}  "
            f"{self.duration:.2f}s  |  {self.executable}{csv_icon}"
        )


# Default persistence file
_HISTORY_FILE = Path(__file__).resolve().parent.parent / ".run_history.json"

# Maximum entries to keep
MAX_HISTORY = 50


class HistoryManager:
    """Manages an in-memory list of simulation runs with JSON persistence.

    Entries are stored newest-first and capped at MAX_HISTORY.
    """

    def __init__(self, history_file: Path | None = None):
        """Initialize the history manager.

        Args:
            history_file: Path to the JSON persistence file.
                          Defaults to .run_history.json in project root.
        """
        self._file = history_file or _HISTORY_FILE
        self._entries: list[HistoryEntry] = []
        self._load()

    @property
    def entries(self) -> list[HistoryEntry]:
        """Return all history entries (newest first)."""
        return list(self._entries)

    def add(
        self,
        executable: str,
        start_time: int,
        stop_time: int,
        status: str,
        duration: float,
        return_code: int = 0,
        output_file: str = "",
    ) -> HistoryEntry:
        """Record a new simulation run.

        Args:
            executable: Name of the executable file.
            start_time: Simulation start time.
            stop_time: Simulation stop time.
            status: "Success" or "Failed".
            duration: Execution duration in seconds.
            return_code: Process return code.
            output_file: Path to the CSV output file (if any).

        Returns:
            The newly created HistoryEntry.
        """
        entry = HistoryEntry(
            executable=executable,
            start_time=start_time,
            stop_time=stop_time,
            status=status,
            duration=duration,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            return_code=return_code,
            output_file=output_file,
        )
        self._entries.insert(0, entry)

        # Cap history size
        if len(self._entries) > MAX_HISTORY:
            self._entries = self._entries[:MAX_HISTORY]

        self._save()
        return entry

    def clear(self) -> None:
        """Clear all history entries."""
        self._entries.clear()
        self._save()

    def get_entry(self, index: int) -> HistoryEntry | None:
        """Get a history entry by index.

        Args:
            index: Zero-based index (0 = most recent).

        Returns:
            HistoryEntry or None if out of range.
        """
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None

    def get_entries_with_files(self) -> list[HistoryEntry]:
        """Return only entries that have associated output files.

        Used by the Compare Runs view to filter entries that
        can be plotted and compared.

        Returns:
            List of HistoryEntry objects with non-empty output_file
            where the file still exists on disk.
        """
        return [
            e
            for e in self._entries
            if e.output_file and Path(e.output_file).exists()
        ]

    def _save(self) -> None:
        """Persist history to JSON file."""
        try:
            data = [asdict(e) for e in self._entries]
            self._file.write_text(
                json.dumps(data, indent=2), encoding="utf-8"
            )
        except OSError:
            pass  # Non-critical

    def _load(self) -> None:
        """Load history from JSON file."""
        if not self._file.exists():
            return
        try:
            data = json.loads(self._file.read_text(encoding="utf-8"))
            self._entries = [
                HistoryEntry(**entry) for entry in data
            ]
        except (OSError, json.JSONDecodeError, TypeError):
            self._entries = []
