#!/usr/bin/env python3
"""screen_copies.py  v1  Screens generated firm-year files for copied values before any agent sees them.

A value drawn with noise almost never repeats exactly within a firm, and almost never equals the median of the
firm's other values in the same column. A generator that fills cells by copying a firm statistic produces many
of both, and an agent can detect them (two pilot agents did). For every file keyed by firm_id and fyear, and
every numeric column in it, the screen counts values that

    repeat   an earlier value of the same firm in the same column, or
    median   equal the median of the same firm's other values, at the precision the file prints.

firms.csv and id_history.csv are not keyed by year and are not screened: the duplicate rows in firms.csv are a
planted defect. Values printed with fewer than MIN_DIGITS significant digits (an R&D ratio of 0.000007) tie by
rounding, so they are not counted. A column fails when its hits exceed LIMIT, set above what chance gives on
every instance prepared so far (results/screen_copies_check.csv).

    python3 screen_copies.py DATA_FOLDER_OR_CSV [...]        prints every column; exit 1 if any column fails
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

KEYS = ("firm_id", "fyear")
LIMIT = 5
MIN_DIGITS = 4


def decimals(text_col):
    """The number of decimals the file prints in this column (its precision)."""
    s = text_col.dropna().astype(str)
    s = s[s.str.contains(r"\.")]
    return int(s.str.split(".").str[1].str.len().max()) if len(s) else 0


def screen_frame(d, text=None, name=""):
    """d: a firm-year frame. text: the same frame read as text, for the printed precision. Returns one row per
    numeric column: hits that repeat, hits that equal the leave-one-out median, values counted, pass or fail."""
    out = []
    for c in d.columns:
        if c in KEYS or not pd.api.types.is_numeric_dtype(d[c]):
            continue
        k = decimals(text[c]) if text is not None else 6
        x = d.loc[d[c].notna() & (np.round(d[c].abs() * 10.0 ** k) >= 10 ** (MIN_DIGITS - 1)), ["firm_id", c]]
        rep = int(x.duplicated(["firm_id", c]).sum())
        med = 0
        for _, v in x.groupby("firm_id")[c]:
            v = v.to_numpy(dtype=float)
            if len(v) < 3:
                continue
            for i in range(len(v)):
                if np.round(np.median(np.delete(v, i)), k) == np.round(v[i], k):
                    med += 1
        out.append(dict(file=name, column=c, decimals=k, counted=len(x), repeat=rep, median=med,
                        passed=(rep <= LIMIT and med <= LIMIT)))
    return out


def screen_file(path):
    head = pd.read_csv(path, nrows=0).columns
    if not all(k in head for k in KEYS):
        return []
    text = pd.read_csv(path, dtype=str, keep_default_na=False).replace("", np.nan)
    d = pd.read_csv(path, dtype={"firm_id": str})
    return screen_frame(d, text, os.path.basename(path))


def screen_paths(paths):
    rows = []
    for p in paths:
        files = sorted(glob.glob(os.path.join(p, "*.csv"))) if os.path.isdir(p) else [p]
        for f in files:
            rows += screen_file(f)
    return pd.DataFrame(rows)


def require_clean(paths):
    """Stop the build when a generated file fails the screen."""
    r = screen_paths(paths)
    bad = r[~r["passed"]] if len(r) else r
    if len(bad):
        raise RuntimeError("copied values in generated files:\n" + bad.to_string(index=False))
    return r


if __name__ == "__main__":
    r = screen_paths(sys.argv[1:])
    print(r.to_string(index=False) if len(r) else "no firm-year files")
    sys.exit(0 if (len(r) == 0 or r["passed"].all()) else 1)
