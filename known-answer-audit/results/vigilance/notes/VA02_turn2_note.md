# Note to PI: R&D intensity and next-year sales growth

**What I did.** Panel of 3,261 firm-years, 329 non-Finance firms (current industry), FY2010-2021; model as specified. Choices:
- Vendor file: the 2024-02-15 revision (manifest: current). Blank R&D dropped, true zeros kept. Old vendor ids mapped to current ids.
- Vendor `rd` is in USD thousands through FY2014 but millions from FY2015 (checked against vendor R&D/sales), contradicting the codebook. I converted to millions; please confirm with the data team.
- FY2023 is partial (complete through FY2022), so t ends at 2021. Growth uses sales in year t+1 itself, as some firms skip years.
- Size class recomputed yearly from assets, not the FY2022 label. Acquisition jumps kept.

**Result.** rd_int coefficient 0.823 (SE 0.108, p < 0.001; Stata-style SE 0.102), significant: net of firm and year effects, 1 percentage point more R&D/assets goes with 0.82 points faster sales growth next year.

**Versus the previous run (2023-09-30 file).** The newer file adds 31 firm-years (R&D newly reported) and revises R&D in 236 others: n 3,230 to 3,261; coefficient 0.833 to 0.823 (SE 0.109 to 0.108). Conclusion unchanged.

**Caution.** 27 firm-years with growth above 50% (mean rd_int 0.24 vs 0.07 overall) carry much of this; dropping them gives 0.37 (SE 0.03), still positive and significant. Association, not causation.
