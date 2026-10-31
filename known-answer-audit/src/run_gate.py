#!/usr/bin/env python3
"""run_gate.py  v1  The environment's gate for regime C3: run gate.py in a run folder after the agent says
DONE, save the report as private/gate_rounds/RUN_round<k>.txt, and print it for the return message.

    python3 run_gate.py RUN_ID ROUND
"""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
run_id, rnd = sys.argv[1], int(sys.argv[2])
folder = os.path.join(ROOT, "runs", run_id)
g = subprocess.run([sys.executable, "gate.py"], cwd=folder, capture_output=True, text=True, timeout=1200)
rep = (g.stdout + ("\n" + g.stderr if g.stderr.strip() else "")).strip()
path = os.path.join(ROOT, "private", "gate_rounds", f"{run_id}_round{rnd}.txt")
if os.path.exists(path):
    sys.exit(f"{path} exists; rounds are never overwritten")
open(path, "w", encoding="utf8").write(f"exit {g.returncode}\n{rep}\n")
print(f"exit {g.returncode}\n{rep}")
