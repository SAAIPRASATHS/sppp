# ⚙ OpenModelica Simulation Runner v2.0

A professional PyQt6 desktop application for executing OpenModelica-generated simulation executables with real-time output streaming, result analysis, CSV visualization, and automated report generation.

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue) ![PyQt6](https://img.shields.io/badge/UI-PyQt6-green) ![Matplotlib](https://img.shields.io/badge/Plot-Matplotlib-orange) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### Core Features
| Feature | Description |
|---|---|
| **Executable Picker** | Browse and select any OpenModelica `.exe` binary |
| **File Inspector** | View file name, size, and last modified date |
| **Parameter Inputs** | Set start/stop time with validation (`0 ≤ start < stop < 5`) |
| **Command Preview** | See the exact command before running |
| **Input Validation** | Enforced constraints with descriptive error dialogs |
| **One-Click Demo** | Run with preset params (start=0, stop=4) instantly |

### v2.0 — Advanced Features
| Feature | Description |
|---|---|
| **Real-Time Output Streaming** | stdout/stderr streamed line-by-line via QThread |
| **Result File Auto-Detection** | Scans for .csv, .mat, .plt, .json after each run |
| **CSV Preview Panel** | Tabular preview of first 100 rows with column headers |
| **Graph Visualization** | Interactive matplotlib plots with column selection |
| **Execution Time Tracker** | Precise timing displayed in status bar |
| **Report Generator** | Auto-generates structured .txt reports per run |
| **Run History Panel** | Persistent clickable history with parameter reload |
| **Dark/Light Mode Toggle** | Full theme switching with one click |
| **Tabbed Interface** | Organized into Simulation, Results & Plot, History |
| **Persistent Settings** | Saves executable path, params, and theme preference |

---

## 📁 Project Structure

```
├── main.py                          # Application entry point
├── gui/
│   ├── __init__.py
│   ├── main_window.py               # Main UI with tabs and themes
│   └── plot_widget.py               # Matplotlib chart widget
├── core/
│   ├── __init__.py
│   ├── simulation_runner.py         # QThread subprocess with timing
│   ├── validator.py                 # Input validation logic
│   ├── logger.py                    # HTML-formatted log output
│   ├── result_parser.py             # CSV parsing and file scanning
│   ├── report_generator.py          # Structured report creation
│   └── history_manager.py           # Persistent run history
├── utils/
│   ├── __init__.py
│   └── file_handler.py              # File selection and inspection
├── reports/                         # Auto-generated simulation reports
├── requirements.txt
└── README.md
```

---

## 🚀 Setup

### Prerequisites
- **Python 3.10** or later
- **pip** package manager

### Installation

```bash
# 1. Navigate to project directory
cd spppp

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶ How to Run

```bash
python main.py
```

---

## 📖 Usage Guide

### Tab 1: Simulation
1. **Browse** → Select your OpenModelica executable (e.g., `TwoConnectedTanks.exe`)
2. **Set Parameters** → Enter Start Time and Stop Time
3. **Preview** → The exact command updates in real time
4. **Run Simulation** → Output streams live into the console
5. **Or use Demo Mode** → One click runs with `start=0, stop=4`

### Tab 2: Results & Plot
- After a simulation run, output files are **auto-detected**
- Click any `.csv` file to see a **tabular preview**
- Select X/Y columns and click **Plot** to visualize
- Use the matplotlib toolbar to **zoom, pan, and save** charts

### Tab 3: History
- All runs are recorded with status, duration, and parameters
- **Double-click** any entry to reload its parameters
- History **persists** across application restarts

### Theme Toggle
- Click **☀ Light Mode / 🌙 Dark Mode** in the top-right corner to switch themes

---

## 📊 Graph Visualization

The plot widget supports:
- **Auto-detection** of numeric columns in CSV data
- **Smart defaults** — tries to detect "time" column for X-axis
- **Interactive toolbar** — zoom, pan, home, save as image
- **Dark-themed** chart styling consistent with the app theme

---

## 📝 Report Generation

After each run, a structured report is saved to the `reports/` directory:

```
============================================================
     OPENMODELICA SIMULATION REPORT
============================================================

TIMESTAMP:          2026-04-01 20:30:00
EXECUTABLE:         TwoConnectedTanks.exe
PATH:               D:\models\TwoConnectedTanks.exe

------------------------------------------------------------
SIMULATION PARAMETERS:
    Start Time:     0
    Stop Time:      4

------------------------------------------------------------
EXECUTION RESULTS:
    Status:         Success
    Return Code:    0
    Duration:       2.341 seconds

------------------------------------------------------------
OUTPUT FILES DETECTED:
    • TwoConnectedTanks_res.csv
    • TwoConnectedTanks_res.mat

============================================================
```

---

## 🏗 Architecture

| Module | Responsibility |
|--------|---------------|
| `core/simulation_runner.py` | QThread with Popen, real-time streaming, execution timing |
| `core/validator.py` | Pure validation with `ValidationResult` dataclass |
| `core/logger.py` | HTML-formatted, timestamped, color-coded log entries |
| `core/result_parser.py` | CSV parsing, output file scanning, column analysis |
| `core/report_generator.py` | Structured text report creation and file saving |
| `core/history_manager.py` | JSON-persisted run history with entry management |
| `gui/main_window.py` | Tabbed UI, theme management, signal coordination |
| `gui/plot_widget.py` | Matplotlib FigureCanvas with column selectors |
| `utils/file_handler.py` | File dialog wrapper and metadata inspector |

---

## ⚠ Error Handling

| Scenario | Behavior |
|----------|----------|
| No file selected | Warning dialog |
| Invalid time inputs | Descriptive validation error |
| File not found at runtime | Error logged with path |
| Permission denied | Explanation with fix suggestion |
| CSV parse failure | Error shown in status label |
| Missing output files | Info message in console |
| Execution crash | Status → Failed, stderr displayed |

---

## 📄 License

MIT — use freely for educational and professional purposes.
