# test_screen.py  The copy screen passes the generator's files and fails the pilot's artifact.
# Run from the repository root: python3 tests/test_screen.py
import os
import sys
import tempfile

sys.path.insert(0, "src")
import glab_core as G  # noqa: E402
import glab_project as P  # noqa: E402
import make_runs as M  # noqa: E402
import screen_copies as SC  # noqa: E402

fails = []
for seed in (101, 202, 303):
    s, files, truth, rb, ref_panel = M.choose_instance(seed)       # calls SC.require_clean on the five files
    for noise_sd, should_pass in ((0.35, True), (0.0, False)):    # 0.0 rebuilds the pilot's median copies
        r2, info = P.revised_vendor(rb["rd_new"], rb["financials"], s, noise_sd=noise_sd)
        with tempfile.TemporaryDirectory() as d:
            r2.to_csv(os.path.join(d, P.NEW_FILE), index=False)
            r = SC.screen_paths([d])
        got = bool(r["passed"].all())
        hits = r.loc[r["column"] == "rd_intensity", ["repeat", "median"]].iloc[0].tolist()
        print(f"seed {s} noise_sd {noise_sd}: rd_intensity repeat, median = {hits}; passed {got}")
        if got != should_pass:
            fails.append((s, noise_sd))
print("TEST PASS" if not fails else f"TEST FAIL {fails}")
sys.exit(1 if fails else 0)
