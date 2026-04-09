# Installation Guide

Follow these steps to set up the OpenModelica Simulation Studio on your local machine.

## Prerequisites
- **Python 3.10 or higher**: Ensure Python is added to your system PATH.
- **OpenModelica**: A working installation of OpenModelica is required to generate simulation executables.

## Step-by-Step Setup

### 1. Clone the Repository
```bash
git clone https://github.com/SAAIPRASATHS/sppp.git
cd sppp
```

### 2. Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
Run the following command to launch the application:
```bash
python main.py
```

## Common Issues
- **ModuleNotFoundError**: Ensure you have activated your virtual environment before running the app.
- **Permission Denied**: On Linux/macOS, you may need to grant execute permissions to your simulation binaries (`chmod +x your_sim.exe`).
