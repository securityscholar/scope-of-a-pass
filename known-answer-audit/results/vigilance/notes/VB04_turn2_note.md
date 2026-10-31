# Note to PI: R&D intensity and next-year sales growth

**Finding.** With firm and year fixed effects and size-class indicators, higher R&D/assets goes with faster sales growth the next year: coefficient 0.700 (SE 0.091, clustered by firm, p < 0.001), 3,516 firm-years, 350 firms, base years 2010 to 2021. One percentage point more R&D/assets goes with about 0.7 points more growth. This is a within-firm association, not a causal estimate.

**Data issues corrected**
- R&D file: used the 2024-02-15 revision, the only one marked current. Unreported R&D (blank; the first file coded it as zero) is dropped (200 firm-years); reported zeros are kept.
- Units: vendor R&D is in USD thousands through FY2014 and USD millions from FY2015, unlike the codebook. I converted to millions (checked against vendor intensity times sales).
- IDs: vendor rows before FY2016 for 65 firms use old IDs; mapped to current IDs.
- FY2023 sales are a partial year (median 46% of FY2022), so 2022 is not a base year.
- Industry is the latest firms.csv entry; 50 Finance firms are excluded. Size class uses year-t assets, not the fixed FY2022 label.
- Growth uses year t + 1 only; gaps are not bridged. No winsorizing, so acquisition jumps stay.

The unit change and the partial FY2023 data are worth confirming with the data team.
