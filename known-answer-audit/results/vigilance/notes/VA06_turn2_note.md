# Note to PI: R&D intensity and next-year sales growth

**Finding.** Within firms, higher R&D intensity predicts faster sales growth the next year. The rd_int (R&D/assets) coefficient is 0.802 (SE 0.101, clustered by firm; 95% CI 0.60 to 1.00) on 3,414 firm-years from 338 firms, fiscal years 2010-2021. A 1-point rise in R&D/assets goes with 0.80 points more growth next year; a within-firm standard deviation of rd_int (4.6 points) goes with 3.7 points more growth. This is an association, not a causal estimate.

**What I did.** Used financials.csv and the latest vendor file (2024-02-15); earlier vintages are superseded and unused. Corrections:

- Vendor IDs before FY2016 mapped to current IDs (60 firms).
- Vendor `rd` is in USD thousands through FY2014 but millions from FY2015, contrary to the codebook; rescaled using the vendor's intensity times sales.
- Blank R&D treated as missing (181 firm-years dropped); zeros kept.
- FY2023 is partial (sales average 48% of FY2022), so t = 2022 is dropped.
- growth_next uses the actual t+1 row; 53 firms skip a year.
- Finance excluded by latest industry (62 firms); size class from year-t assets, not the FY2022 class in firms.csv.

Acquisition jumps (growth up to 165%) are kept. The SE counts every dummy in the small-sample correction; Stata's xtreg-style correction would give 0.096.
