# Note to PI: R&D intensity and next-year sales growth

**What I did.** Firm-year panel, fiscal years 2010-2021, so next-year sales come from FY2022, the last complete year; FY2023 is a partial year (median sales 46% of FY2022) and was dropped. R&D comes from the 2024-02-15 vendor file; earlier vintages are superseded. The codebook says R&D is in thousands, but the file switches to millions in FY2015 (verified against the vendor's R&D/sales ratio); I converted before dividing by total assets. Old vendor IDs were mapped to current IDs. Blank R&D is missing, not zero. Growth uses the actual year t+1. Size class uses year-t assets, not the FY2022 class in firms.csv. The 50 firms currently in Finance are excluded. Acquisition jumps are kept.

**What I found.** With firm and year fixed effects and firm-clustered SEs (350 firms, 3,516 firm-years), the rd_int coefficient is 0.700 (SE 0.091, t = 7.7). One percentage point more R&D/assets goes with about 0.7 points more sales growth the next year, within firm. The previous vendor file (2023-09-30) gave 0.705 on 32 fewer firm-years.

**Caveat.** Association, not causation. The estimate leans on 22 sales jumps above 50% (presumably the acquisitions) at R&D-intensive firm-years (mean rd_int 0.19 vs 0.06 overall). Without them the coefficient is 0.39 (SE 0.03), still positive.
