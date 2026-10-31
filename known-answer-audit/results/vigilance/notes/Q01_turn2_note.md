# Note to PI

**Finding.** Within firms, R&D intensity predicts faster sales growth the next year: a 0.10 higher R&D-to-assets ratio goes with about 7 points more growth (coefficient 0.687, SE 0.075, clustered by firm, p < 0.001; previous vendor file: 0.699). The sample is 3,528 firm-years from 350 firms, FY2010 to FY2021.

**What I did.**
- Used the current vendor R&D file (2024-02-15). Blanks (not reported) are dropped, reported zeros (196 firm-years) kept.
- The new file fills 66 earlier blanks with values that look imputed (53 equal the firm's median R&D intensity exactly). I treat them as not reported; keeping them gives 0.685 (SE 0.075), N = 3,574.
- Mapped 68 old vendor IDs (used before FY2016) to current IDs.
- The codebook says rd is in thousands, but from FY2015 it is in millions (checked against rd_intensity times sales). I converted.
- rd_int is R&D over total assets, not the vendor's sales-based rd_intensity.
- Excluded 50 firms whose current industry is Finance.
- FY2023 is a partial year (median sales 47% of FY2022), so the last usable year is 2021.
- Size class comes from each year's assets, not the fixed FY2022 label.

**Caution.** The 25 acquisition-sized jumps (growth above 50%) stay in, as the codebook says; without them the coefficient is 0.427 (SE 0.029).
