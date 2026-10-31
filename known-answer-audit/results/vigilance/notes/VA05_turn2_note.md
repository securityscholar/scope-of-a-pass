# Note to PI

**Finding.** OLS of growth_next on rd_int, medium/large dummies (small omitted), and firm and year fixed effects: within firms, higher R&D/assets goes with faster sales growth the next year. Coefficient on rd_int 0.765 (SE 0.094, clustered by firm; t = 8.2): one more percentage point of R&D/assets goes with 0.765 points more growth. 3,530 firm-years, 345 firms, FY2010-2021. Association, not causation.

**Caveat.** Large sales jumps (acquisitions, per the codebook) are kept, not winsorized. But 24 firm-years with growth above 50% (0.7% of the sample; mean rd_int 0.26 vs 0.07 elsewhere) drive much of the estimate: for reference only, dropping them gives 0.39 (SE 0.03).

**Data decisions.**
- Used the latest R&D vintage (2024-02-15); the oldest file shows 312 zeros that are now blank (255) or positive (57).
- Blank R&D means not reported: 180 firm-years dropped. True zeros kept.
- Codebook says R&D is in USD thousands; vendor R&D/sales times sales shows millions from FY2015. Rescaled to millions. Vendor rd_intensity is R&D/sales, so unused.
- Pre-2016 vendor rows of 63 firms carry old IDs; mapped to current IDs.
- FY2023 is incomplete (sales 46% of FY2022 at the median), so t ends at 2021.
- Finance excluded by current industry (55 firms). Size class uses year-t assets, not the FY2022 class in firms.csv.
