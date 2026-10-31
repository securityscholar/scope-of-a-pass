#!/usr/bin/env python3
"""replicate.py  v1  Build a run folder that repeats an earlier run exactly: the same instance (seed), codebook
version and regime, and for project runs the same revised vendor file and known answers the earlier agent had.
Every delivered file is checked byte for byte against the earlier run's files; any difference stops the build.

    python3 replicate.py NEW_ID=OLD_ID [NEW_ID=OLD_ID ...]

Used for the clean arm: the same tasks without the researcher's standing instructions in the agent's context.
"""
import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_runs as M  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS, PRIV = os.path.join(ROOT, "runs"), os.path.join(ROOT, "private")
TURN2 = "rd_vendor_2024-02-15.csv"


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def replicate(new, old):
    k_old = json.load(open(os.path.join(PRIV, f"{old}.json"), encoding="utf8"))
    os.environ["GLAB_VERSION"] = k_old.get("version") or "v1"
    os.environ["GLAB_NFIRMS"] = str(k_old.get("n_firms", 400))
    k_new = M.make_run(new, k_old["condition"], k_old["seed_requested"])
    if k_new["seed"] != k_old["seed"]:
        raise RuntimeError(f"{new}: seed {k_new['seed']} differs from {old}'s {k_old['seed']}")
    d_new, d_old = os.path.join(RUNS, new, "data"), os.path.join(RUNS, old, "data")
    project = "project" in k_old
    checked = []
    for f in sorted(os.listdir(d_new)):
        if project and f == "MANIFEST.csv":
            continue            # the earlier run's MANIFEST was replaced at turn 2; the generator's copy is compared below
        if md5(os.path.join(d_new, f)) != md5(os.path.join(d_old, f)):
            raise RuntimeError(f"{new}: data/{f} differs from {old}")
        checked.append(f)
    for f in ("TASK.md",) + tuple(M.EXTRA[k_old["condition"]]):
        if md5(os.path.join(RUNS, new, f)) != md5(os.path.join(RUNS, old, f)):
            raise RuntimeError(f"{new}: {f} differs from {old}")
        checked.append(f)
    a, b = k_new["reference"], k_old["reference"]   # earlier keys were computed with the dummy-variable estimator
    if (a["n_obs"], a["n_firms"]) != (b["n_obs"], b["n_firms"]) or abs(a["coef_rd_int"] - b["coef_rd_int"]) > 1e-9 \
            or abs(a["se_rd_int"] / b["se_rd_int"] - 1) > 1e-6:
        raise RuntimeError(f"{new}: known answer differs from {old}: {a} vs {b}")
    if project:
        # the revised file and the later known answers are the ones the earlier agent had
        if md5(os.path.join(PRIV, f"{old}_turn2_{TURN2}")) != md5(os.path.join(d_old, TURN2)):
            raise RuntimeError(f"{old}: private turn-2 file is not the file its agent saw")
        for suffix in (f"turn2_{TURN2}", "turn2_MANIFEST.csv", "ref_panel_turn2.csv", "ref_panel_turn3.csv"):
            shutil.copy2(os.path.join(PRIV, f"{old}_{suffix}"), os.path.join(PRIV, f"{new}_{suffix}"))
        if md5(os.path.join(PRIV, f"{new}_turn2_MANIFEST.csv")) != md5(os.path.join(d_old, "MANIFEST.csv")):
            raise RuntimeError(f"{old}: private turn-2 MANIFEST is not the one its agent saw")
        k_new["project"] = k_old["project"]
    k_new["replicates"] = old
    json.dump(k_new, open(os.path.join(PRIV, f"{new}.json"), "w", encoding="utf8"), indent=1)
    print(f"{new} = {old}: {k_old['condition']} {os.environ['GLAB_VERSION']} seed {k_new['seed']}; identical: {', '.join(checked)}"
          + ("; turn-2 file, MANIFEST and known answers copied" if project else ""))


if __name__ == "__main__":
    for pair in sys.argv[1:]:
        new, old = pair.split("=")
        replicate(new, old)
