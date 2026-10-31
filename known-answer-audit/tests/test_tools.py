import json, os, shutil, subprocess, sys, tempfile
sys.path.insert(0, "src")
import make_runs as M
import glab_core as G
tmp = tempfile.mkdtemp(prefix="glabtest_")
M.RUNS, M.PRIV = os.path.join(tmp, "runs"), os.path.join(tmp, "private")
os.makedirs(M.RUNS); os.makedirs(M.PRIV)
key = M.make_run("T1", "C3", 777)
ref = key["reference"]
results = {}
for name in ["correct_guarded", "naive_plain"]:
    folder = os.path.join(M.RUNS, "T1")
    shutil.rmtree(os.path.join(folder, "output")); os.makedirs(os.path.join(folder, "output"))
    shutil.copy2(f"tests/agents/{name}.py", os.path.join(folder, "analysis.py"))
    r = subprocess.run([sys.executable, "analysis.py"], cwd=folder, capture_output=True, text=True, timeout=600)
    print(f"--- {name}: analysis.py exit {r.returncode}; last line: {((r.stdout + r.stderr).strip().splitlines() or ['(no output)'])[-1][:150]}")
    g = subprocess.run([sys.executable, "gate.py"], cwd=folder, capture_output=True, text=True, timeout=900)
    print(f"    gate exit {g.returncode}:\n      " + "\n      ".join(g.stdout.strip().splitlines()))
    if os.path.exists(os.path.join(folder, "output", "result.json")):
        res = json.load(open(os.path.join(folder, "output", "result.json")))
        print(f"    result {res}\n    reference coef {ref['coef_rd_int']:.6f} n {ref['n_obs']} firms {ref['n_firms']}")
        results[name] = (res, g.returncode)
ok = abs(results["correct_guarded"][0]["coef_rd_int"] - ref["coef_rd_int"]) < 1e-9 and results["correct_guarded"][0]["n_obs"] == ref["n_obs"] \
     and results["correct_guarded"][1] == 0 and results["naive_plain"][1] == 1
print("TEST", "PASS" if ok else "FAIL", "(correct script reproduces the reference and passes the gate; naive script fails the gate)")
shutil.rmtree(tmp)
