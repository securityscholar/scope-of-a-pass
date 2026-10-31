#!/usr/bin/env python3
"""glab_core.py  v2  Data-generating process, reference pipeline and planted-defect variants.

One task instance is a messy set of source files for a firm-year panel study (does R&D intensity
predict next-year sales growth), with eight planted defects and two legitimate features that look
like defects. The known answer is the estimate from the reference pipeline on the delivered files.
Agents never see this module.

Defects (key: what a correct pipeline does)
  dup        firms.csv lists name-changers twice; current attributes are on the latest as_of row
  idchange   the R&D vendor keeps pre-2016 IDs for fiscal years before 2016; id_history.csv maps them
  units      R&D is in USD thousands through FY2014 and USD millions from FY2015
  vintage    rd_vendor.csv is superseded (missing R&D filled with zero, uncorrected values);
             rd_vendor_2023-09-30.csv is current
  grid       some firms skip a fiscal year; growth to t+1 needs the t+1 filing, not the next row
  partial    FY2023 is year to date (extract 2023-06-30); growth into FY2023 is not computable
  lookahead  firms.csv size_class is assigned from FY2022 assets; the model needs class at t
  label      the vendor rd_intensity column is R&D / sales; the model needs R&D / assets
Near misses (key: a correct pipeline leaves them alone)
  zeros      reported zero R&D in the current vintage is a true zero
  jumps      acquisition years carry real sales jumps
"""
import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

FIRST_SRC, LAST_SRC = 2009, 2023
ANALYSIS_START = 2010
PARTIAL_YEAR = 2023
UNIT_SWITCH = 2015          # thousands through FY2014, millions from FY2015
ID_CHANGE_YEAR = 2016
CUT_MED, CUT_LARGE = 100.0, 1000.0
BETA = 0.40
D_CLASS = {"small": 0.0, "medium": -0.10, "large": -0.22}
INDUSTRIES = ["Manufacturing", "Software", "Biotech", "Retail", "Energy", "Finance"]
IND_P = [0.24, 0.18, 0.14, 0.16, 0.14, 0.14]
RD_RANGE = {"Manufacturing": (0.03, 0.08), "Software": (0.10, 0.22), "Biotech": (0.12, 0.25),
            "Retail": (0.0, 0.02), "Energy": (0.0, 0.03), "Finance": (0.0, 0.02)}
FIX_ALL = dict(dup=True, idchange=True, units=True, vintage=True, grid=True, partial=True,
               lookahead=True, label=True, zeros=True, jumps=True)
RD_FILE_OLD, RD_FILE_NEW = "rd_vendor.csv", "rd_vendor_2023-09-30.csv"


def size_class(assets):
    a = np.asarray(assets, dtype=float)
    return np.where(a >= CUT_LARGE, "large", np.where(a >= CUT_MED, "medium", "small"))


