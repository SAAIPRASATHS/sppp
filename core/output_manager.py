"""
Output Manager for Simulation Studio runs.

Identifies and creates unique, timestamped directories for organizing
each simulation run's output files and logs.
"""

import datetime
import os
from pathlib import Path


class OutputManager:
    """Manager for maintaining a clean, organized workspace by creating run folders."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.runs_dir = base_dir / "runs"

    def create_run_folder_path(self) -> Path:
        """Construct a unique directory path for a new simulation run.

        Returns:
            The unique, timestamped run folder Path.
        """
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        run_name = f"run_{timestamp}"
        
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        run_folder = self.runs_dir / run_name
        return run_folder

    def make_run_folder(self) -> Path:
        """Create a new timestamped directory for a simulation run.

        Returns:
            The created run directory Path.
        """
        run_folder = self.create_run_folder_path()
        run_folder.mkdir(parents=True, exist_ok=True)
        return run_folder

    @staticmethod
    def list_generated_files(run_dir: Path) -> list:
        """List all generated files within a specific run directory.

        Args:
            run_dir: Path to the run folder.

        Returns:
            A list of Path objects for all files within the directory.
        """
        if not run_dir.exists():
            return []
        
        files = [p for p in run_dir.iterdir() if p.is_file()]
        return files
