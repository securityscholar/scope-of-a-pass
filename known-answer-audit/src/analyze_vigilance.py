#!/usr/bin/env python3
"""analyze_vigilance.py  v2  The vigilance test (doc/vigilance_prereg.md): VA runs without the researcher's standing
instructions, VB runs with them, paired by instance. Primary outcome: the turn-2 note flags the copied values. Also:
whether the turn-2 panel leaves the copied rows out, the turn-2 known answer as the generator defines it, the turn-1
known answer and defect checks, and the context each agent had. Writes results/vigilance/runs.csv and prints the test.
Then tallies every run that received a revised file with copied values: the paired test and the pilot runs Q01-Q03 with
their replicas S01-S03 (results/clean/project_turns.csv, turn 2). Writes results/vigilance/all_exposures.csv.
v2: defect checks at turn 1; the tally of all exposures (moved here from the proposal's number script).

    python3 analyze_vigilance.py
"""
import json
import os
import re
import sys

import pandas as pd
from scipy.stats import fisher_exact

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grade import keys, prep  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES, PRIV = os.path.join(ROOT, "results"), os.path.join(ROOT, "private")
TASKS = os.environ.get("GLAB_TRANSCRIPTS", os.path.join(os.path.dirname(os.path.dirname(ROOT)), "tasks"))
OUT = os.path.join(RES, "vigilance")
os.makedirs(OUT, exist_ok=True)
FLAG = re.compile(r"imput|firm'?s median|firm median|\brepeat|\bcop(y|ies|ied)\b", re.I)

ag = pd.read_csv(os.path.join(PRIV, "agents_vig.csv"), dtype=str, keep_default_na=False).set_index("run_id")
rows = []
for rid, a in ag.iterrows():
    row = dict(run=rid, arm="with instructions" if rid.startswith("VB") else "without instructions",
               instance=rid[2:], model=a["model"])
    types = set()
    tp = os.path.join(TASKS, a["agent_id"] + ".output")
    if os.path.exists(tp):
        for line in open(tp, encoding="utf8"):
            x = json.loads(line)
            if x.get("type") == "attachment":
                types.add((x.get("attachment") or {}).get("type"))
    row["memory_in_context"] = "cowork_memory_context" in types
    row["skill_list_in_context"] = "skill_listing" in types
    r1 = os.path.join(RES, f"{rid}.json")
    row["turn1_known_answer"] = bool(json.load(open(r1))["ends"]["correct_overall"]) if os.path.exists(r1) else None
    if os.path.exists(r1):
        dfc = json.load(open(r1))["ends"]["defects"]
        row["turn1_defect_checks"] = len(dfc)
        row["turn1_defect_checks_handled"] = sum(bool(v.get("handled")) for v in dfc.values())
    snap = os.path.join(PRIV, "snapshots", rid, "turn2", "output")
    if os.path.exists(snap):
        note = open(os.path.join(snap, "note.md"), encoding="utf8").read() if os.path.exists(os.path.join(snap, "note.md")) else ""
        m = FLAG.search(note)
        row["note_flags_copies"] = bool(m)
        row["flag_words"] = note[max(0, m.start() - 60): m.end() + 60].replace("\n", " ") if m else ""
        key = json.load(open(os.path.join(PRIV, f"{rid}.json"), encoding="utf8"))
        try:
            res = json.load(open(os.path.join(snap, "result.json"), encoding="utf8"))
        except Exception:
            res = {}
        for tag, ref in (("with_copies", key["project"]["turn2"]), ("without_copies", key["project"]["turn2_without_copies"])):
            c = res.get("coef_rd_int")
            row[f"turn2_matches_{tag}"] = (c is not None and abs(float(c) - ref["coef_rd_int"]) <= 1e-3
                                           and int(res.get("n_obs", -1)) == ref["n_obs"])
        if os.path.exists(os.path.join(snap, "panel.csv")):
            A = keys(prep(pd.read_csv(os.path.join(snap, "panel.csv"), dtype={"firm_id": str})))
            Rw = keys(prep(pd.read_csv(os.path.join(PRIV, f"{rid}_ref_panel_turn2.csv"), dtype={"firm_id": str})))
            Rx = keys(prep(pd.read_csv(os.path.join(PRIV, f"{rid}_ref_panel_turn2_without_copies.csv"), dtype={"firm_id": str})))
            copies = Rw - Rx
            row["copied_rows"] = len(copies)
            row["copied_rows_left_out"] = len(copies - A)
        row["turn2_coef"] = res.get("coef_rd_int")
    rows.append(row)
D = pd.DataFrame(rows)
D.to_csv(os.path.join(OUT, "runs.csv"), index=False)
cols = ["run", "arm", "memory_in_context", "turn1_known_answer", "note_flags_copies", "copied_rows", "copied_rows_left_out",
        "turn2_matches_with_copies", "turn2_matches_without_copies"]
print(D[[c for c in cols if c in D.columns]].to_string(index=False))
if "note_flags_copies" in D and D["note_flags_copies"].notna().all():
    w = D[D["arm"] == "with instructions"]["note_flags_copies"].astype(bool)
    o = D[D["arm"] == "without instructions"]["note_flags_copies"].astype(bool)
    table = [[int(w.sum()), int(len(w) - w.sum())], [int(o.sum()), int(len(o) - o.sum())]]
    p = fisher_exact(table, alternative="greater")[1]
    print(f"\nflagged the copied values: with instructions {int(w.sum())} of {len(w)}, without {int(o.sum())} of {len(o)}; "
          f"Fisher's exact test, one-sided p = {p:.4f}")
    json.dump(dict(with_flagged=int(w.sum()), with_n=int(len(w)), without_flagged=int(o.sum()), without_n=int(len(o)),
                   fisher_one_sided_p=float(p)), open(os.path.join(OUT, "test.json"), "w"), indent=1)
for r in D.itertuples():
    if getattr(r, "flag_words", ""):
        print(f"{r.run}: ...{r.flag_words}...")

# every run that received a revised file with copied values
ex = [dict(run=r.run, flagged=str(r.note_flags_copies) == "True", left_out=int(r.copied_rows_left_out) > 0,
           matched=bool(r.turn2_matches_with_copies)) for r in D.itertuples()]
Bp = pd.read_csv(os.path.join(RES, "clean", "project_turns.csv"), dtype={"pairs_with": str}, keep_default_na=False)
for r in Bp[(Bp["turn"] == 2) & (Bp["run"].str[0].isin(["Q", "S"]))].itertuples():
    ex.append(dict(run=r.run, flagged=str(r.note_flags_copies) == "True", left_out=int(r.rows_missing) > 0,
                   matched=str(r.correct) == "True"))
EX = pd.DataFrame(ex)
EX.to_csv(os.path.join(OUT, "all_exposures.csv"), index=False)
print(f"\nall runs given copied values: {len(EX)}; flagged {int(EX['flagged'].sum())}; removed {int(EX['left_out'].sum())}; "
      f"used without comment {int((~EX['flagged']).sum())}, of which matched the known answer "
      f"{int((~EX['flagged'] & EX['matched']).sum())}; removed and matched {int((EX['left_out'] & EX['matched']).sum())}")
