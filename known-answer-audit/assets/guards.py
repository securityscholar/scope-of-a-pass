"""guards.py: one check function for each working rule in RULES.md.

Import it in analysis.py (from guards import *). Every call prints what it checked and appends a
record to output/checks.jsonl. A failed check raises GuardError, which stops the script.

    g_read(name, **read_csv_kwargs)            rule 1  read a data file only if MANIFEST.csv lists it as current
    g_key(df, cols, label)                     rule 2  stop unless cols identify rows uniquely
    g_merge(left, right, on, how, ...)         rule 2  merge, print matched and unmatched rows, stop above 1 percent
    g_rows(n_before, df, step, reason)         rule 3  print rows in and out at a step
    g_lead(df, unit, period, col, k=1)         rule 4  value of col in period t+k, from a complete unit-by-period grid
    g_lag(df, unit, period, col, k=1)          rule 4  value of col in period t-k, same way
    g_scale(df, col, period, max_ratio=10)     rule 5  median by period; stop on a break in scale
    g_complete(df, period, source)             rule 6  stop if df holds periods after the source's last complete one
"""
import json
import os
import time

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
LOG = os.path.join(HERE, "output", "checks.jsonl")
RUN = time.strftime("%Y%m%dT%H%M%S") + f"-{os.getpid()}"


class GuardError(Exception):
    pass


def _log(rule, check, ok, **info):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    rec = dict(run=RUN, rule=rule, check=check, ok=bool(ok), **info)
    with open(LOG, "a", encoding="utf8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    print(f"[{'OK' if ok else 'FAIL'}] rule {rule}, {check}: " + ", ".join(f"{k}={v}" for k, v in info.items()),
          flush=True)
    if not ok:
        raise GuardError(f"rule {rule}, {check} failed: {info}")


def _manifest():
    return pd.read_csv(os.path.join(DATA, "MANIFEST.csv"), dtype=str, keep_default_na=False)


def g_read(name, **kwargs):
    """Rule 1. Read data/<name> only if MANIFEST.csv lists it as current."""
    m = _manifest()
    row = m[m["file"] == name]
    status = row["status"].iloc[0] if len(row) == 1 else "not in MANIFEST.csv"
    _log(1, "read", status == "current", file=name, status=status)
    df = pd.read_csv(os.path.join(DATA, name), **kwargs)
    print(f"      {name}: {len(df)} rows, {df.shape[1]} columns", flush=True)
    return df


def g_key(df, cols, label):
    """Rule 2. Stop unless cols identify the rows of df uniquely."""
    cols = [cols] if isinstance(cols, str) else list(cols)
    n_dup = int(df.duplicated(cols, keep=False).sum())
    _log(2, "unique key", n_dup == 0, table=label, key="+".join(cols), rows=len(df), rows_sharing_a_key=n_dup)


def g_rows(n_before, df, step, reason=""):
    """Rule 3. Print rows in and out at a step."""
    _log(3, "rows", True, step=step, rows_in=int(n_before), rows_out=len(df), change=len(df) - int(n_before),
         reason=reason)


def g_merge(left, right, on, how="left", left_label="left", right_label="right", left_unique=False,
            right_unique=True, max_unmatched=0.01, reason=""):
    """Rule 2. Merge, print matched and unmatched rows on each side, and stop when the unmatched share on
    either side is above max_unmatched, unless a reason is given. Keys are checked for uniqueness first."""
    on = [on] if isinstance(on, str) else list(on)
    if left_unique:
        g_key(left, on, left_label)
    if right_unique:
        g_key(right, on, right_label)
    m = left.merge(right, on=on, how="outer", indicator=True)
    both = int((m["_merge"] == "both").sum())
    lo = int((m["_merge"] == "left_only").sum())
    ro = int((m["_merge"] == "right_only").sum())
    sl, sr = lo / max(len(left), 1), ro / max(len(right), 1)
    over = sl > max_unmatched or sr > max_unmatched
    _log(2, "merge", (not over) or bool(reason), left=left_label, right=right_label, on="+".join(on), matched=both,
         left_only=lo, right_only=ro, left_unmatched_share=round(sl, 4), right_unmatched_share=round(sr, 4),
         max_unmatched=max_unmatched, reason=reason)
    keep = {"inner": ["both"], "left": ["both", "left_only"], "right": ["both", "right_only"],
            "outer": ["both", "left_only", "right_only"]}[how]
    out = m[m["_merge"].isin(keep)].drop(columns="_merge").reset_index(drop=True)
    g_rows(len(left), out, f"merge {left_label} with {right_label} ({how})")
    return out


def _shift(df, unit, period, col, k, name):
    g_key(df, [unit, period], "lead/lag source")
    other = df[[unit, period, col]].copy()
    other[period] = other[period] - k
    out = df.merge(other.rename(columns={col: name}), on=[unit, period], how="left")
    return out


def g_lead(df, unit, period, col, k=1, name=None):
    """Rule 4. Add col's value in period t+k, matched on the period itself, never on row order."""
    name = name or f"{col}_lead{k}"
    out = _shift(df, unit, period, col, k, name)
    _log(4, "lead on grid", True, column=name, rows=len(out), rows_without_value=int(out[name].isna().sum()))
    return out


def g_lag(df, unit, period, col, k=1, name=None):
    """Rule 4. Add col's value in period t-k, matched on the period itself, never on row order."""
    name = name or f"{col}_lag{k}"
    out = _shift(df, unit, period, col, -k, name)
    _log(4, "lag on grid", True, column=name, rows=len(out), rows_without_value=int(out[name].isna().sum()))
    return out


def g_scale(df, col, period, max_ratio=10.0):
    """Rule 5. Print the median of col by period and stop if adjacent medians differ by more than max_ratio."""
    med = df.groupby(period)[col].median()
    print(f"      median of {col} by {period}:\n" + med.to_string(), flush=True)
    ratio = (med / med.shift(1)).dropna()
    breaks = ratio[(ratio > max_ratio) | (ratio < 1.0 / max_ratio)]
    _log(5, "scale", breaks.empty, column=col, breaks={str(k): round(float(v), 6) for k, v in breaks.items()})


def g_complete(df, period, source):
    """Rule 6. Stop if df holds periods after the last complete period MANIFEST.csv gives for source."""
    m = _manifest()
    row = m[m["file"] == source]
    ct = row["complete_through"].iloc[0] if len(row) == 1 else ""
    last = int(ct.replace("FY", "")) if ct else None
    top = int(pd.to_numeric(df[period]).max())
    _log(6, "complete periods", last is None or top <= last, source=source, complete_through=ct or "not given",
         last_period_in_data=top)
