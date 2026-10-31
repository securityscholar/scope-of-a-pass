"""gate.py: checks a finished submission against the working rules. Run from the task folder:

    python gate.py

It reruns analysis.py in a fresh copy of the folder and checks the rerun and the submitted outputs.
Exit code 0 means the submission passes.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
COLS = ["firm_id", "year", "rd_int", "growth_next", "size_class_t"]
KEYS = ["coef_rd_int", "se_rd_int", "n_obs", "n_firms"]
NEED_RULES = {1: "read (rule 1)", 2: "merge (rule 2)", 4: "lead or lag on grid (rule 4)", 5: "scale (rule 5)",
              6: "complete periods (rule 6)"}


def load(folder):
    panel = pd.read_csv(os.path.join(folder, "output", "panel.csv"), dtype={"firm_id": str})
    with open(os.path.join(folder, "output", "result.json"), encoding="utf8") as fh:
        res = json.load(fh)
    return panel, res


def same_frames(a, b):
    if a.shape != b.shape or list(a.columns) != list(b.columns):
        return False
    for c in a.columns:
        if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
            if not np.allclose(a[c].to_numpy(float), b[c].to_numpy(float), rtol=0, atol=1e-9, equal_nan=True):
                return False
        elif not (a[c].astype(str).to_numpy() == b[c].astype(str).to_numpy()).all():
            return False
    return True


def main():
    fails, notes = [], []
    need = [os.path.join(HERE, "analysis.py")] + [os.path.join(OUT, f) for f in ("panel.csv", "result.json", "note.md")]
    missing = [os.path.relpath(p, HERE) for p in need if not os.path.exists(p)]
    if missing:
        print("FAIL G1 missing files: " + ", ".join(missing))
        print("GATE: FAIL")
        return 1
    panel, res = load(HERE)
    if [c for c in COLS if c not in panel.columns]:
        fails.append("G1 panel.csv lacks columns: " + ", ".join(c for c in COLS if c not in panel.columns))
    if [k for k in KEYS if k not in res]:
        fails.append("G1 result.json lacks keys: " + ", ".join(k for k in KEYS if k not in res))

    # G2 rerun analysis.py in a fresh copy of the folder
    tmp = tempfile.mkdtemp(prefix="gate_")
    try:
        for item in os.listdir(HERE):
            if item in ("output", "__pycache__"):
                continue
            src = os.path.join(HERE, item)
            (shutil.copytree if os.path.isdir(src) else shutil.copy2)(src, os.path.join(tmp, item))
        os.makedirs(os.path.join(tmp, "output"))
        run = subprocess.run([sys.executable, "analysis.py"], cwd=tmp, capture_output=True, text=True, timeout=900)
        if run.returncode != 0:
            fails.append("G2 analysis.py fails when rerun in a fresh folder; last lines:\n    "
                         + "\n    ".join((run.stdout + run.stderr).strip().splitlines()[-8:]))
        else:
            p2, r2 = load(tmp)
            a = panel.sort_values(["firm_id", "year"]).reset_index(drop=True)
            b = p2.sort_values(["firm_id", "year"]).reset_index(drop=True)
            same = same_frames(a, b)
            if not same:
                fails.append("G2 the submitted panel.csv differs from the one analysis.py produces")
            for k in KEYS:
                if k in res and k in r2 and abs(float(res[k]) - float(r2[k])) > 1e-9:
                    fails.append(f"G2 result.json {k} = {res[k]} but analysis.py produces {r2[k]}")
            # G3 the rerun's check log
            logp = os.path.join(tmp, "output", "checks.jsonl")
            recs = [json.loads(x) for x in open(logp, encoding="utf8")] if os.path.exists(logp) else []
            if not recs:
                fails.append("G3 the rerun wrote no output/checks.jsonl (guards.py was not used)")
            for rule, label in NEED_RULES.items():
                if recs and not any(r.get("rule") == rule for r in recs):
                    fails.append(f"G3 no {label} check in the rerun's checks.jsonl")
            bad = [r for r in recs if not r.get("ok", True)]
            if bad:
                fails.append(f"G3 {len(bad)} failed check(s) were caught and ignored, e.g. rule {bad[0].get('rule')} "
                             f"{bad[0].get('check')}")
            for r in recs:
                if r.get("check") == "merge" and r.get("reason"):
                    notes.append(f"merge {r.get('left')} x {r.get('right')} passed above the unmatched limit with "
                                 f"reason: {r.get('reason')}")
    except subprocess.TimeoutExpired:
        fails.append("G2 analysis.py did not finish within 15 minutes when rerun")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # G4 the submitted panel
    if {"firm_id", "year"} <= set(panel.columns):
        nd = int(panel.duplicated(["firm_id", "year"]).sum())
        if nd:
            fails.append(f"G4 panel.csv has {nd} duplicated firm_id-year rows")
    if {"rd_int", "year"} <= set(panel.columns):
        med = panel.groupby("year")["rd_int"].median()
        ratio = (med / med.shift(1)).dropna()
        brk = ratio[(ratio > 10) | (ratio < 0.1)]
        if not brk.empty:
            fails.append("G4 rd_int has a break in scale between years: " + ", ".join(f"{k}: x{v:.4g}" for k, v in brk.items()))
    # G5 superseded files named in analysis.py
    man = pd.read_csv(os.path.join(HERE, "data", "MANIFEST.csv"), dtype=str, keep_default_na=False)
    code = open(os.path.join(HERE, "analysis.py"), encoding="utf8").read()
    for f in man.loc[man["status"] != "current", "file"]:
        if f in code:
            fails.append(f"G5 analysis.py names a superseded file: {f}")
    # G6 the note reports the numbers in result.json
    note = open(os.path.join(OUT, "note.md"), encoding="utf8").read().replace(",", "")
    if "coef_rd_int" in res:
        c = float(res["coef_rd_int"])
        if not any(f"{c:.{d}f}" in note for d in (2, 3, 4)):
            fails.append(f"G6 note.md does not report the coefficient in result.json ({c:.4f})")
    if "n_obs" in res and str(int(res["n_obs"])) not in note:
        fails.append(f"G6 note.md does not report n_obs from result.json ({int(res['n_obs'])})")

    for n in notes:
        print("NOTE " + n)
    for f in fails:
        print("FAIL " + f)
    print("GATE: " + ("PASS" if not fails else f"FAIL ({len(fails)} problem(s))"))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
