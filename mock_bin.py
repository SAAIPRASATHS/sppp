"""
Mock OpenModelica Simulation Binary.

Mimics the behavior of an OpenModelica-generated executable:
1. Accepts -override startTime=X,stopTime=Y.
2. Prints progress messages to stdout.
3. Generates a _res.csv file with numeric data.
"""

import sys
import argparse
import time
import csv
import random
from pathlib import Path

def main():
    print("OpenModelica Simulation Studio — Mock Binary (TwoConnectedTanks)")
    print("--------------------------------------------------------------")
    
    # Simple manual parsing of the -override flag
    start_time = 0.0
    stop_time = 1.0
    
    for arg in sys.argv:
        if arg.startswith("-override="):
            parts = arg.split("=", 1)
            if len(parts) < 2:
                continue
            overrides = parts[1].split(",")
            for o in overrides:
                kv = o.split("=", 1)
                if len(kv) < 2:
                    continue
                key, val = kv[0], kv[1]
                try:
                    if "startTime" in key:
                        start_time = float(val)
                    elif "stopTime" in key:
                        stop_time = float(val)
                except ValueError:
                    continue

    print(f"INFO: Simulation interval: [{start_time}, {stop_time}]")
    print("INFO: Initializing differential equations solver...")
    time.sleep(0.5)
    
    # Simulate progress
    for i in range(1, 101, 10):
        print(f"LOG: Solving for time t = {start_time + (stop_time - start_time) * i / 100.0:.2f} (Progress: {i}%)")
        time.sleep(0.1)

    # Generate output CSV
    # Name format: <exe_name>_res.csv
    # We'll use TwoConnectedTanks_res.csv
    output_path = Path("TwoConnectedTanks_res.csv")
    
    headers = ["time", "tank1.level", "tank2.level", "valve.flow"]
    
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        steps = 50
        current_time = start_time
        dt = (stop_time - start_time) / steps
        
        # Simple Physics Model: Two Connected Tanks
        # dh1/dt = -k * sqrt(h1 - h2)
        # dh2/dt =  k * sqrt(h1 - h2)
        h1 = 2.0  # Initial level tank 1
        h2 = 0.5  # Initial level tank 2
        k = 0.1   # Flow coefficient
        
        for _ in range(steps + 1):
            writer.writerow([
                f"{current_time:.2f}",
                f"{h1:.6f}",
                f"{h2:.6f}",
                f"{max(0, k * (h1 - h2)**0.5 if h1 > h2 else 0):.6f}"
            ])
            
            # Euler integration
            if h1 > h2:
                flow = k * ((h1 - h2)**0.5)
                h1 -= flow * dt
                h2 += flow * dt
            
            current_time += dt
            # Level cannot be negative
            h1 = max(0, h1)
            h2 = max(0, h2)

    print(f"SUCCESS: Simulation finished. Results written to: {output_path.absolute()}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
