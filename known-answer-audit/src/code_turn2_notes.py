#!/usr/bin/env python3
"""code_turn2_notes.py  v3  Hand coding of the 26 turn-2 notes written after the revised vendor file with copied
values: whether the note reports how many values the revision added (counted against an earlier vintage). Each
coded note is located by a phrase copied from it, and the full line holding that phrase is saved as the evidence.
A note with no phrase reports no count. Read by every note before coding (2026-10-28). The 26 notes are kept in
results/vigilance/notes/ (copied there from the run snapshots when those exist). Writes
results/vigilance/turn2_notes_coded.csv.
v2: codes the released copies of the notes.
v3: VA05 is not coded as reporting the count: its 57 positive values are counted against the oldest file, and the
note never mentions the revision (independent check, 2026-10-28).

    python3 code_turn2_notes.py
"""
import os
import re
import shutil

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, "private", "snapshots")
OUT = os.path.join(ROOT, "results", "vigilance")
NOTES = os.path.join(OUT, "notes")
os.makedirs(NOTES, exist_ok=True)
PHRASE = {  # run: phrase in the note that reports the count of added values
    "Q01": "fills 66 earlier blanks", "Q02": "fills 61 cells", "Q03": "fills 52 blank firm-years",
    "S03": "fills 52 blank firm-years", "VA02": "adds 31 firm-years", "VA03": "adds 39 firm-years",
    "VA04": "on 32 fewer firm-years", "VA07": "gains 30 firm-years",
    "VA10": "fills 63 R&D values", "VB05": "fills 57 firm-years", "VB08": "58 blanks are filled",
    "VB10": "Of the 46 additions",
}
EX = pd.read_csv(os.path.join(OUT, "all_exposures.csv"))
rows = []
for r in EX.itertuples():
    src, dst = os.path.join(SNAP, r.run, "turn2", "output", "note.md"), os.path.join(NOTES, f"{r.run}_turn2_note.md")
    if os.path.exists(src):
        shutil.copyfile(src, dst)
    note = open(dst, encoding="utf8").read()
    ph = PHRASE.get(r.run)
    line = ""
    if ph:
        hit = [ln for ln in note.splitlines() if ph in ln]
        assert len(hit) == 1, (r.run, ph, len(hit))
        line = " ".join(hit[0].split())
    rows.append(dict(run=r.run, flagged=r.flagged, left_out=r.left_out, matched_known_answer=r.matched,
                     reports_count_added=bool(ph), evidence=line))
D = pd.DataFrame(rows)
D.to_csv(os.path.join(OUT, "turn2_notes_coded.csv"), index=False)
print(D[["run", "flagged", "left_out", "matched_known_answer", "reports_count_added"]].to_string(index=False))
s = D[~D["flagged"]]
print(f"\nsilent runs {len(s)}; of them report the count of added values: {int(s['reports_count_added'].sum())}")
