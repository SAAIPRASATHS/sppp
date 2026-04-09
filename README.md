# OpenModelica Simulation Studio

A professional PyQt6 desktop application for executing, monitoring, and visualizing OpenModelica simulation binaries. Developed for the FOSSEE Summer Fellowship 2026 (OpenModelica Screening Task).

---

## Project Structure

```
openmodelica-simulation-studio/
├── core/
│   ├── simulation_runner.py   # Subprocess execution in background thread
│   ├── validator.py           # Input and file validation logic
│   ├── result_parser.py       # CSV result detection and parsing
│   ├── history_manager.py     # Run history tracking
│   ├── logger.py              # Structured log formatting
│   ├── config_manager.py      # Save/load simulation configuration
│   ├── export_manager.py      # ZIP/copy export of result files
│   ├── output_manager.py      # Run folder organization
│   ├── report_generator.py    # Simulation report generation
│   └── sweep_runner.py        # Parameter sweep execution
├── gui/
│   ├── main_window.py         # Primary application window
│   ├── theme_manager.py       # Dark/light theme switching
│   ├── compare_view.py        # Side-by-side run comparison
│   ├── plot_widget.py         # Matplotlib plotting widget
│   ├── panels/
│   │   ├── control_panel.py   # Left sidebar: file + simulation setup
│   │   ├── console_panel.py   # Terminal output display
│   │   ├── plot_panel.py      # Visualization workspace
│   │   ├── inspector_panel.py # Right sidebar: status + file listing
│   │   └── history_panel.py   # Run history list
│   └── styles/
│       ├── dark_theme.qss     # Dark mode stylesheet
│       └── light_theme.qss    # Light mode stylesheet
├── utils/
│   └── file_handler.py        # File dialog + metadata utilities
├── model/
│   ├── TwoConnectedTanks.exe  # OpenModelica-generated simulation binary
│   └── README.md              # Instructions for the model directory
├── sample_data/
│   └── simulation_results.csv # Example output for reference
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
└── README.md
```

---

## How the Executable Was Generated

The `TwoConnectedTanks` model was authored in the Modelica language and compiled using OpenModelica:

1. **Model design** — The `TwoConnectedTanks.mo` model defines two fluid tanks connected by a valve, governed by differential equations for fluid dynamics.
2. **Compilation** — OpenModelica compiles the Modelica model to C code and links it into a standalone Windows executable.
3. **Output** — The resulting `TwoConnectedTanks.exe` accepts simulation parameters via command-line override flags and writes results to a `_res.csv` file.

The executable is included in the `/model/` folder. **No OpenModelica installation is required to run this application.**

---

## Installation

**Requirements:** Python 3.10+

```bash
# 1. Clone the repository
git clone https://github.com/your-username/openmodelica-simulation-studio.git
cd openmodelica-simulation-studio

# 2. (Optional) Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

---

## Usage

### Running the Pre-bundled TwoConnectedTanks Model

The application automatically detects `TwoConnectedTanks.exe` in the `model/` folder on startup — no manual selection needed.

1. **Launch** — Run `python main.py`. The executable is auto-loaded and shown in the sidebar.
2. **Set time parameters** — Enter Start Time and Stop Time (must satisfy `0 ≤ start < stop < 5`).
3. **Run** — Click **▶ Run Simulation**. Progress streams live to the console panel.
4. **View results** — On success, the plot panel automatically renders the simulation output.

### Selecting a Different Executable

Click **Select Executable...** in the sidebar to browse for any OpenModelica-compiled binary.

---

## Command Format

The application invokes the executable using the standard OpenModelica override syntax:

```
TwoConnectedTanks.exe -override=startTime=0,stopTime=4
```

This is built programmatically by `core/simulation_runner.py`:

```python
def build_command(self) -> list[str]:
    override_arg = f"-override=startTime={self._start_time},stopTime={self._stop_time}"
    return [str(self._executable), override_arg]
```

---

## Input Validation

The validator (`core/validator.py`) enforces:

| Rule | Condition |
|------|-----------|
| Start ≥ 0 | `start_time >= 0` |
| Stop < 5 | `stop_time < 5` |
| Start < Stop | `start_time < stop_time` |
| Valid executable | File exists and is a `.exe` (Windows) or executable binary (Linux) |

Invalid inputs trigger a `QMessageBox` warning — no simulation is launched.

---

## Features

- **Subprocess Execution** — Runs simulation binaries via `subprocess.Popen` in a background `QThread`, keeping the GUI responsive.
- **Real-time Console** — Streams `stdout` and `stderr` line-by-line as the simulation runs.
- **Auto-load** — Automatically detects and loads the executable from `model/` on startup.
- **Result Plotting** — Parses the output CSV and plots all numeric columns using Matplotlib.
- **Parameter Sweep** — Run the same model across multiple stop times and compare results.
- **Run History** — Each run is logged with duration, status, and output file path.
- **Dark / Light Theme** — Toggle via the toolbar; preference is saved across sessions.
- **Export** — Export result files as a ZIP archive or copy to a chosen directory.

---

## Architecture

```
main.py
  └── MainWindow (QMainWindow)
        ├── ControlPanel     — user inputs + run controls
        ├── ConsolePanel     — live terminal output
        ├── PlotPanel        — matplotlib result visualization
        ├── InspectorPanel   — execution status + file list
        └── HistoryPanel     — past run records
              │
        ┌─────┴──────┐
  SimulationRunner   SweepRunner
  (QThread)          (QThread)
        │
  subprocess.Popen → TwoConnectedTanks.exe -override=startTime=X,stopTime=Y
```

---

## Dependencies

```
PyQt6>=6.6.0
matplotlib>=3.8.0
```

Install with: `pip install -r requirements.txt`

---

## Notes for Evaluators

- The executable is included in `/model/` for immediate testing — no additional tools required.
- The application auto-loads the executable on startup.
- Use Start Time `0` and Stop Time `4` for a standard test run.
- Results are plotted automatically and also saved to a timestamped folder under `runs/`.

---

## License

MIT License
