#!/usr/bin/env python3
"""models.py  v1  Regime effects in journal layout, from results/defects_long.csv and results/runs_long.csv.

    python3 models.py [RUN_PREFIX ...]

Defect-level linear probability models: handled on regime indicators (plain instructions omitted), with
defect and task-instance fixed effects, standard errors clustered by run. Saves results/models.json.
"""
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
REG = ["C1", "C2", "C3"]
LAB = {"C1": "Written rules", "C2": "Rules + tools the agent may run", "C3": "Rules + tools + enforced gate"}


def fit(df, y, fe):
    d = df.dropna(subset=[y]).copy()
    d[y] = d[y].astype(float)
    for r in REG:
        d[r] = (d["regime"] == r).astype(float)
    rhs = " + ".join([r for r in REG if d[r].std() > 0] + [f"C({f})" for f in fe if d[f].nunique() > 1])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = smf.ols(f"{y} ~ {rhs}", data=d).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d["run"])[0]})
    out = {r: dict(b=float(m.params[r]), se=float(m.bse[r]), p=float(m.pvalues[r])) for r in REG if r in m.params}
    return dict(coefs=out, n=int(m.nobs), r2=float(m.rsquared), runs=int(d["run"].nunique()),
                mean_plain=float(d.loc[d["regime"] == "C0", y].mean()) if (d["regime"] == "C0").any() else None)


def table(cols, title):
    w = 22
    print(title)
    print(" " * 34 + "".join(f"{c[0]:>{w}s}" for c in cols))
    for r in REG:
        for k, fmt in (("b", "{:.3f}"), ("se", "({:.3f})"), ("p", "[{:.3f}]")):
            lab = LAB[r] if k == "b" else ""
            cells = []
            for _, res in cols:
                c = res["coefs"].get(r)
                cells.append((fmt.format(c[k]) if k != "p" or c[k] >= 0.001 else "[<0.001]") if c else "")
            print(f"{lab[:33]:33s} " + "".join(f"{x:>{w}s}" for x in cells))
    for k, lab in (("mean_plain", "Mean, plain instructions"), ("n", "Observations"), ("runs", "Runs (clusters)"),
                   ("r2", "R-squared")):
        print(f"{lab:33s} " + "".join(f"{(f'{res[k]:.3f}' if isinstance(res[k], float) else str(res[k])):>{w}s}"
                                         for _, res in cols))


def main(prefixes):
    dl = pd.read_csv(os.path.join(RES, "defects_long.csv"))
    runs = pd.read_csv(os.path.join(RES, "runs_long.csv"))
    if prefixes:
        dl = dl[dl["run"].str.startswith(tuple(prefixes))]
        runs = runs[runs["run"].str.startswith(tuple(prefixes))]
    seeds = {}
    for rid in runs["run"]:
        k = json.load(open(os.path.join(ROOT, "private", f"{rid}.json"), encoding="utf8"))
        seeds[rid] = k["seed"]
    dl["inst"] = dl["run"].map(seeds)
    runs["inst"] = runs["run"].map(seeds)
    dl["handled"] = dl["handled"].map({True: 1.0, False: 0.0, "True": 1.0, "False": 0.0})
    cols = [("Covered defects", fit(dl[dl["kind"] == "covered"], "handled", ["defect", "inst"])),
            ("Uncovered defects", fit(dl[dl["kind"] == "uncovered"], "handled", ["defect", "inst"])),
            ("Near misses kept", fit(dl[dl["kind"] == "near miss"], "handled", ["defect", "inst"]))]
    table(cols, "DV: defect handled correctly (1/0). Linear probability; defect and instance fixed effects;\n"
                "SE clustered by run; coefficient, (SE), [p].")
    runs["correct"] = runs["correct"].astype(float)
    runs["own_match"] = runs["own_match"].astype(float)
    runs["gate_out"] = runs["gate_out"].astype(float)
    rc = [("Correct estimate", fit(runs, "correct", ["inst"])),
          ("Gate outputs pass", fit(runs, "gate_out", ["inst"])),
          ("Note matches own panel", fit(runs, "own_match", ["inst"]))]
    print()
    table(rc, "Run-level outcomes (1/0). Linear probability; instance fixed effects; robust SE by run.")
    json.dump(dict(defect_models={c[0]: c[1] for c in cols}, run_models={c[0]: c[1] for c in rc}),
              open(os.path.join(RES, "models.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
