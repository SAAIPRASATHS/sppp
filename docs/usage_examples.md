# Usage Examples

This guide provides practical examples of how to use the OpenModelica Simulation Studio for various simulation tasks.

## 1. Running a Basic Simulation (BouncingBall)
The `BouncingBall` model is a classic example in Modelica.
- **Executable**: `BouncingBall.exe`
- **Start Time**: 0
- **Stop Time**: 3
- **Action**: Click "Run Simulation".
- **Result**: You will see the height variable decreases as it bounces, eventually coming to rest (or continuing if no damping is applied).

## 2. Analyzing a Cooling System
For a custom cooling model:
- **Executable**: `CoolingSystem.exe`
- **Start Time**: 0
- **Stop Time**: 4.5
- **Observation**: Watch the temperature variables in the real-time display. Adjust the stop time to see when the system reaches steady state.

## 3. Comparing Multiple Runs
1. Run a simulation with `Stop Time = 2`.
2. Save the result in the history.
3. Run the same model with `Stop Time = 4`.
4. Use the "Compare View" to overlay both results on the same graph to analyze efficiency differences.

## Tips for Success
- Always check the **Console Panel** if a simulation fails; it contains detailed error messages from the OpenModelica runtime.
- Use the **History Search** to quickly find previous runs by executable name or date.
