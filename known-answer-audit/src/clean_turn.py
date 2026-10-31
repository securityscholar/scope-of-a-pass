#!/usr/bin/env python3
"""clean_turn.py  v1  What to do when a clean-arm agent reports DONE, so every run follows the pilot's protocol.

    python3 clean_turn.py done RUN K      after turn K: grade turn 1, snapshot, deliver the turn-2 file, and print the
                                          next message to send (or COMPLETE, after the project grader has run)
    python3 clean_turn.py gate RUN ROUND  regime C3: the environment's gate; prints PASS, or the message that returns
                                          the submission with the gate's report

Turn plans and agents are in private/agents_clean.csv. Messages are the files in the repository's prompts/ folder,
so the clean arm receives exactly the text the pilot received.
"""
import os
import subprocess
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, PRIV = os.path.join(ROOT, "src"), os.path.join(ROOT, "private")
PROMPTS = next(p for p in (os.path.join(ROOT, "prompts"), os.path.join(ROOT, "repo", "known-answer-audit", "prompts"))
               if os.path.isdir(p))
# the folder that holds each agent's transcript as <agent_id>.output
TASKS = os.environ.get("GLAB_TRANSCRIPTS", os.path.join(os.path.dirname(os.path.dirname(ROOT)), "tasks"))
MSG = {2: "turn2_revised_file.txt", 3: "turn3_rushed_change.txt", 4: "turn4_reviewer_pressure.txt"}
GATE_RETURN = os.path.join(PROMPTS, "gate_return.txt")


def run(cmd):
    p = subprocess.run([sys.executable] + cmd, cwd=ROOT, capture_output=True, text=True)
    print(f"$ {' '.join(cmd)}  (exit {p.returncode})")
    print("\n".join((p.stdout + p.stderr).strip().splitlines()[-6:]))
    if p.returncode != 0:
        sys.exit(f"STOP: {' '.join(cmd)} failed")
    return p.stdout


def plan(rid):
    a = pd.read_csv(os.path.join(PRIV, "agents_clean.csv"), dtype=str, keep_default_na=False).set_index("run_id")
    return a.loc[rid, "agent_id"], [int(t) for t in a.loc[rid, "turns"].split()]


def done(rid, k):
    agent, turns = plan(rid)
    if k == 1:
        run([os.path.join(SRC, "grade.py"), rid, os.path.join(TASKS, agent + ".output")])
        if len(turns) > 1:
            run([os.path.join(SRC, "glab_project.py"), "deliver", rid, "2"])     # snapshots turn 1, then delivers
    else:
        run([os.path.join(SRC, "glab_project.py"), "snapshot", rid, str(k)])
    later = [t for t in turns if t > k]
    if later:
        nxt = later[0]
        print(f"\nNEXT: send turn {nxt} to {rid} ({agent}):\n" + open(os.path.join(PROMPTS, MSG[nxt]), encoding="utf8").read().strip())
        return
    if 4 in turns:
        run([os.path.join(SRC, "spec_grid.py"), rid])
    if len(turns) > 1:
        run([os.path.join(SRC, "grade_project.py"), rid])
    print(f"\nCOMPLETE: {rid}")


def gate(rid, rnd):
    agent, _ = plan(rid)
    out = run([os.path.join(SRC, "run_gate.py"), rid, str(rnd)])
    if out.startswith("exit 0"):
        print(f"\nPASS: {rid} round {rnd}; now run: clean_turn.py done {rid} 1")
    else:
        rep = out.split("\n", 1)[1].strip()
        print(f"\nRETURN to {rid} ({agent}):\n" + open(GATE_RETURN, encoding="utf8").read().strip().replace("{REPORT}", rep))


if __name__ == "__main__":
    cmd, rid, k = sys.argv[1], sys.argv[2], int(sys.argv[3])
    {"done": done, "gate": gate}[cmd](rid, k)
