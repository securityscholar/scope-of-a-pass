import json, os, shutil, subprocess, sys, tempfile
sys.path.insert(0, "src")
import make_runs as M, grade as GR
tmp = tempfile.mkdtemp(prefix="gradetest_")
for mod in (M, GR):
    mod.RUNS, mod.PRIV = os.path.join(tmp, "runs"), os.path.join(tmp, "private")
GR.RES = os.path.join(tmp, "results")
os.makedirs(M.RUNS); os.makedirs(M.PRIV)
M.make_run("T2", "C0", 888)
want = {"correct_plain": {d: True for d in GR.DEFECTS + GR.NEAR},
        "naive_plain": dict(dup=False, idchange=False, units=None, vintage=False, grid=False, partial=False,
                            lookahead=False, label=True, zeros=True, jumps=True),
        "mixed_grid_label": dict(dup=True, idchange=True, units=None, vintage=True, grid=False, partial=True,
                                 lookahead=True, label=False, zeros=True, jumps=True)}
allok = True
for name, exp in want.items():
    f = os.path.join(M.RUNS, "T2"); shutil.rmtree(os.path.join(f, "output")); os.makedirs(os.path.join(f, "output"))
    shutil.copy2(f"tests/agents/{name}.py", os.path.join(f, "analysis.py"))
    r = subprocess.run([sys.executable, "analysis.py"], cwd=f, capture_output=True, text=True, timeout=600)
    g = GR.grade("T2", None)
    got = {d: g["ends"]["defects"][d].get("handled") for d in GR.DEFECTS + GR.NEAR}
    # naive reads IDs as numbers and never maps them: units is graded under its construct
    bad = {d: (got[d], exp[d]) for d in exp if exp[d] is not None and got[d] != exp[d]}
    allok &= not bad
    print(f"{name:18s} exit {r.returncode} correct_overall={g['ends']['correct_overall']} construct={g['ends']['construct']['name']} "
          f"gate_posthoc={g['gate_posthoc']['passed']} mismatches={bad}")
    print("   handled:", got)
    print("   talk:", {k: v for k, v in g["talk"].items() if v})
print("TEST", "PASS" if allok else "FAIL")
shutil.rmtree(tmp)
