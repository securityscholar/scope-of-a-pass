**Sample and model.** Fiscal years 2010 to 2021: 3,596 firm-years, 354 firms. OLS with firm and year fixed effects and firm-clustered standard errors.

**Data decisions.**
- R&D is from the current vendor file (2024-02-15).
- It revises 388 values and fills 61 cells the 2023-09-30 file left blank (44 in the sample). 60 of the fills repeat the firm's median or another year's rd_intensity, so I treat them as imputations and drop them.
- Other blank rd (180 firm-years) is dropped, not set to zero.
- rd_int is R&D over total assets; the vendor's rd_intensity uses sales.
- Vendor rd is in USD thousands through FY2014 but millions from FY2015, contrary to the codebook (verified row by row).
- Old IDs (65 firms, before FY2016) are mapped to current IDs.
- FY2023 is incomplete, so the last usable t is 2021.
- Finance is excluded by each firm's latest industry; size_class_t uses each year's assets, not the FY2022 class in firms.csv.

**Result.** rd_int has coefficient 0.750 (SE 0.086, p < 0.001): a one percentage point higher R&D-to-assets ratio goes with 0.75 points more sales growth next year. The 2023-09-30 file gave 0.763; keeping the imputed values gives 0.745 (N 3,640). Acquisition jumps (33 firm-years, growth above 50%) are kept as the codebook says they are real; without them it is 0.385.