def generate(seed, n_firms=400):
    """Return dict of DataFrames (the delivered files) plus latent truth used for checks."""
    rng = np.random.default_rng(seed)
    pool = rng.choice(np.arange(1001, 299999), size=2 * n_firms, replace=False)
    cur_ids, old_ids = pool[:n_firms], pool[n_firms:]
    fid = np.array([f"{i:06d}" for i in cur_ids])
    oid = np.array([f"{i:06d}" for i in old_ids])
    industry = rng.choice(INDUSTRIES, size=n_firms, p=IND_P)
    first = np.where(rng.random(n_firms) < 0.7, FIRST_SRC, rng.integers(2010, 2015, n_firms))
    last = np.where(rng.random(n_firms) < 0.8, LAST_SRC, rng.integers(2018, 2023, n_firms))
    gap = np.full(n_firms, -1)
    for i in np.where(rng.random(n_firms) < 0.15)[0]:
        lo, hi = max(first[i] + 2, 2011), min(last[i] - 2, 2020)
        if lo <= hi:
            gap[i] = rng.integers(lo, hi + 1)
    idchanger = rng.random(n_firms) < 0.15
    mu = np.array([rng.uniform(*RD_RANGE[k]) for k in industry])
    zero_firm = (np.isin(industry, ["Retail", "Energy", "Finance"])) & (rng.random(n_firms) < 0.35)
    turnover = rng.uniform(0.5, 1.6, n_firms)
    alpha = rng.normal(0.05, 0.03, n_firms)
    years = np.arange(FIRST_SRC, LAST_SRC + 1)
    gamma = dict(zip(years, rng.normal(0.0, 0.03, len(years))))
    jump_firm = (mu > np.median(mu)) & (rng.random(n_firms) < 0.14)
    jump_year = np.full(n_firms, -1)

    rows = []
    for i in range(n_firms):
        T = np.arange(first[i], last[i] + 1)
        a0 = np.exp(rng.normal(np.log(150.0), 1.3))
        a = a0 * np.exp(np.concatenate([[0.0], np.cumsum(rng.normal(0.08, 0.12, len(T) - 1))]))
        rdi = mu[i] * (a / a0) ** (-0.8) * np.exp(rng.normal(0.0, 0.5, len(T)))
        if zero_firm[i]:
            rdi = np.where(rng.random(len(T)) < 0.5, 0.0, rdi)
        cls = size_class(a)
        jy = -1
        if jump_firm[i]:
            win = (T >= 2011) & (T <= 2020)
            if win.any():
                jy = int(T[win][np.argmax(rdi[win])])
        jump_year[i] = jy
        g = (alpha[i] + np.array([gamma[t] for t in T]) + BETA * rdi + np.array([D_CLASS[c] for c in cls])
             + rng.normal(0.0, 0.07, len(T)) + np.where(T == jy, rng.uniform(0.8, 1.5), 0.0))
        g = np.maximum(g, -0.8)
        s = np.empty(len(T))
        s[0] = a0 * turnover[i]
        for k in range(1, len(T)):
            s[k] = s[k - 1] * (1.0 + g[k - 1])
        for k, t in enumerate(T):
            rows.append(dict(i=i, fyear=int(t), assets=a[k], sales=s[k], rd_int=rdi[k], cls=str(cls[k]),
                             g_true=g[k]))
    lat = pd.DataFrame(rows)
    lat["firm_id"] = fid[lat["i"]]
    lat["rd_m"] = lat["rd_int"] * lat["assets"]                       # R&D, USD millions
    lat = lat[lat["fyear"] != gap[lat["i"]]].reset_index(drop=True)   # skipped filings
    # partial FY2023: year to date at the 2023-06-30 extract
    frac = rng.choice([0.25, 0.5, 0.75], n_firms)
    is23 = lat["fyear"] == PARTIAL_YEAR
    lat["sales_rep"] = np.where(is23, lat["sales"] * frac[lat["i"]], lat["sales"])
    lat["rd_rep_m"] = np.where(is23, lat["rd_m"] * frac[lat["i"]], lat["rd_m"])
    # R&D truly missing for 6 percent of firm-years (blank in the current vintage)
    lat["rd_missing"] = rng.random(len(lat)) < 0.06
    # superseded vintage: missing filled with zero; 10 percent of values later corrected
    lat["corrected"] = (~lat["rd_missing"]) & (rng.random(len(lat)) < 0.10) & (lat["rd_m"] > 0)
    lat["rd_old_m"] = np.where(lat["rd_missing"], 0.0,
                               np.where(lat["corrected"], lat["rd_rep_m"] * rng.uniform(0.4, 1.6, len(lat)),
                                        lat["rd_rep_m"]))

    # financials.csv (current IDs throughout)
    fin = pd.DataFrame({"firm_id": lat["firm_id"], "fyear": lat["fyear"],
                        "sales": lat["sales_rep"].round(4), "assets": lat["assets"].round(4)})

    def vendor(rd_m_col, blank_missing):
        units = np.where(lat["fyear"] <= UNIT_SWITCH - 1, 1000.0, 1.0)   # thousands before FY2015
        rd = (lat[rd_m_col] * units).round(4)
        inten = (lat[rd_m_col] / lat["sales_rep"]).round(6)              # vendor ratio: R&D / sales
        if blank_missing:
            rd = rd.where(~lat["rd_missing"])
            inten = inten.where(~lat["rd_missing"])
        vid = np.where(idchanger[lat["i"]] & (lat["fyear"] < ID_CHANGE_YEAR), oid[lat["i"]], lat["firm_id"])
        return pd.DataFrame({"firm_id": vid, "fyear": lat["fyear"], "rd": rd, "rd_intensity": inten})

    rd_new = vendor("rd_rep_m", blank_missing=True)
    rd_old = vendor("rd_old_m", blank_missing=False)

    # firms.csv: current attributes; name-changers listed twice; size_class from FY2022 (look-ahead)
    last_obs = lat[lat["fyear"] <= 2022].sort_values("fyear").groupby("i").tail(1).set_index("i")
    names = [f"{w1} {w2}" for w1, w2 in zip(rng.choice(["Apex", "Birch", "Cobalt", "Delta", "Ember", "Falcon",
                                                         "Granite", "Harbor", "Iris", "Juniper", "Keystone",
                                                         "Lumen", "Meridian", "Northwind", "Orion", "Pioneer"],
                                                        n_firms),
                                             rng.choice(["Labs", "Systems", "Holdings", "Group", "Works",
                                                         "Industries", "Partners", "Technologies"], n_firms))]
    names = [f"{nm} {k}" for k, nm in enumerate(names)]
    firms = pd.DataFrame({"firm_id": fid, "name": names, "industry": industry,
                          "size_class": size_class(last_obs.reindex(range(n_firms))["assets"]),
                          "as_of": "2023-07-15"})
    changer = rng.random(n_firms) < 0.12
    # force at least three Finance switches in each direction among name-changers
    fin_idx = np.where(industry == "Finance")[0]
    non_idx = np.where(industry != "Finance")[0]
    old_ind = industry.copy()
    to_fin = rng.choice(fin_idx, size=min(3, len(fin_idx)), replace=False)       # now Finance, were not
    from_fin = rng.choice(non_idx, size=3, replace=False)                        # were Finance, now not
    changer[to_fin] = True
    changer[from_fin] = True
    for i in np.where(changer)[0]:
        if i in to_fin:
            old_ind[i] = rng.choice([k for k in INDUSTRIES if k != "Finance"])
        elif i in from_fin:
            old_ind[i] = "Finance"
        elif rng.random() < 0.3:
            old_ind[i] = rng.choice([k for k in INDUSTRIES if k != industry[i]])
    old_rows = pd.DataFrame({"firm_id": fid[changer], "name": [f"{names[i].split(' ')[0]} Former {i}" for i in
                                                                np.where(changer)[0]],
                             "industry": old_ind[changer], "size_class": firms["size_class"].values[changer],
                             "as_of": "2014-03-31"})
    firms = pd.concat([old_rows, firms]).sample(frac=1.0, random_state=seed).reset_index(drop=True)

    idh = pd.DataFrame({"old_id": oid[idchanger], "firm_id": fid[idchanger], "effective_fyear": ID_CHANGE_YEAR})
    files = {"firms": firms, "financials": fin, "rd_new": rd_new, "rd_old": rd_old, "id_history": idh}
    truth = dict(seed=int(seed), n_firms=int(n_firms), n_changer=int(changer.sum()), n_idchanger=int(idchanger.sum()),
                 n_gap=int((gap > 0).sum()), n_zero_firm=int(zero_firm.sum()), n_jump=int(jump_firm.sum()),
                 jump_rows=[(fid[i], int(jump_year[i])) for i in np.where(jump_firm)[0]],
                 to_fin=[fid[i] for i in to_fin], from_fin=[fid[i] for i in from_fin])
    return files, truth


