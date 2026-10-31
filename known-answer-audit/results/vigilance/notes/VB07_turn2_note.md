# R&D intensity and next-year sales growth

**Finding.** The coefficient on rd_int is 0.772 (SE 0.091, clustered by firm, p < 0.001; 3,579 firm-years, 351 firms). Within a firm, 1 percentage point more R&D/assets goes with 0.77 percentage points more sales growth the next year. This is an association, not a causal effect. The estimate is sensitive to 32 acquisition-sized jumps (next-year growth above 50%; mean rd_int 0.25 against 0.07 elsewhere): without them the coefficient is 0.393 (SE 0.024).

**What I did.** Fiscal years 2010-2021, growth measured to t+1. The data are complete only through FY2022, so partial FY2023 rows are dropped. Data decisions:
- R&D from the latest vendor file (2024-02-15), the only one the manifest marks current; earlier vintages are superseded.
- Vendor rows before FY2016 use old IDs; I mapped 375 rows (63 firms) to current IDs.
- Vendor R&D is in USD thousands through FY2014 and millions from FY2015, contrary to the codebook. I converted to millions and divided by total assets (the vendor's rd_intensity is per sales, so unused).
- Blank R&D is missing (192 firm-years dropped); true zeros are kept.
- Growth uses the actual t+1 record, so a missing year gives no growth.
- Size class comes from year-t assets, not the FY2022 label.
- Finance is judged on current industry (49 firms out).
- Acquisition jumps are kept, as the codebook says they are real.
