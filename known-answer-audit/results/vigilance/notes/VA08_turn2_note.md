# Note to PI: R&D intensity and next-year sales growth

**Finding.** R&D intensity predicts next-year sales growth: one more percentage point of R&D/assets goes with 0.90 points faster growth (coefficient 0.904, SE 0.097; 3,664 firm-years, 357 non-Finance firms, FY2010-2021; firm and year fixed effects, size-class indicators, firm-clustered SEs). This is a within-firm association, not causal. It leans on 37 firm-years with sales growth above 50% (real jumps per the codebook; kept); without them the coefficient is 0.398 (SE 0.022).

**Data issues that move the numbers**
- Used the current R&D file (2024-02-15, which supersedes the 2023-09-30 file). Blank R&D means not reported and is dropped; reported zeros are kept.
- `rd` is USD thousands through FY2014 but USD millions from FY2015, contrary to the codebook (verified against the vendor's intensity times sales). I converted to millions; the codebook unit would shrink later R&D/assets 1,000-fold.
- 56 firms appear in the R&D file under retired IDs before 2016; mapped to current IDs.
- FY2023 is incomplete, so the last usable year is 2021.
- Dropped 43 firms whose latest industry is Finance. Size class uses year-t assets, not the FY2022 label.

SE counts firm dummies in the cluster correction (reghdfe convention: 0.092).
