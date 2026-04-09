# System Architecture

The OpenModelica Simulation Studio follows a modular, Object-Oriented Programming (OOP) design to ensure maintainability and scalability.

## High-Level Components

### 1. Presentation Layer (GUI)
- **MainWindow**: The primary controller for the user interface, managing the layout and coordination between panels.
- **Panels**: Modular UI sections (e.g., Control Panel, Console Panel, Plot Panel) that handle specific user interactions.
- **ThemeManager**: Handles dynamic CSS (QSS) switching for light and dark modes.

### 2. Logic Layer (Core)
- **SimulationRunner**: Inherits from `QThread`. Responsible for managing the simulation subprocess and streaming output.
- **Validator**: Ensures input parameters (Start/Stop time) adhere to the required constraints.
- **ResultParser**: Processes simulation output files (CSV/MAT) for visualization.
- **HistoryManager**: Keeps track of previous simulation runs and metadata.

### 3. Utility Layer (Utils)
- Helper functions for file I/O, logging, and color palette management.

## Data Flow
1. User selects an executable and enters parameters in the **GUI**.
2. The **Validator** checks the parameters.
3. The **SimulationRunner** launches the process via `subprocess.Popen`.
4. Output is piped back to the **Console Panel** in real-time.
5. Upon completion, the **ResultParser** reads the output, and the **Plot Panel** renders the data using Matplotlib.
