# Note to PI

**Finding.** Yes. The coefficient on R&D/assets is 0.904 (SE 0.097, p < 0.001): within a firm, one percentage point more R&D/assets goes with about 0.9 points more sales growth the next year, net of firm, year and size-class effects. This is an association, not a causal estimate.

**What I did.** 3,664 firm-years, 357 firms, fiscal years 2010-2021. OLS with firm and year fixed effects and medium/large indicators (small omitted); SEs clustered by firm (default small-sample correction, counting firm dummies; the xtreg/reghdfe convention gives 0.092).

**Data problems fixed.**
- Used the current vendor file (2024-02-15). Versus the 2023-09-30 file, 58 blanks are filled and 380 values revised, moving the coefficient from 0.916 to 0.904. Blanks stay missing.
- Vendor R&D is in thousands through FY2014 but millions from FY2015, contrary to the codebook. Checked against the vendor's own R&D/sales; converted.
- The vendor file uses old IDs before FY2016 (56 firms); mapped to current IDs.
- FY2023 is a partial year (median sales 49% of FY2022; files are complete through FY2022), so t ends at 2021.
- Next-year sales are matched on the exact year (some firms skip a year).
- Finance firms are identified by current industry (43 excluded); size class uses assets in year t, not the FY2022 label. Acquisition jumps stay in.