def build_panel(files, fix=None):
    """Reference pipeline. fix[k] = False mishandles defect k the way a careless script would."""
    f = dict(FIX_ALL)
    f.update(fix or {})
    firms, fin = files["firms"].copy(), files["financials"].copy()
    rd = (files["rd_new"] if f["vintage"] else files["rd_old"]).copy()
    # firm attributes
    if f["dup"]:
        firms = firms.sort_values(["firm_id", "as_of"]).groupby("firm_id").tail(1)
    # ID mapping for the vendor file
    if f["idchange"]:
        m = dict(zip(files["id_history"]["old_id"], files["id_history"]["firm_id"]))
        rd["firm_id"] = rd["firm_id"].map(lambda x: m.get(x, x))
    # units
    if f["units"]:
        rd["rd"] = np.where(rd["fyear"] <= UNIT_SWITCH - 1, rd["rd"] / 1000.0, rd["rd"])
    # lead of sales
    fin = fin.sort_values(["firm_id", "fyear"])
    if f["grid"]:
        nxt = fin[["firm_id", "fyear", "sales"]].rename(columns={"sales": "sales_next"})
        nxt["fyear"] = nxt["fyear"] - 1
        fin = fin.merge(nxt, on=["firm_id", "fyear"], how="left")
    else:
        fin["sales_next"] = fin.groupby("firm_id")["sales"].shift(-1)
    if f["partial"]:
        fin = fin[fin["fyear"] < PARTIAL_YEAR]
        fin.loc[fin["fyear"] == PARTIAL_YEAR - 1, "sales_next"] = np.nan
    fin["growth_next"] = fin["sales_next"] / fin["sales"] - 1.0
    # merge
    p = fin.merge(rd, on=["firm_id", "fyear"], how="inner")
    p = p.merge(firms[["firm_id", "industry", "size_class"]], on="firm_id", how="inner")
    p = p[p["industry"] != "Finance"]
    p = p[p["fyear"] >= ANALYSIS_START]
    p["rd_int"] = (p["rd"] / p["assets"]) if f["label"] else p["rd_intensity"]
    p["size_class_t"] = size_class(p["assets"]) if f["lookahead"] else p["size_class"]
    if not f["zeros"]:
        p = p[p["rd_int"] != 0]
    p = p.dropna(subset=["rd_int", "growth_next"])
    if not f["jumps"]:
        lo, hi = p["growth_next"].quantile([0.01, 0.99])
        p["growth_next"] = p["growth_next"].clip(lo, hi)
    p = p.rename(columns={"fyear": "year"})
    return p[["firm_id", "year", "rd_int", "growth_next", "size_class_t"]].sort_values(["firm_id", "year"]) \
        .reset_index(drop=True)


