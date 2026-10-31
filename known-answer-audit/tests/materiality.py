import sys, time, tempfile
sys.path.insert(0, "src")
import numpy as np, pandas as pd
import glab_core as G
pd.set_option("display.width", 120)
rows = []
for seed in [101, 102, 103]:
    t0 = time.time()
    files, truth = G.generate(seed)
    with tempfile.TemporaryDirectory() as d:
        G.write_files(files, d)
        rb = G.read_back(d)                      # what an analyst reads from disk
    ref_panel = G.build_panel(rb)
    ref = G.estimate(ref_panel)
    per_firm = ref_panel.groupby("firm_id").size()
    rows.append(dict(seed=seed, variant="REFERENCE", coef=ref["coef_rd_int"], se=ref["se_rd_int"], n=ref["n_obs"],
                     firms=ref["n_firms"], dcoef_se=0.0, dn=0, min_rows_per_firm=int(per_firm.min())))
    for k in ["dup", "idchange", "units", "vintage", "grid", "partial", "lookahead", "label", "zeros", "jumps"]:
        p = G.build_panel(rb, {k: False})
        e = G.estimate(p)
        rows.append(dict(seed=seed, variant=k, coef=e["coef_rd_int"], se=e["se_rd_int"], n=e["n_obs"],
                         firms=e["n_firms"], dcoef_se=(e["coef_rd_int"] - ref["coef_rd_int"]) / ref["se_rd_int"],
                         dn=e["n_obs"] - ref["n_obs"], min_rows_per_firm=int(p.groupby("firm_id").size().min())))
    print(f"seed {seed}: {time.time()-t0:.1f}s  truth: " + ", ".join(f"{k}={v}" for k, v in truth.items() if not isinstance(v, list)))
out = pd.DataFrame(rows)
print(out.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
