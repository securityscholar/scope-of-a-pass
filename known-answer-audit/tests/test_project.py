import os, sys, tempfile, shutil, json
sys.path.insert(0, "src")
import make_runs as M, glab_project as P
tmp = tempfile.mkdtemp(prefix="projtest_")
for mod in (M, P):
    mod.RUNS, mod.PRIV = os.path.join(tmp, "runs"), os.path.join(tmp, "private")
os.makedirs(M.RUNS); os.makedirs(M.PRIV)
os.environ["GLAB_VERSION"] = "v2"
M.make_run("T3", "C0", 999)
P.prepare("T3")
P.snapshot("T3", 1); P.deliver("T3", 2)
print(open(os.path.join(M.RUNS, "T3", "data", "MANIFEST.csv")).read())
shutil.rmtree(tmp)
