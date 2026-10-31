import json, numpy as np, pandas as pd, statsmodels.formula.api as smf
T = {"firm_id": str, "old_id": str}
firms = pd.read_csv("data/firms.csv", dtype=T); fin = pd.read_csv("data/financials.csv", dtype=T)
rd = pd.read_csv("data/rd_vendor_2023-09-30.csv", dtype=T); idh = pd.read_csv("data/id_history.csv", dtype=T)
firms = firms.sort_values(["firm_id", "as_of"]).groupby("firm_id").tail(1)
m = dict(zip(idh["old_id"], idh["firm_id"])); rd["firm_id"] = rd["firm_id"].map(lambda x: m.get(x, x))
rd["rd"] = np.where(rd["fyear"] <= 2014, rd["rd"] / 1000.0, rd["rd"])
fin = fin[fin["fyear"] <= 2022]
nxt = fin[["firm_id", "fyear", "sales"]].rename(columns={"sales": "sales_next"}); nxt["fyear"] -= 1
fin = fin.merge(nxt, on=["firm_id", "fyear"], how="left")
p = fin.merge(rd, on=["firm_id", "fyear"], how="left").merge(firms[["firm_id", "industry"]], on="firm_id", how="left")
p = p[(p["industry"] != "Finance") & (p["fyear"] >= 2010)].copy()
p["rd_int"] = p["rd"] / p["assets"]; p["growth_next"] = p["sales_next"] / p["sales"] - 1
p["size_class_t"] = np.where(p["assets"] >= 1000, "large", np.where(p["assets"] >= 100, "medium", "small"))
p = p.dropna(subset=["rd_int", "growth_next"]).rename(columns={"fyear": "year"})
p[["firm_id", "year", "rd_int", "growth_next", "size_class_t"]].to_csv("output/panel.csv", index=False)
d = p.copy(); d["m"] = (d["size_class_t"] == "medium") * 1.0; d["l"] = (d["size_class_t"] == "large") * 1.0
fit = smf.ols("growth_next ~ rd_int + m + l + C(firm_id) + C(year)", data=d).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d["firm_id"])[0]})
res = dict(coef_rd_int=float(fit.params["rd_int"]), se_rd_int=float(fit.bse["rd_int"]), n_obs=int(fit.nobs), n_firms=int(d["firm_id"].nunique()))
json.dump(res, open("output/result.json", "w"))
open("output/note.md", "w").write(f"I used the current vendor vintage, mapped pre-2016 identifiers, put R&D in millions, kept firm-years with a t+1 filing, dropped FY2023 (year to date). Coefficient {res['coef_rd_int']:.3f}, N = {res['n_obs']}.\n")
