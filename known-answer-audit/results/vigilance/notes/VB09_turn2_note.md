# Note to the PI: R&D intensity and next-year sales growth

**Finding.** Higher R&D intensity predicts faster next-year sales growth. The coefficient on rd_int is 0.887 (SE 0.138, clustered by firm, p < 0.001; 3,425 firm-years, 341 firms): within a firm, one percentage point more R&D/assets goes with 0.89 percentage points more sales growth in t+1. This is an association, not a causal effect. It leans on 30 large sales jumps (growth of 88% to 159%, presumably the codebook's acquisitions), which I kept; without them the coefficient is 0.331 (SE 0.026).

**Model.** OLS with firm and year fixed effects and size class indicators; non-Finance firms, fiscal years 2010-2021.

**Data fixes**
- Files are complete only through FY2022; FY2023 is a partial year, so t = 2022 is out.
- Vendor rd is in USD thousands through FY2014 but millions from FY2015, contrary to the codebook (checked against rd_intensity x sales). Converted to millions; please confirm with the data team.
- Latest vendor file (2024-02-15) used. Blank R&D is missing; reported zeros are kept.
- Vendor rows before 2016 use old firm ids (60 firms); mapped to current ids.
- rd_int is R&D / total assets, not the vendor's R&D / sales. Size class uses assets in year t, not firms.csv.
- Finance is judged on current industry (latest firms.csv row).
- growth_next needs sales in exactly t+1.
