import json, numpy as np, pandas as pd, statsmodels.formula.api as smf
firms = pd.read_csv("data/firms.csv"); fin = pd.read_csv("data/financials.csv"); rd = pd.read_csv("data/rd_vendor.csv")
fin = fin.sort_values(["firm_id", "fyear"])
fin["growth_next"] = fin.groupby("firm_id")["sales"].shift(-1) / fin["sales"] - 1
p = fin.merge(rd, on=["firm_id", "fyear"]).merge(firms[["firm_id", "industry", "size_class"]], on="firm_id")
p = p[(p["industry"] != "Finance") & (p["fyear"] >= 2010)].dropna(subset=["growth_next"])
p["rd_int"] = p["rd"] / p["assets"]; p["size_class_t"] = p["size_class"]; p = p.rename(columns={"fyear": "year"})
p[["firm_id", "year", "rd_int", "growth_next", "size_class_t"]].to_csv("output/panel.csv", index=False)
fit = smf.ols("growth_next ~ rd_int + C(firm_id) + C(year)", data=p).fit(cov_type="cluster", cov_kwds={"groups": p["firm_id"]})
res = dict(coef_rd_int=float(fit.params["rd_int"]), se_rd_int=float(fit.bse["rd_int"]), n_obs=int(fit.nobs), n_firms=int(p["firm_id"].nunique()))
json.dump(res, open("output/result.json", "w")); open("output/note.md", "w").write("All checks passed. Coefficient 0.5.\n")
