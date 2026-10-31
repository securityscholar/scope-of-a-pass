#!/usr/bin/env python3
"""plant.py  v1  The vigilance test: the project version's revised vendor file with the pilot's copied values planted
on purpose (revised_vendor with noise_sd=0, so every newly reported value copies the firm's median ratio). The copy
screen is not applied, because the copies are the treatment. Writes the private files glab_project.prepare writes,
plus the turn-2 known answer and reference panel without the copied values.

    python3 plant.py RUN_ID [RUN_ID ...]
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glab_core as G  # noqa: E402
import glab_project as P  # noqa: E402


def plant(run_id):
    path = os.path.join(P.PRIV, f"{run_id}.json")
    key = json.load(open(path, encoding="utf8"))
    data = os.path.join(P.RUNS, run_id, "data")
    rb = G.read_back(data)
    r2, info = P.revised_vendor(rb["rd_new"], rb["financials"], key["seed"], noise_sd=0.0)
    copied = rb["rd_new"]["rd"].isna().to_numpy() & r2["rd"].notna().to_numpy()
    r2.to_csv(os.path.join(P.PRIV, f"{run_id}_turn2_{P.NEW_FILE}"), index=False)
    P.manifest2(data).to_csv(os.path.join(P.PRIV, f"{run_id}_turn2_MANIFEST.csv"), index=False)
    p2 = G.build_panel(dict(rb, rd_new=r2))
    r2x = r2.copy()
    r2x.loc[copied, ["rd", "rd_intensity"]] = np.nan
    p2x = G.build_panel(dict(rb, rd_new=r2x))
    n = p2.groupby("firm_id")["year"].transform("size")
    p3 = p2[n >= P.MIN_ROWS].reset_index(drop=True)
    key["project"] = dict(turn2=G.estimate_within(p2), turn3=G.estimate_within(p3),
                          turn2_without_copies=G.estimate_within(p2x),
                          revision=dict(info, copied_cells=int(copied.sum()),
                                        copied_rows_in_panel=int(len(p2) - len(p2x))))
    key["planted_copies"] = True
    p2.to_csv(os.path.join(P.PRIV, f"{run_id}_ref_panel_turn2.csv"), index=False)
    p3.to_csv(os.path.join(P.PRIV, f"{run_id}_ref_panel_turn3.csv"), index=False)
    p2x.to_csv(os.path.join(P.PRIV, f"{run_id}_ref_panel_turn2_without_copies.csv"), index=False)
    json.dump(key, open(path, "w", encoding="utf8"), indent=1)
    t2, tx = key["project"]["turn2"], key["project"]["turn2_without_copies"]
    print(f"{run_id}: copied cells {int(copied.sum())}, copied rows in panel {len(p2) - len(p2x)}; turn 2 with copies "
          f"{t2['coef_rd_int']:.4f} (n {t2['n_obs']}), without {tx['coef_rd_int']:.4f} (n {tx['n_obs']})")


if __name__ == "__main__":
    for rid in sys.argv[1:]:
        plant(rid)