def estimate(panel):
    """OLS of growth_next on rd_int and size class dummies (small omitted), firm and year effects,
    standard errors clustered by firm. Dummies with no variation are left out."""
    import warnings
    d = panel.copy()
    d["fid"] = d["firm_id"].astype(str)
    d["cls_medium"] = (d["size_class_t"] == "medium").astype(float)
    d["cls_large"] = (d["size_class_t"] == "large").astype(float)
    terms = ["rd_int"] + [c for c in ["cls_medium", "cls_large"] if d[c].std() > 0]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = smf.ols("growth_next ~ " + " + ".join(terms) + " + C(fid) + C(year)", data=d).fit(
            cov_type="cluster", cov_kwds={"groups": pd.factorize(d["fid"])[0]})
    rank_ok = bool(np.linalg.matrix_rank(fit.model.exog) == fit.model.exog.shape[1])
    return dict(coef_rd_int=float(fit.params["rd_int"]), se_rd_int=float(fit.bse["rd_int"]),
                n_obs=int(fit.nobs), n_firms=int(d["fid"].nunique()), full_rank=rank_ok)


def estimate_within(panel):
    """Same model as estimate(), by firm demeaning (Frisch-Waugh) with year and size dummies demeaned within firm.
    Coefficient and N are identical to the dummy version; the clustered SE uses the dummy version's degrees of
    freedom (firm effects counted), so it matches estimate() as well."""
    d = panel.dropna(subset=["rd_int", "growth_next"]).copy()
    d["fid"] = d["firm_id"].astype(str)
    X = pd.DataFrame({"rd_int": d["rd_int"].astype(float)})
    for c in ["medium", "large"]:
        col = (d["size_class_t"] == c).astype(float)
        if col.std() > 0:
            X[f"cls_{c}"] = col
    yrs = sorted(d["year"].unique())
    for y in yrs[1:]:
        X[f"y{y}"] = (d["year"] == y).astype(float)
    g = d["fid"].to_numpy()
    Xd = X - X.groupby(g).transform("mean")
    yd = d["growth_next"].astype(float) - d["growth_next"].astype(float).groupby(g).transform("mean")
    keep = [c for c in Xd.columns if Xd[c].abs().max() > 1e-12]
    A = Xd[keep].to_numpy()
    b, *_ = np.linalg.lstsq(A, yd.to_numpy(), rcond=None)
    e = yd.to_numpy() - A @ b
    n, k = A.shape
    G_ = pd.factorize(g)[0]
    ng = G_.max() + 1
    XtX_inv = np.linalg.pinv(A.T @ A)
    meat = np.zeros((k, k))
    S = np.zeros((ng, k))
    np.add.at(S, G_, A * e[:, None])
    meat = S.T @ S
    k_full = k + ng                      # firm effects counted, as in the dummy regression with an intercept
    c = (ng / (ng - 1)) * ((n - 1) / (n - k_full))
    V = c * XtX_inv @ meat @ XtX_inv
    j = keep.index("rd_int")
    return dict(coef_rd_int=float(b[j]), se_rd_int=float(np.sqrt(V[j, j])), n_obs=int(n), n_firms=int(ng), full_rank=True)


