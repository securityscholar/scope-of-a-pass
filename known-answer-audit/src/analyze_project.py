#!/usr/bin/env python3
"""analyze_project.py  v1  Turn-by-regime table from results/*_project.json.

    python3 analyze_project.py [RUN_PREFIX ...]
"""
import glob
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def main(prefixes):
    rows = []
    for p in sorted(glob.glob(os.path.join(RES, "*_project.json"))):
        r = json.load(open(p, encoding="utf8"))
        if prefixes and not r["run_id"].startswith(tuple(prefixes)):
            continue
        for t in r["turns"]:
            if t.get("exists"):
                rows.append(dict(run=r["run_id"], regime=r["condition"], turn=t["turn"], correct=t.get("correct"),
                                 stale=t.get("stale"), rows_equal=t.get("panel_rows_equal_ref"),
                                 own_match=t.get("own_match"), note_match=t.get("note_match"),
                                 note_prev_n=t.get("note_mentions_previous_n"), dev_se=t.get("coef_dev_in_ref_se")))
    d = pd.DataFrame(rows)
    if d.empty:
        print("no project results")
        return
    d.to_csv(os.path.join(RES, "project_long.csv"), index=False)
    for col in ["correct", "stale", "rows_equal", "own_match", "note_match", "note_prev_n"]:
        t = d.groupby(["turn", "regime"])[col].agg(lambda s: f"{int(s.fillna(False).astype(bool).sum())}/{s.notna().sum()}")
        print(f"\n{col} (k/n) by turn and regime")
        print(t.unstack("regime").to_string())
    print()
    print(d.sort_values(["run", "turn"]).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1:])
