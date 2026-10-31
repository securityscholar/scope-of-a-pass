# Note to PI: R&D intensity and next-year sales growth

**What I did.** I built a firm-year panel for FY2010 to FY2021 (3,570 firm-years, 346 firms) and regressed next-year sales growth on R&D/assets and size-class indicators (small omitted), with firm and year fixed effects and firm-clustered standard errors.

**Data decisions**
- Used the current R&D file (2024-02-15); the earlier vintages are superseded. Blank R&D means not reported, so those 191 firm-years are dropped; reported zeros are kept.
- Mapped old firm IDs in the vendor file (72 firms, changed FY2016) to current IDs.
- Vendor R&D is in thousands through FY2014 but in millions from FY2015, contrary to the codebook (verified with the vendor's R&D/sales ratio); converted to millions.
- FY2023 is partial, so the last sample year is 2021. A missing year leaves the prior year's growth missing.
- Dropped 54 firms whose current industry is Finance. Size class uses year-t assets.

**Result.** R&D intensity predicts faster sales growth the next year: coefficient 0.899 (SE 0.109, p < 0.001); one point more R&D/assets goes with 0.90 points more growth. The 29 firm-years with growth above 40% look like the acquisitions the codebook calls real, so I kept them; without them the coefficient is 0.424 (SE 0.024).
