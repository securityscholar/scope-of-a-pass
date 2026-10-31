# R&D intensity and next-year sales growth

**Finding.** R&D intensity predicts faster sales growth the following year. The coefficient on rd_int (R&D / total assets) is 0.716 (SE 0.105; p < 0.001; 3,506 firm-years, 349 firms). Within a firm, one more percentage point of R&D/assets goes with 0.72 points more growth next year. Association, not causation.

**Caveat.** Dropping the 24 firm-years with growth above 50% (presumably the acquisitions the codebook says to keep) cuts the coefficient to 0.348 (SE 0.028). Sign and significance hold; the size falls 51%.

**Sample and model.** Fiscal years 2010 to 2021, excluding 51 firms whose current industry is Finance. OLS with firm and year fixed effects and size-class dummies (small omitted) from year-t assets, not the FY2022 label in firms.csv. SEs clustered by firm (statsmodels default correction). No winsorizing.

**Data decisions.**
- R&D comes from the current vendor file (2024-02-15); 2 earlier versions are superseded.
- Blank R&D is missing (192 firm-years dropped); reported zeros stay.
- rd is in thousands through FY2014 but millions from FY2015, contrary to the codebook; converted.
- Vendor IDs before FY2016 were mapped to current IDs.
- Data are complete only through FY2022, so FY2023 is unused.
- Growth uses the actual next fiscal year; 54 firm-years before a missing year are dropped, not bridged.
