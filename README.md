# OpenModelica Simulation Studio

A PyQt6-based desktop application for executing OpenModelica simulation executables. This tool provides real-time output streaming, interactive result visualization, and parameter sweep capabilities in a professional workspace.

## Key Features

- **Subprocess Execution**: Run OpenModelica-generated `.exe` binaries with real-time stdout/stderr streaming.
- **Data Visualization**: Integrated Matplotlib charts for interactive analysis of simulation results.
- **Parameter Sweep**: Batch execution mode for multiple stop-time configurations.
- **Run Comparison**: Overlay multiple simulation results on a single chart for side-by-side analysis.
- **Workspace Management**: VS Code-inspired layout with dark and light theme support.
- **Automated Reporting**: Generation of structured simulation reports for every run.

## Getting Started

### Prerequisites

- Python 3.10 or later
- OpenModelica simulation executables

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd OpenModelica-Simulation-Studio
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. **Select Executable**: Use the file picker in the sidebar to select an OpenModelica-compiled `.exe`.
2. **Configure Parameters**: Set the simulation start and stop times.
3. **Execute**: Click "Run Simulation" to start the process. Output will stream to the console panel in real-time.
4. **Analyze**: Results are automatically scanned and can be plotted using the "Plot" action or via the History panel.

## Project Structure

```text
├── core/                # Simulation logic, runners, and data parsers
├── gui/                 # PyQt6 window, panels, and theme management
├── utils/               # File handling and general utilities
├── reports/             # Auto-generated simulation reports
├── runs/                # Organized output folders for individual runs
└── main.py              # Application entry point
```

## Configuration

The application stores persistent settings (last used executable, theme) in `.sim_settings.json`. Individual simulation configurations can be exported and imported as JSON files via the Control Panel.

## License

This project is licensed under the MIT License.
