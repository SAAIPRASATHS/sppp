"""
Result file detection and CSV parsing for simulation output.

Scans directories for output files (.csv, .mat) and provides
efficient CSV preview with limited row loading. Includes smart
detection to filter non-simulation data files.
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ResultFile:
    """Metadata about a detected result file."""
    name: str
    full_path: str
    extension: str
    size_display: str
    has_numeric_data: bool = True


@dataclass
class CsvPreview:
    """Parsed CSV data for preview and plotting."""
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    total_rows: int = 0
    error: str = ""
    numeric_column_count: int = 0


# Supported output file extensions
RESULT_EXTENSIONS = {".csv", ".mat", ".plt", ".json"}

# Maximum rows to load for preview
MAX_PREVIEW_ROWS = 100


def _format_size(size_bytes: int) -> str:
    """Convert byte count to human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _probe_csv_has_numeric_data(file_path: Path) -> bool:
    """Quick probe to check if a CSV file contains numeric simulation data.

    Reads the first few rows and checks if at least one column
    contains parseable floating-point numbers. This filters out
    credential files, config files, logs, etc.

    Args:
        file_path: Path to the CSV file.

    Returns:
        True if the file appears to contain numeric simulation data.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            sample = f.read(4096)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel

            reader = csv.reader(f, dialect)

            # Read header
            try:
                headers = next(reader)
            except StopIteration:
                return False

            if not headers:
                return False

            # Read up to 5 data rows
            data_rows: list[list[str]] = []
            for _, row in zip(range(5), reader):
                data_rows.append(row)

            if not data_rows:
                return False

            # Check each column for numeric values
            for col_idx in range(len(headers)):
                numeric_count = 0
                for row in data_rows:
                    if col_idx >= len(row) or not row[col_idx].strip():
                        continue
                    try:
                        float(row[col_idx].strip())
                        numeric_count += 1
                    except ValueError:
                        pass
                if numeric_count > 0:
                    return True

            return False

    except Exception:
        return False


def scan_result_files(
    directory: str,
    smart_filter: bool = True,
) -> list[ResultFile]:
    """Scan a directory for simulation output files.

    Args:
        directory: Absolute path to the directory to scan.
        smart_filter: If True, probe CSV files and exclude those
                      without numeric data (e.g. credentials, configs).

    Returns:
        List of ResultFile objects for each detected output file,
        sorted by modification time (newest first).
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return []

    results: list[ResultFile] = []
    for file_path in dir_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in RESULT_EXTENSIONS:
            # Skip hidden/dot files (e.g. .sim_settings.json, .run_history.json)
            if file_path.name.startswith("."):
                continue

            try:
                st = file_path.stat()

                # Smart filtering for CSV files
                has_numeric = True
                if smart_filter and file_path.suffix.lower() == ".csv":
                    has_numeric = _probe_csv_has_numeric_data(file_path)
                    if not has_numeric:
                        continue  # Skip non-numeric CSV files

                results.append(ResultFile(
                    name=file_path.name,
                    full_path=str(file_path.resolve()),
                    extension=file_path.suffix.lower(),
                    size_display=_format_size(st.st_size),
                    has_numeric_data=has_numeric,
                ))
            except OSError:
                continue

    # Sort newest first
    results.sort(
        key=lambda f: Path(f.full_path).stat().st_mtime,
        reverse=True,
    )
    return results


def parse_csv_preview(
    file_path: str,
    max_rows: int = MAX_PREVIEW_ROWS,
) -> CsvPreview:
    """Parse a CSV file and return limited rows for preview.

    Handles common CSV dialects, large files, and encoding issues.

    Args:
        file_path: Absolute path to the CSV file.
        max_rows: Maximum number of data rows to return.

    Returns:
        CsvPreview with headers, rows, total count, and any error.
    """
    path = Path(file_path)
    if not path.exists():
        return CsvPreview(error=f"File not found: {path.name}")

    if path.suffix.lower() != ".csv":
        return CsvPreview(error=f"Not a CSV file: {path.name}")

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            # Sniff dialect for flexibility
            sample = f.read(4096)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel  # fallback

            reader = csv.reader(f, dialect)

            # Read header
            try:
                headers = next(reader)
            except StopIteration:
                return CsvPreview(error="CSV file is empty.")

            # Clean headers
            headers = [h.strip().strip('"') for h in headers]

            # Read data rows
            rows: list[list[str]] = []
            total = 0
            for row in reader:
                total += 1
                if len(rows) < max_rows:
                    rows.append([cell.strip() for cell in row])

            # Count numeric columns
            preview = CsvPreview(
                headers=headers,
                rows=rows,
                total_rows=total,
            )
            preview.numeric_column_count = len(get_numeric_columns(preview))
            return preview

    except PermissionError:
        return CsvPreview(error=f"Permission denied: {path.name}")
    except UnicodeDecodeError:
        return CsvPreview(error=f"Encoding error reading: {path.name}")
    except Exception as exc:
        return CsvPreview(error=f"Error parsing CSV: {exc}")


def get_numeric_columns(preview: CsvPreview) -> list[str]:
    """Identify columns that contain numeric data for plotting.

    Args:
        preview: A previously parsed CsvPreview.

    Returns:
        List of header names where data is numeric.
    """
    if not preview.headers or not preview.rows:
        return []

    numeric_cols: list[str] = []
    for col_idx, header in enumerate(preview.headers):
        is_numeric = True
        sample_count = 0
        for row in preview.rows[:20]:  # Check first 20 rows
            if col_idx >= len(row) or not row[col_idx]:
                continue
            try:
                float(row[col_idx])
                sample_count += 1
            except ValueError:
                is_numeric = False
                break
        if is_numeric and sample_count > 0:
            numeric_cols.append(header)

    return numeric_cols


def get_column_data(preview: CsvPreview, column_name: str) -> list[float]:
    """Extract a column's numeric data as a list of floats.

    Args:
        preview: A previously parsed CsvPreview.
        column_name: Header name of the column.

    Returns:
        List of float values (skips non-numeric rows).
    """
    if column_name not in preview.headers:
        return []

    col_idx = preview.headers.index(column_name)
    values: list[float] = []
    for row in preview.rows:
        if col_idx < len(row) and row[col_idx]:
            try:
                values.append(float(row[col_idx]))
            except ValueError:
                values.append(float("nan"))
    return values
