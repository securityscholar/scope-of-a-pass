import sys, tempfile, time
sys.path.insert(0, "src")
import glab_core as G
for seed in [101, 202]:
    files, truth = G.generate(seed)
    with tempfile.TemporaryDirectory() as d:
        G.write_files(files, d); rb = G.read_back(d)
    p = G.build_panel(rb)
    t0 = time.time(); a = G.estimate(p); t1 = time.time(); b = G.estimate_within(p); t2 = time.time()
    print(f"seed {seed}: dummies coef {a['coef_rd_int']:.10f} se {a['se_rd_int']:.8f} n {a['n_obs']} ({t1-t0:.1f}s) | "
          f"within coef {b['coef_rd_int']:.10f} se {b['se_rd_int']:.8f} n {b['n_obs']} ({t2-t1:.2f}s) | "
          f"coef diff {abs(a['coef_rd_int']-b['coef_rd_int']):.2e} se ratio {b['se_rd_int']/a['se_rd_int']:.6f}")
