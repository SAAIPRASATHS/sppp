# OpenModelica Simulation Studio

## Description
This project is developed for the FOSSEE Summer Fellowship 2026 (OpenModelica Screening Task). The OpenModelica Simulation Studio is a professional desktop application designed to streamline the execution, monitoring, and visualization of OpenModelica simulation binaries.

## Features
*   **Subprocess Execution**: Seamless execution of OpenModelica-generated simulation binaries using Python's subprocess module.
*   **PyQt6 GUI**: A clean, modern, and responsive interface built with the PyQt6 framework.
*   **Dynamic Inputs**: Dedicated input fields for selecting simulation executables and configuring time parameters.
*   **Real-time Output Display**: Live streaming of simulation stdout and stderr to an integrated console.
*   **Data Visualization**: High-quality plotting of simulation results using Matplotlib.
*   **Parameter Validation**: Strict validation logic ensuring simulation parameters remain within safe bounds (0 ≤ start < stop < 5).

## Technologies Used
*   Python 3.x
*   PyQt6
*   OpenModelica
*   Matplotlib

## Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/openmodelica-simulation-studio.git
    cd openmodelica-simulation-studio
    ```

2.  **Install Dependencies**
    Ensure you have Python 3.x installed. Install the required libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    Launch the simulation studio:
    ```bash
    python main.py
    ```

## Usage
1.  **Select Executable**: Click the folder icon or use the file selector to choose an OpenModelica-compiled executable (.exe).
2.  **Enter Time Parameters**: Input the desired Start Time and Stop Time. (Note: Values must satisfy 0 ≤ start < stop < 5).
3.  **Run Simulation**: Click the "Run Simulation" button to begin execution.
4.  **View Results**: Monitor the live console output and view the generated plots upon successful completion.

## How It Works
OpenModelica simulations are typically authored in the Modelica language and compiled into standalone C-code executables. This application automates the interaction with these binaries.

*   **Command Execution**: The application utilizes the `subprocess.Popen` API to launch the simulation as a child process.
*   **Override Arguments**: Simulation parameters are passed to the binary using the OpenModelica override flag: `-override startTime=X,stopTime=Y`.
*   **Threaded Execution**: Simulations run in a dedicated background thread to ensure the GUI remains responsive during intensive calculations.

## Project Structure
*   **core/**: Contains the business logic, including the simulation runner, result parser, and parameter validator.
*   **gui/**: Contains the PyQt6 layout definitions, custom styles, and main window logic.
*   **utils/**: Helper modules for file system operations and logging.
*   **main.py**: The central entry point of the application.
*   **requirements.txt**: List of Python dependencies required to run the project.

## Screenshots
*(Section intentionally left for UI and output screenshots)*

## Example Run
*   **Input Executable**: `BouncingBall.exe`
*   **Start Time**: 0
*   **Stop Time**: 4
*   **Behavior**: Upon clicking Run, the console will display the simulation header. Once finished, a plot window will appear showing the height (`h`) and velocity (`v`) of the ball over the 4-second interval.

## Evaluation Highlights
*   **Clean OOP Design**: Separation of concerns between UI logic, simulation execution, and data processing.
*   **User-friendly Interface**: Intuitive layout designed for technical users and evaluators.
*   **Real-time Execution**: Efficient handling of subprocess output for immediate feedback.
*   **Proper Documentation**: Comprehensive code comments and structured README for easy assessment.

## License
This project is licensed under the MIT License.
