@echo off
rem Mock simulation wrapper for OpenModelica Simulation Runner
echo Starting mock simulation process...
python "%~dp0mock_sim_logic.py" %*
if %errorlevel% neq 0 (
    echo Simulation failed.
    exit /b 1
)
echo Done.
