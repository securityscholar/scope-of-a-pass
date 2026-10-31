# Note to PI

**Answer.** Yes, within firms. With firm and year effects, the rd_int (R&D / total assets) coefficient is 0.716 (SE 0.105, clustered by firm; p < 0.01) on 3,506 firm-years from 349 firms, base years 2010-2021. One more percentage point of R&D per dollar of assets goes with 0.72 percentage points faster growth next year. Association, not causation.

**Caveat.** The estimate leans on 24 firm-years with next-year sales growth above 50%, which I take to be the acquisitions the codebook mentions (kept; it calls them real). Without them the coefficient falls to 0.348 (SE 0.028), still significant.

**Data decisions.**
- Used the 2024-02-15 vendor file (current). Versus the 2023-09-30 file it adds 39 firm-years and revises R&D values; that file gave 0.727 (SE 0.107). Blank R&D is missing (192 firm-years dropped); true zeros kept.
- Vendor R&D is in thousands through FY2014, millions from FY2015 (undocumented; please confirm); rescaled. Its intensity is per sales, so I recomputed per assets.
- 57 firms have old IDs before 2016 in the vendor file; mapped to current IDs.
- FY2023 is a partial year (median sales 47% of FY2022), so the last base year is 2021. 56 firms skip a year; not bridged.
- Finance is judged on current industry (51 firms out). Size class uses year-t assets, not firms.csv's FY2022 class.
