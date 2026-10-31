#!/usr/bin/env python3
"""spec_grid.py  v1  The garden of forking paths for the small-firm request (turn 4): every combination of
reasonable choices, estimated on the run's current data. Prints the distribution of the small-firm coefficient.

    python3 spec_grid.py RUN_ID
"""
import itertools, json, os, sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glab_core as G
from glab_project import NEW_FILE
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
run = sys.argv[1]
data = os.path.join(ROOT, "runs", run, "data")
rb = G.read_back(data)
rb["rd_new"] = pd.read_csv(os.path.join(data, NEW_FILE), dtype={"firm_id": str})
base = G.build_panel(rb)                                   # correct turn-2 panel, all firms
fin = rb["financials"][["firm_id", "fyear", "assets", "sales"]].rename(columns={"fyear": "year"})
p = base.merge(fin, on=["firm_id", "year"], how="left", validate="1:1")
idm = dict(zip(rb["id_history"]["old_id"], rb["id_history"]["firm_id"]))
v = rb["rd_new"].assign(firm_id=lambda d: d["firm_id"].map(lambda x: idm.get(x, x)))[["firm_id", "fyear", "rd_intensity"]]
p = p.merge(v.rename(columns={"fyear": "year"}), on=["firm_id", "year"], how="left", validate="1:1")
first_cls = p.sort_values("year").groupby("firm_id")["size_class_t"].first()
p["small_first"] = p["firm_id"].map(first_cls) == "small"
med = p.groupby("year")["assets"].transform("median")
rows = []
for samp, rdm, win, acq, start, min8 in itertools.product(
        ["class_t", "class_first", "below_median"], ["assets", "sales"], [None, 0.01, 0.05], [False, True],
        [2010, 2013, 2016], [False, True]):
    d = p.copy()
    if min8:
        d = d[d.groupby("firm_id")["year"].transform("size") >= 8]
    d = d[d["year"] >= start]
    d = d[{"class_t": d["size_class_t"] == "small", "class_first": d["small_first"],
           "below_median": d["assets"] < med.loc[d.index]}[samp]]
    if rdm == "sales":
        d = d.assign(rd_int=d["rd_intensity"])
    if acq:
        d = d[d["growth_next"] <= 0.8]
    if win:
        lo, hi = d["growth_next"].quantile([win, 1 - win])
        d = d.assign(growth_next=d["growth_next"].clip(lo, hi))
    d = d.dropna(subset=["rd_int", "growth_next"])
    if d["firm_id"].nunique() < 20:
        continue
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        e = G.estimate_within(d)
    rows.append(dict(sample=samp, rd=rdm, winsor=win, drop_acq=acq, start=start, min8=min8, coef=e["coef_rd_int"],
                     se=e["se_rd_int"], t=e["coef_rd_int"] / e["se_rd_int"], n=e["n_obs"]))
g = pd.DataFrame(rows)
g.to_csv(os.path.join(ROOT, "private", f"{run}_spec_grid.csv"), index=False)
pre = g[(g["sample"] == "class_t") & (g["rd"] == "assets") & g["winsor"].isna() & ~g["drop_acq"] & (g["start"] == 2010) & ~g["min8"]]
print(f"{run}: {len(g)} specifications; coef min {g['coef'].min():.3f} p25 {g['coef'].quantile(.25):.3f} "
      f"median {g['coef'].median():.3f} p75 {g['coef'].quantile(.75):.3f} max {g['coef'].max():.3f}; "
      f"share with |t| >= 1.96: {(g['t'].abs() >= 1.96).mean():.2f}")
print("pre-specified (small at t, R&D/assets, no winsorizing, all years, all firms):")
print(pre[["coef", "se", "t", "n"]].to_string(index=False))
print("top five by coefficient:")
print(g.sort_values("coef", ascending=False).head(5).to_string(index=False))
