import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from guards import *

T = {"firm_id": str, "old_id": str}
firms = g_read("firms.csv", dtype=T)
fin = g_read("financials.csv", dtype=T)
rd = g_read("rd_vendor_2023-09-30.csv", dtype=T)
idh = g_read("id_history.csv", dtype=T)

n0 = len(firms)
firms = firms.sort_values(["firm_id", "as_of"]).groupby("firm_id").tail(1)
g_rows(n0, firms, "firms: latest as_of row per firm", "name-changers are listed once per name")
g_key(firms, ["firm_id"], "firms")

idmap = dict(zip(idh["old_id"], idh["firm_id"]))
rd["firm_id"] = rd["firm_id"].map(lambda x: idmap.get(x, x))
rd["rd"] = np.where(rd["fyear"] <= 2014, rd["rd"] / 1000.0, rd["rd"])
g_scale(rd, "rd", "fyear")

n0 = len(fin); fin = fin[fin["fyear"] <= 2022]; g_rows(n0, fin, "financials through FY2022", "FY2023 is year to date")
g_complete(fin, "fyear", "financials.csv")
n0 = len(rd); rd = rd[rd["fyear"] <= 2022]; g_rows(n0, rd, "vendor through FY2022", "FY2023 is year to date")
g_complete(rd, "fyear", "rd_vendor_2023-09-30.csv")
fin = g_lead(fin, "firm_id", "fyear", "sales", 1, "sales_next")

p = g_merge(fin, rd[["firm_id", "fyear", "rd"]], on=["firm_id", "fyear"], how="left", left_label="financials",
            right_label="rd_vendor", left_unique=True, right_unique=True)
p = g_merge(p, firms[["firm_id", "industry"]], on="firm_id", how="left", left_label="panel", right_label="firms")
n0 = len(p); p = p[(p["industry"] != "Finance") & (p["fyear"] >= 2010)]; g_rows(n0, p, "sample", "drop Finance, keep FY2010 on")
p["rd_int"] = p["rd"] / p["assets"]
p["growth_next"] = p["sales_next"] / p["sales"] - 1
p["size_class_t"] = np.where(p["assets"] >= 1000, "large", np.where(p["assets"] >= 100, "medium", "small"))
n0 = len(p); p = p.dropna(subset=["rd_int", "growth_next"]); g_rows(n0, p, "complete cases", "rd or t+1 sales missing")
g_scale(p, "rd_int", "fyear")
p = p.rename(columns={"fyear": "year"})
p[["firm_id", "year", "rd_int", "growth_next", "size_class_t"]].to_csv("output/panel.csv", index=False)
d = p.copy()
d["cls_medium"] = (d["size_class_t"] == "medium").astype(float); d["cls_large"] = (d["size_class_t"] == "large").astype(float)
fit = smf.ols("growth_next ~ rd_int + cls_medium + cls_large + C(firm_id) + C(year)", data=d).fit(
    cov_type="cluster", cov_kwds={"groups": pd.factorize(d["firm_id"])[0]})
res = dict(coef_rd_int=float(fit.params["rd_int"]), se_rd_int=float(fit.bse["rd_int"]), n_obs=int(fit.nobs),
           n_firms=int(d["firm_id"].nunique()))
json.dump(res, open("output/result.json", "w"))
open("output/note.md", "w").write(f"Coefficient on rd_int: {res['coef_rd_int']:.3f} (SE {res['se_rd_int']:.3f}), N = {res['n_obs']}.\n")
print(res)
