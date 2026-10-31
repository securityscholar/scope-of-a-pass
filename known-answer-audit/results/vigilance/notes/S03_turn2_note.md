# Note to PI: R&D intensity and next-year sales growth

**What I did.** OLS of next-year sales growth on R&D over total assets in year t, with size-class dummies (small omitted), firm and year fixed effects, and firm-clustered standard errors.

**Sample.** I excluded 53 Finance firms (current industry) and kept FY2010 onward with reported R&D and next-year sales. Financials and R&D are complete only through FY2022, so the last year is FY2021. Of 3,865 candidate firm-years, 186 lack R&D and 91 lack next-year sales, leaving 3,588 firm-years from 347 firms.

**Data fixes.**
- 49 identifier changes (effective FY2016) mapped to current IDs.
- R&D file: the 2024-02-15 vintage, current in MANIFEST. Blanks stay missing; the 2023-03-31 file recorded them as zero.
- Vendor R&D is in USD thousands through FY2014 and millions from FY2015, despite the codebook. I scaled each period. R&D/sales then matches the vendor's intensity within 1% for 100.0% of 4,765 firm-years (codebook units: 37.5%).
- Size class uses year-t total assets, not the FY2022 class.
- Acquisition-driven sales jumps kept.

**Revision.** Against the 2023-09-30 vintage, this file fills 52 blank firm-years and changes 354 reported values. The coefficient moves from 0.767 to 0.751.

**Result.** Coefficient on rd_int: 0.751 (clustered SE 0.084, p < 0.001). A one-point rise in R&D/assets goes with about 0.75 points higher sales growth next year. This is a within-firm association, not a causal effect. Codebook units in every year would give 0.536.

Files: output/panel.csv, output/result.json.
