"""
Config Manager for Simulation Studio settings.

Handles saving and loading the simulation setup (executable path,
start/stop times) to and from JSON configuration files.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manager for setting up, saving, and loading simulation experiments."""

    @staticmethod
    def save_config(params: Dict[str, Any], config_path: Path) -> bool:
        """Save simulation parameters to a JSON file.

        Args:
            params: Dictionary containing simulation configuration.
            config_path: Destination path for the JSON config file.

        Returns:
            True if settings saved successfully, else False.
        """
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(params, f, indent=4)
            return True
        except (OSError, TypeError):
            return False

    @staticmethod
    def load_config(config_path: Path) -> Optional[Dict[str, Any]]:
        """Load simulation parameters from a JSON file.

        Args:
            config_path: Path to the JSON configuration file.

        Returns:
            Dictionary containing parameters if loaded, else None.
        """
        try:
            if not config_path.exists():
                return None
            with open(config_path, 'r') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None


class SimulationConfig:
    """Container for simulation parameter settings."""

    def __init__(self, exe_path: str, start_time: int, stop_time: int):
        self.exe_path = exe_path
        self.start_time = start_time
        self.stop_time = stop_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration settings into a dictionary."""
        return {
            "exe_path": self.exe_path,
            "start_time": self.start_time,
            "stop_time": self.stop_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationConfig":
        """Initialize configuration parameters from a dictionary."""
        return cls(
            exe_path=data.get("exe_path", ""),
            start_time=data.get("start_time", 0),
            stop_time=data.get("stop_time", 4)
        )
