**Finding.** Yes. Within firms, higher R&D/assets is followed by faster sales growth the next year. Coefficient on rd_int (R&D / total assets): 0.899 (SE 0.104, clustered by firm; 95% CI 0.69 to 1.10); 3,570 firm-years (FY2010-2021), 346 firms, firm and year fixed effects, size-class indicators. One percentage point more R&D/assets goes with 0.90 percentage points faster growth. A within-firm association, not a causal estimate.

**What I did**
- Dropped the 54 firms whose current (latest as_of) industry is Finance.
- Used FY2010-2021 as year t: financials are complete through FY2022; FY2023 rows are partial-year (median sales 47% of FY2022).
- Matched t+1 sales on the exact fiscal year, so gaps never create two-year growth.
- Used the current (2024-02-15) vendor revision; the superseded 2023-09-30 file gave 0.921 (N = 3,533). Blank R&D is missing (dropped); true zeros kept.
- **Unit problem:** vendor rd is in thousands through FY2014 but millions from FY2015, contradicting the codebook (checked against the vendor's R&D/sales). I converted to millions; codebook units would give 0.63. Please confirm with the vendor.
- Mapped old to current IDs for 72 firms (vendor rows before FY2016).
- Size class from year-t assets, not the fixed FY2022 label.
- Kept acquisition sales jumps; no winsorizing.

SEs: Stata-style small-sample correction; statsmodels' dummy default is 5% larger.
