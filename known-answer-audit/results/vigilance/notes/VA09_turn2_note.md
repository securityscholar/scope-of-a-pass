# Note to PI

**Finding.** Yes: R&D intensity is positively associated with next-year sales growth within firms. Coefficient on rd_int: 0.887 (SE 0.138, clustered by firm), with firm and year fixed effects and size-class dummies; 3,425 firm-years, 341 non-Finance firms, base years FY2010-2021. A one-point rise in R&D/assets goes with 0.89 points more growth. Association, not causation.

**Caution.** 30 firm-years followed by sales jumps above 50% (presumably the acquisitions the codebook says to keep) carry unusually high R&D intensity (mean 0.29 versus 0.07). Without them the coefficient is 0.33 (SE 0.026), still positive.

**Data decisions**
- Used the latest vendor file (2024-02-15); earlier vintages ignored.
- Mapped 60 old vendor IDs (pre-2016 rows) to current IDs.
- Vendor R&D is in USD thousands through FY2014 but millions from FY2015, contrary to the codebook (checked against vendor intensity times sales); harmonized.
- Blank R&D is missing (201 firm-years dropped); zeros kept.
- R&D/assets computed here; the vendor ratio is over sales.
- Dropped 59 firms whose latest industry is Finance.
- Size class uses year-t assets, not the fixed FY2022 class.
- FY2023 is incomplete (sales down 51% on average): last base year FY2021; growth uses exactly year t+1.

SE uses statsmodels' default small-sample factor; Stata-style (firm effects not counted) it is 0.130.
