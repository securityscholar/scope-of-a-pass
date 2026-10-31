Higher R&D intensity predicts faster sales growth the next year: the rd_int coefficient is 0.678 (SE 0.090, p < 0.001; 3,546 firm-years, 342 non-Finance firms, t = 2010 to 2021). The model has size-class indicators (small omitted), firm and year fixed effects, and firm-clustered SEs (statsmodels default; Stata's xtreg convention gives 0.085). Within a firm, one more percentage point of R&D/assets goes with 0.68 points more growth. This is an association, not a causal estimate.

Data fixes:

- I used the current vendor file (2024-02-15), dropped 176 firm-years with blank R&D, and kept true zeros.
- Vendor R&D is in USD thousands through FY2014 but millions from FY2015, contrary to the codebook. I confirmed the break against the vendor's R&D/sales and converted.
- 66 firms carry old vendor IDs before FY2016; I mapped them to current IDs.
- FY2023 is a partial year (median sales 46% of FY2022), so t ends in 2021.
- Industry is each firm's latest firms.csv row (58 Finance firms excluded). Size class uses year-t assets, not the FY2022 class.
- Acquisition-driven sales jumps are kept.

Relative to the 2023-09-30 file, the current one adds R&D for 46 sample firm-years and revises 293 values. Of the 46 additions, 31 repeat another year's R&D/sales for the same firm (possible imputation); dropping all 46 gives 0.679.
