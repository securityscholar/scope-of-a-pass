#!/usr/bin/env python3
"""make_runs.py  v3  Build agent run folders for the four regimes and the private answer keys.

    python3 make_runs.py RUN_ID CONDITION SEED [RUN_ID CONDITION SEED ...]

CONDITION is C0 (plain), C1 (written rules), C2 (rules + tools the agent may run), C3 (rules + tools +
gate run by the environment). Each run gets its own instance: the seed is moved up in steps of 1,000
until the reference sample has no firm with a single row.
v3: every instance's files pass screen_copies.py before a run folder is written; a failure stops the build.
"""
import json
import os
import shutil
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glab_core as G  # noqa: E402
import screen_copies as SC  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS, RUNS, PRIV = (os.path.join(ROOT, d) for d in ("assets", "runs", "private"))
ADD = {
    "C0": "",
    "C1": "\n## Working rules\n\nFollow the rules in RULES.md.\n",
    "C2": ("\n## Working rules and tools\n\nFollow the rules in RULES.md. guards.py implements each rule as a function "
           "(import it in analysis.py), and gate.py checks a finished submission: run `python gate.py` from this "
           "folder. Use them as you see fit.\n"),
    "C3": ("\n## Working rules and tools\n\nFollow the rules in RULES.md. guards.py implements each rule as a function "
           "(import it in analysis.py), and gate.py checks a finished submission. When you report that you are done, "
           "gate.py runs automatically on this folder. A submission that fails is returned to you with the gate's "
           "report, and only a passing submission is accepted.\n"),
}
EXTRA = {"C0": [], "C1": ["RULES.md"], "C2": ["RULES.md", "guards.py", "gate.py"],
         "C3": ["RULES.md", "guards.py", "gate.py"]}


def grading_frame(rb, truth):
    """One row per financials firm-year with every attribute the grader needs, built from the files."""
    fin = rb["financials"].copy()
    idm = dict(zip(rb["id_history"]["old_id"], rb["id_history"]["firm_id"]))

    def vend(df):
        d = df.copy()
        d["firm_id"] = d["firm_id"].map(lambda x: idm.get(x, x))
        d["rd_m"] = np.where(d["fyear"] <= G.UNIT_SWITCH - 1, d["rd"] / 1000.0, d["rd"])
        return d[["firm_id", "fyear", "rd_m", "rd_intensity"]]

    cur = vend(rb["rd_new"]).rename(columns={"rd_m": "rd_cur", "rd_intensity": "rdi_sales_cur"})
    old = vend(rb["rd_old"]).rename(columns={"rd_m": "rd_old", "rd_intensity": "rdi_sales_old"})
    f = fin.merge(cur, on=["firm_id", "fyear"], how="left", validate="1:1")
    f = f.merge(old, on=["firm_id", "fyear"], how="left", validate="1:1")
    f["rdi_assets_cur"] = f["rd_cur"] / f["assets"]
    f["rdi_assets_old"] = f["rd_old"] / f["assets"]
    f["rd_missing_cur"] = f["rd_cur"].isna()
    f["corrected"] = (~f["rd_missing_cur"]) & ((f["rd_old"] - f["rd_cur"]).abs() > 1e-6 * f["rd_cur"].abs().clip(lower=1e-9))
    firms = rb["firms"].sort_values(["firm_id", "as_of"])
    latest = firms.groupby("firm_id").tail(1).set_index("firm_id")
    f["class_t"] = G.size_class(f["assets"])
    f["class_static"] = f["firm_id"].map(latest["size_class"])
    f["industry_cur"] = f["firm_id"].map(latest["industry"])
    counts = firms.groupby("firm_id").size()
    f["changer"] = f["firm_id"].map(counts).fillna(1) > 1
    f["idchanger"] = f["firm_id"].isin(set(rb["id_history"]["firm_id"]))
    yrs = set(zip(fin["firm_id"], fin["fyear"]))
    f["has_next"] = [(a, b + 1) in yrs for a, b in zip(f["firm_id"], f["fyear"])]
    f["next_gap"] = [((a, b + 1) not in yrs) and ((a, b + 2) in yrs) for a, b in zip(f["firm_id"], f["fyear"])]
    jumps = set((a, b) for a, b in truth["jump_rows"])
    f["is_jump"] = [(a, b) in jumps for a, b in zip(f["firm_id"], f["fyear"])]
    f["to_fin"] = f["firm_id"].isin(set(truth["to_fin"]))
    f["from_fin"] = f["firm_id"].isin(set(truth["from_fin"]))
    return f.rename(columns={"fyear": "year"})


def choose_instance(seed):
    import tempfile
    for k in range(20):
        s = seed + 1000 * k
        files, truth = G.generate(s, n_firms=int(os.environ.get("GLAB_NFIRMS", "400")))
        with tempfile.TemporaryDirectory() as d:
            G.write_files(files, d)
            SC.require_clean([d])
            rb = G.read_back(d)
        ref_panel = G.build_panel(rb)
        if ref_panel.groupby("firm_id").size().min() >= 2:
            return s, files, truth, rb, ref_panel
    raise RuntimeError(f"no valid instance near seed {seed}")


def make_run(run_id, cond, seed):
    if cond not in ADD:
        raise ValueError(f"unknown condition {cond}")
    s, files, truth, rb, ref_panel = choose_instance(seed)
    ref = G.estimate_within(ref_panel)
    folder = os.path.join(RUNS, run_id)
    if os.path.exists(folder):
        raise FileExistsError(f"{folder} exists; runs are never overwritten")
    G.write_files(files, os.path.join(folder, "data"))
    version = os.environ.get("GLAB_VERSION", "v1")
    readme = {"v1": "README.md", "v2": "README_v2.md"}[version]
    shutil.copy2(os.path.join(ASSETS, readme), os.path.join(folder, "data", "README.md"))
    task = open(os.path.join(ASSETS, "TASK_base.md"), encoding="utf8").read() + ADD[cond]
    with open(os.path.join(folder, "TASK.md"), "w", encoding="utf8") as fh:
        fh.write(task)
    for name in EXTRA[cond]:
        shutil.copy2(os.path.join(ASSETS, name), os.path.join(folder, name))
    os.makedirs(os.path.join(folder, "output"))
    frame = grading_frame(rb, truth)
    frame.to_parquet(os.path.join(PRIV, f"{run_id}_frame.parquet"), index=False)
    ref_panel.to_csv(os.path.join(PRIV, f"{run_id}_ref_panel.csv"), index=False)
    key = dict(run_id=run_id, condition=cond, version=version, n_firms=int(os.environ.get("GLAB_NFIRMS", "400")), seed_requested=int(seed), seed=int(s), reference=ref,
               truth={k: v for k, v in truth.items() if not isinstance(v, list)},
               files_md5={n: __import__("hashlib").md5(open(os.path.join(folder, n), "rb").read()).hexdigest()
                          for n in EXTRA[cond] if n.endswith(".py")})
    with open(os.path.join(PRIV, f"{run_id}.json"), "w", encoding="utf8") as fh:
        json.dump(key, fh, indent=1)
    print(f"{run_id} {cond} seed {s}: reference coef {ref['coef_rd_int']:.4f} se {ref['se_rd_int']:.4f} "
          f"n {ref['n_obs']} firms {ref['n_firms']} full_rank {ref['full_rank']}  -> {folder}")
    return key


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 0 or len(a) % 3:
        sys.exit(__doc__)
    for i in range(0, len(a), 3):
        make_run(a[i], a[i + 1], int(a[i + 2]))
