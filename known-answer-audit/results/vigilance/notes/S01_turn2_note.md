**Note to PI**

**What I did.** Firm-years t = 2010-2021, firms whose current industry (latest `as_of` row) is not Finance: 3,574 firm-years, 350 firms. rd_int = R&D / assets in t; growth_next = sales(t+1)/sales(t) - 1 on the exact next fiscal year; size class from assets in t. OLS with firm and year fixed effects, small omitted, SEs clustered by firm (0.071 if the firm dummies are left out of the small-sample correction).

**Data issues handled.**
- Current R&D file (2024-02-15); earlier vintages are superseded.
- 68 retired vendor IDs (FY2009-2015) mapped to current IDs.
- Vendor `rd` is in USD thousands through FY2014 but millions from FY2015, judging by its own R&D/sales; the codebook says thousands throughout. Converted to millions; please confirm with the data team.
- FY2023 is partial (median sales change -53%), so t = 2022 drops out.
- Blank R&D is missing, not zero.

**Result.** R&D intensity is positively associated with next-year sales growth: rd_int coefficient 0.685, SE 0.075. Within a firm, one percentage point more R&D/assets goes with 0.69 points more growth the next year (an association, not a causal effect). The 25 large sales jumps (growth above 50%, presumably acquisitions) are kept; they sit at high rd_int (mean 0.20 vs 0.07). Diagnostic only: without them the coefficient is 0.427 (SE 0.029).
