# Note to PI

**Result.** R&D intensity positively predicts next-year sales growth: +1 point of R&D/assets goes with +0.75 points of growth (coef 0.745, SE 0.086, t-stat 8.7; N = 3,640 firm-years, 354 firms, year t = FY2010-2021). OLS with firm and year fixed effects, size-class indicators and firm-clustered SEs. A within-firm association, not causal.

**Caveat.** 33 firm-years have sales jumps above 50% (likely acquisitions, concentrated in high-R&D firms; kept per the codebook). Without them the coefficient is 0.38 (SE 0.025). Exploratory only.

**Data decisions**
- R&D: newest vendor file (2024-02-15). The superseded 2023-09-30 file gives 0.763. Blank R&D is missing (180 firm-years dropped); true zeros kept.
- Vendor R&D is in thousands through FY2014, millions from FY2015 (undocumented; checked against vendor intensity). Converted; rd_int is R&D/total assets, not the vendor's sales ratio.
- Vendor files use old IDs before 2016 (65 firms); mapped to current IDs.
- Excluded 46 firms whose current (latest as_of) industry is Finance.
- Size class recomputed from year-t assets, not the FY2022 label.
- FY2023 is partial (median sales 0.47 of FY2022; MANIFEST: complete through FY2022), so the last t is 2021.
- Next-year sales matched by fiscal year (49 firms skip a year).

SE: statsmodels default d.f.; absorbed-FE d.f. gives 0.082.
