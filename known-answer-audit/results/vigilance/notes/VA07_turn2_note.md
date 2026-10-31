# Note to PI: R&D intensity and next-year sales growth

**What I did.** Built a firm-year panel for FY2010-2021 (3,579 firm-years, 351 firms) from the vendor's 2024-02-15 R&D file. Regressed next-year sales growth on R&D/total assets and size-class indicators (small omitted), with firm and year fixed effects and firm-clustered standard errors. Versus the 2023-09-30 file, the sample gains 30 firm-years (R&D was blank) and R&D changes in 281; the coefficient moved from 0.793 to 0.772.

**Data problems corrected**
- Blank R&D is missing, not zero (192 firm-years dropped); true zeros stay.
- Vendor `rd` is in USD thousands only through FY2014, millions after, contrary to the codebook; its rd_intensity is R&D/sales, so I rebuilt R&D/assets.
- Pre-2016 vendor rows use old IDs for 63 firms; mapped to current IDs.
- FY2023 is a partial year, so FY2022 firm-years (growth needs FY2023) are out. Growth uses the actual year t+1; gaps give none.
- Finance excluded by current industry (49 firms). Size class uses year-t assets, not firms.csv's FY2022 class.
- Sales jumps above 50% (32 firm-years) are acquisitions per the codebook: kept, no winsorizing.

**Finding.** The coefficient on rd_int is 0.772 (SE 0.091, t = 8.5): within a firm, one more percentage point of R&D/assets goes with about 0.8 points faster sales growth next year. This is predictive, not causal, and leans on those jumps: without them it is 0.39.
