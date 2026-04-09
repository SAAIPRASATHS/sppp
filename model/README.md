# Model Directory

Place your OpenModelica-generated simulation executable and its runtime dependencies here.

## Expected Contents

```
model/
├── TwoConnectedTanks.exe          # Compiled simulation binary
├── TwoConnectedTanks_init.xml     # Initialization file (if generated)
└── (any required DLLs)            # Runtime libraries from OM build
```

## How the Executable Was Generated

1. Open OpenModelica Connection Editor (OMEdit).
2. Load or create the `TwoConnectedTanks` model.
3. Simulate the model once via **Simulation > Simulate**.
4. OpenModelica compiles the Modelica code to C and produces a standalone executable.
5. Copy the generated `.exe` (and any companion files) from the OpenModelica working directory into this folder.

## Auto-Loading

When the application starts, it automatically scans this directory for `.exe` files.
If a simulation executable is found, it is loaded as the default — no manual selection needed.
