# R&D intensity and sales growth

**Finding.** Yes. With firm and year fixed effects, the rd_int coefficient is 0.80 (SE 0.10, clustered by firm; p < 0.001). One percentage point more R&D/assets goes with 0.8 points faster sales growth the next year (3,414 firm-years, 338 firms, t = 2010-2021). This is a within-firm association, not causal. It leans on 31 large sales jumps (growth above 50%, acquisitions per the README), which I kept; without them the coefficient is 0.44 (SE 0.03). Scaled as Stata's reghdfe does, the SE would be 0.096.

**What I did**
- Used the newest vendor R&D file (2024-02-15); earlier vintages are superseded. Blank R&D is missing; true zeros are kept.
- The vendor's rd is in USD thousands through FY2014 but millions from FY2015, contrary to the README (checked against its own R&D/sales). I converted to millions and divided by total assets, not sales as the vendor's rd_intensity does.
- Mapped 60 firms' pre-2016 vendor rows from old to current IDs.
- FY2023 is incomplete (sales fall 52% on average), so the last t is 2021. 53 firms skip a year, so growth_next uses actual t+1 sales.
- Industry is each firm's latest (62 Finance firms dropped). Size class uses assets in year t, not the static FY2022 class.
