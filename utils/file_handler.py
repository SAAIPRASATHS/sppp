"""
File selection and inspection utilities.

Handles executable file picking via QFileDialog and extracts
file metadata (name, size, last modified) for the inspector panel.
"""

import os
import stat
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QWidget


@dataclass
class FileInfo:
    """Metadata about a selected executable file."""
    name: str
    size_bytes: int
    size_display: str
    last_modified: str
    is_executable: bool
    full_path: str


def select_executable(parent: QWidget | None = None) -> str:
    """Open a file dialog to choose a simulation executable.

    Uses platform-appropriate filters: .exe on Windows, all files
    on Linux/macOS.

    Args:
        parent: Parent widget for the dialog.

    Returns:
        Absolute file path string, or empty string if cancelled.
    """
    import platform

    if platform.system() == "Windows":
        file_filter = "Simulation Executables (*.exe)"
    else:
        file_filter = "All Files (*)"

    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Select Simulation Executable",
        "",
        file_filter,
    )
    return path


def _format_size(size_bytes: int) -> str:
    """Convert byte count to a human-readable string.

    Args:
        size_bytes: File size in bytes.

    Returns:
        Formatted string like '2.4 MB' or '512 B'.
    """
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def inspect_file(path: str) -> FileInfo | None:
    """Extract metadata from the selected file.

    Args:
        path: Absolute path to the file.

    Returns:
        FileInfo dataclass with metadata, or None if file doesn't exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        return None

    st = file_path.stat()
    modified_dt = datetime.fromtimestamp(st.st_mtime)

    return FileInfo(
        name=file_path.name,
        size_bytes=st.st_size,
        size_display=_format_size(st.st_size),
        last_modified=modified_dt.strftime("%Y-%m-%d %H:%M:%S"),
        is_executable=bool(st.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
        or file_path.suffix.lower() == ".exe",
        full_path=str(file_path.resolve()),
    )