def write_files(files, folder):
    """Write the delivered files and the codebook pieces that depend on the instance."""
    import os
    os.makedirs(folder, exist_ok=True)
    files["firms"].to_csv(f"{folder}/firms.csv", index=False)
    files["financials"].to_csv(f"{folder}/financials.csv", index=False)
    files["rd_old"].to_csv(f"{folder}/{RD_FILE_OLD}", index=False)
    files["rd_new"].to_csv(f"{folder}/{RD_FILE_NEW}", index=False)
    files["id_history"].to_csv(f"{folder}/id_history.csv", index=False)
    pd.DataFrame([
        dict(file="firms.csv", content="firm attributes", vintage="2023-07-15", status="current", complete_through=""),
        dict(file="financials.csv", content="sales and total assets", vintage="2023-06-30", status="current",
             complete_through="FY2022"),
        dict(file=RD_FILE_OLD, content="R&D vendor file", vintage="2023-03-31", status="superseded",
             complete_through="FY2022"),
        dict(file=RD_FILE_NEW, content="R&D vendor file, revised", vintage="2023-09-30", status="current",
             complete_through="FY2022"),
        dict(file="id_history.csv", content="firm ID changes", vintage="2023-07-15", status="current",
             complete_through=""),
    ]).to_csv(f"{folder}/MANIFEST.csv", index=False)


def read_back(folder):
    """Read the delivered files exactly as a careful analyst would (IDs as text)."""
    t = {"firm_id": str, "old_id": str}
    return {"firms": pd.read_csv(f"{folder}/firms.csv", dtype=t),
            "financials": pd.read_csv(f"{folder}/financials.csv", dtype=t),
            "rd_old": pd.read_csv(f"{folder}/{RD_FILE_OLD}", dtype=t),
            "rd_new": pd.read_csv(f"{folder}/{RD_FILE_NEW}", dtype=t),
            "id_history": pd.read_csv(f"{folder}/id_history.csv", dtype=t)}


if __name__ == "__main__":
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    files, truth = generate(seed)
    print(json.dumps({k: v for k, v in truth.items() if not isinstance(v, list)}))
