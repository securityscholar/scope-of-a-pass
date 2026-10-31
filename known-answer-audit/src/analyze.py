#!/usr/bin/env python3
"""analyze.py  v1  Tables from graded runs.

    python3 analyze.py [RUN_PREFIX ...]

Reads results/*.json and private/agents.csv. Prints a run table, a defect-by-regime table, the
talk-versus-end table, and saves results/runs_long.csv and results/defects_long.csv.
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES, PRIV = os.path.join(ROOT, "results"), os.path.join(ROOT, "private")
DEFECTS = ["dup", "idchange", "units", "vintage", "grid", "partial", "lookahead", "label"]
COVERED = ["dup", "idchange", "units", "vintage", "grid", "partial"]
UNCOVERED = ["lookahead", "label"]
NEAR = ["zeros", "jumps"]


def load(prefixes):
    rows, drows = [], []
    agents = pd.read_csv(os.path.join(PRIV, "agents.csv"), dtype=str).set_index("run_id")
    for p in sorted(glob.glob(os.path.join(RES, "*.json"))):
        rid = os.path.basename(p)[:-5]
        if prefixes and not any(rid.startswith(x) for x in prefixes):
            continue
        r = json.load(open(p, encoding="utf8"))
        e, pr, t, au = r["ends"], r["practice"], r["talk"], r.get("audit", {})
        d = e.get("defects", {})
        hv = {k: d.get(k, {}).get("handled") for k in DEFECTS + NEAR}
        cov = [hv[k] for k in COVERED if hv[k] is not None]
        unc = [hv[k] for k in UNCOVERED if hv[k] is not None]
        nm = [hv[k] for k in NEAR if hv[k] is not None]
        gp = r.get("gate_posthoc") or {}
        mins = None
        if au.get("first") and au.get("last"):
            mins = (pd.Timestamp(au["last"]) - pd.Timestamp(au["first"])).total_seconds() / 60
        rows.append(dict(
            run=rid, regime=r["condition"], model=agents.loc[rid, "model"] if rid in agents.index else "",
            correct=e.get("correct_overall"), dev_se=e.get("coef_dev_in_ref_se"),
            n_ok=e.get("n_correct"), cov_ok=sum(cov), cov_n=len(cov), unc_ok=sum(unc), unc_n=len(unc),
            near_ok=sum(nm), near_n=len(nm), own_match=e.get("reported_matches_own_panel"),
            note_coef=t.get("reports_result_coef"), assure=t.get("assurance_words"),
            gate_out=gp.get("outputs_pass"), gate_all=gp.get("passed"), calls=au.get("n_tool_calls"),
            minutes=mins, banned=len(au.get("banned_tools") or {}), outside=len(au.get("outside_paths") or []),
            contam=sum((au.get("contamination_mentions") or {}).values())))
        for k in DEFECTS + NEAR:
            drows.append(dict(run=rid, regime=r["condition"], defect=k,
                              kind="covered" if k in COVERED else "uncovered" if k in UNCOVERED else "near miss",
                              handled=hv[k], talk=t.get(k), practice=pr.get(k, {}).get("final")
                              if isinstance(pr.get(k), dict) else None))
    return pd.DataFrame(rows), pd.DataFrame(drows)


def main(prefixes):
    runs, dl = load(prefixes)
    if runs.empty:
        print("no graded runs")
        return
    pd.set_option("display.width", 100)
    print("RUNS")
    show = runs.copy()
    show["dev_se"] = show["dev_se"].map(lambda x: f"{x:+.2f}" if pd.notna(x) else "")
    show["minutes"] = show["minutes"].map(lambda x: f"{x:.0f}" if pd.notna(x) else "")
    show["covered"] = show["cov_ok"].astype(str) + "/" + show["cov_n"].astype(str)
    show["uncov"] = show["unc_ok"].astype(str) + "/" + show["unc_n"].astype(str)
    show["near"] = show["near_ok"].astype(str) + "/" + show["near_n"].astype(str)
    print(show[["run", "regime", "model", "correct", "dev_se", "n_ok", "covered", "uncov", "near", "own_match",
                "note_coef", "gate_out", "calls", "minutes"]].to_string(index=False))
    print("\nAUDIT (banned tool calls, paths outside the run folder, mentions of the user's memory context)")
    print(runs[["run", "banned", "outside", "contam", "assure"]].to_string(index=False))
    print("\nDEFECT HANDLED, share of runs where the defect was exposed (k/n)")
    t = dl[dl["handled"].notna()].groupby(["defect", "regime"])["handled"].agg(["sum", "count"])
    t = (t["sum"].astype(int).astype(str) + "/" + t["count"].astype(str)).unstack("regime").reindex(DEFECTS + NEAR)
    print(t.fillna("").to_string())
    print("\nTALK VERSUS END (note mentions the issue x defect handled), all runs pooled")
    x = dl[dl["handled"].notna() & dl["talk"].notna()]
    ct = pd.crosstab(x["defect"], [x["talk"].map({True: "mentioned", False: "silent"}),
                                   x["handled"].map({True: "handled", False: "missed"})]).reindex(DEFECTS + NEAR)
    print(ct.fillna(0).astype(int).to_string())
    runs.to_csv(os.path.join(RES, "runs_long.csv"), index=False)
    dl.to_csv(os.path.join(RES, "defects_long.csv"), index=False)


if __name__ == "__main__":
    main(sys.argv[1:])
