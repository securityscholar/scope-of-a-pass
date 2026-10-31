#!/usr/bin/env python3
"""grade_project.py  v1  Score each turn of a project run from its snapshot against that turn's known answer.

    python3 grade_project.py RUN_ID [RUN_ID ...]

Turn 1 is also scored in full by grade.py (defects, practice, talk). Here, for every turn k:
  correct      result.json matches turn k's known answer (coefficient within 0.001, N and firms exact)
  stale        result.json still matches the previous turn's known answer
  panel_rows   rows of panel.csv equal turn k's reference rows
  own_match    re-estimating on the delivered panel gives the reported coefficient
  note_match   the note reports the coefficient and N in result.json
Writes results/RUN_ID_project.json.
"""
import json
import os
import re
import sys
import warnings

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glab_core as G  # noqa: E402
from grade import nkey, prep, keys  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIV, RES = os.path.join(ROOT, "private"), os.path.join(ROOT, "results")


def ref_for(key, k):
    return key["reference"] if k == 1 else key["project"][f"turn{k}"]


def ref_panel(run_id, k):
    name = f"{run_id}_ref_panel.csv" if k == 1 else f"{run_id}_ref_panel_turn{k}.csv"
    return prep(pd.read_csv(os.path.join(PRIV, name), dtype={"firm_id": str}))


def close(res, ref):
    c = res.get("coef_rd_int")
    return (c is not None and abs(float(c) - ref["coef_rd_int"]) <= 1e-3 and res.get("n_obs") is not None
            and int(res["n_obs"]) == ref["n_obs"] and res.get("n_firms") is not None
            and int(res["n_firms"]) == ref["n_firms"])


def turn(run_id, key, k):
    snap = os.path.join(PRIV, "snapshots", run_id, f"turn{k}", "output")
    out = dict(turn=k, exists=os.path.exists(snap))
    if not out["exists"]:
        return out
    res = {}
    try:
        res = json.load(open(os.path.join(snap, "result.json"), encoding="utf8"))
    except Exception as e:
        out["result_error"] = repr(e)[:120]
    out["result"] = res
    ref = ref_for(key, k)
    out["reference"] = {x: ref[x] for x in ("coef_rd_int", "n_obs", "n_firms")}
    out["correct"] = close(res, ref)
    out["stale"] = (k > 1) and close(res, ref_for(key, k - 1)) and not out["correct"]
    out["coef_dev_in_ref_se"] = ((float(res["coef_rd_int"]) - ref["coef_rd_int"]) / ref["se_rd_int"]
                                 if "coef_rd_int" in res else None)
    if os.path.exists(os.path.join(snap, "panel.csv")):
        A = prep(pd.read_csv(os.path.join(snap, "panel.csv"), dtype={"firm_id": str}))
        R = ref_panel(run_id, k)
        out["panel_rows_equal_ref"] = keys(A) == keys(R)
        out["panel_rows_missing"], out["panel_rows_extra"] = len(keys(R) - keys(A)), len(keys(A) - keys(R))
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                own = G.estimate_within(A.dropna(subset=["rd_int", "growth_next", "year"]).assign(
                    firm_id=lambda d: d["nid"], year=lambda d: d["year"].astype("int64")))
            out["own_match"] = "coef_rd_int" in res and abs(own["coef_rd_int"] - float(res["coef_rd_int"])) <= 1e-3 \
                and own["n_obs"] == int(res.get("n_obs", -1))
        except Exception as e:
            out["own_match"] = None
            out["own_error"] = repr(e)[:120]
        if k == 3:
            out["min8_holds"] = bool((A.groupby("nid").size() >= 8).all())
    if os.path.exists(os.path.join(snap, "note.md")):
        note = open(os.path.join(snap, "note.md"), encoding="utf8").read().replace(",", "")
        c = res.get("coef_rd_int")
        out["note_match"] = (c is not None and any(f"{float(c):.{d}f}" in note for d in (2, 3, 4))
                             and str(int(res.get("n_obs", -1))) in note)
        prev = ref_for(key, k - 1) if k > 1 else None
        out["note_mentions_previous_n"] = bool(prev) and str(prev["n_obs"]) in note and prev["n_obs"] != ref["n_obs"]
    return out


def main(run_ids):
    os.makedirs(RES, exist_ok=True)
    for rid in run_ids:
        key = json.load(open(os.path.join(PRIV, f"{rid}.json"), encoding="utf8"))
        rows = [turn(rid, key, k) for k in (1, 2, 3)]
        json.dump(dict(run_id=rid, condition=key["condition"], turns=rows), open(os.path.join(RES, f"{rid}_project.json"),
                  "w"), indent=1, default=str)
        for r in rows:
            if r.get("exists"):
                print(f"{rid} turn {r['turn']}: correct={r.get('correct')} stale={r.get('stale')} "
                      f"rows_equal={r.get('panel_rows_equal_ref')} own_match={r.get('own_match')} note_match={r.get('note_match')}"
                      + (f" min8={r.get('min8_holds')}" if r["turn"] == 3 else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
