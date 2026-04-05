import sys
import time
import csv
import random
import os

def main():
    print("Initializing mock simulation...")
    
    # Parse arguments
    start_time = 0
    stop_time = 1
    
    for arg in sys.argv:
        if arg.startswith("-override="):
            overrides = arg.replace("-override=", "").split(",")
            for o in overrides:
                if "startTime" in o:
                    start_time = float(o.split("=")[1])
                if "stopTime" in o:
                    stop_time = float(o.split("=")[1])

    print(f"Simulation Range: {start_time} to {stop_time}")
    print("Running TwoConnectedTanks calculation engine...")

    # Generate data
    steps = 50
    dt = (stop_time - start_time) / steps
    
    results = []
    t = start_time
    h1 = 2.0
    h2 = 1.0
    
    for i in range(steps + 1):
        # Fake tank dynamics: damped oscillations
        h1 = 1.5 + 0.5 * pow(0.95, i) * (1.0 if i % 10 < 5 else -1.0)
        h2 = 1.2 + 0.3 * pow(0.98, i) * (1.0 if (i+5) % 10 < 5 else -1.0)
        
        results.append({
            "time": round(t, 4),
            "tank1.level": round(h1 + random.uniform(-0.01, 0.01), 6),
            "tank2.level": round(h2 + random.uniform(-0.01, 0.01), 6),
            "valve.flow": round(0.5 * (h1 - h2), 6)
        })
        
        # Real-time streaming simulation
        print(f"Step {i}/{steps}: t={t:.2f} | h1={h1:.3f} | h2={h2:.3f}")
        time.sleep(0.05) # Simulate workload
        t += dt

    # Write CSV
    filename = "simulation_results.csv"
    keys = results[0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

    print(f"Simulation completed successfully.")
    print(f"Results saved to: {os.path.abspath(filename)}")

if __name__ == "__main__":
    main()
