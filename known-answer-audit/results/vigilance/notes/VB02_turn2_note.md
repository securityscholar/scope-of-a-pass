**Answer.** Yes, within firms. A one percentage point rise in R&D as a share of total assets goes with 0.82 percentage points more sales growth the next year (coefficient 0.823, SE 0.108, p < 0.001; 3,261 firm-years, 329 firms). The model has firm and year fixed effects, size-class dummies and errors clustered by firm. This is an association, not a causal effect.

**Sensitivity.** 27 firm-years have sales growth above 50%. The codebook says acquisition jumps are real, so I kept them. Without them the coefficient is 0.37 (SE 0.03), 45% of the main estimate, so its size depends on these jumps.

**Data decisions.**
- Used the current R&D file, rd_vendor_2024-02-15.csv (the 2023-09-30 file is superseded; with it the coefficient is 0.833).
- Mapped old vendor ids to current ids for 54 firms (FY2016 change).
- Vendor R&D is in USD thousands through FY2014 and millions after (read off the vendor's R&D-to-sales ratio). I converted it to millions before dividing by assets.
- Blank R&D is dropped; reported zeros are kept.
- Data are complete through FY2022, so the sample runs 2010 to 2021 (growth uses FY2022 sales).
- Finance is excluded by current industry. Size class is recomputed each year from total assets.
- Of 3,571 non-Finance firm-years, 3,261 have R&D and next-year sales.
