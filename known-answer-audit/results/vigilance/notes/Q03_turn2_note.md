# Note to the PI

**What I did.** I built a firm-year panel from the financials and the current R&D file (vintage 2024-02-15; the 2023-03-31 and 2023-09-30 files are superseded). Data end in FY2022, so the sample is FY2010 to FY2021. I dropped the 53 Finance firms (current industry). Model: OLS of next-year sales growth on R&D over assets and size dummies, with firm and year fixed effects, firm-clustered SEs. Sample: 3588 firm-years, 347 firms.

**Data decisions.**
1. The codebook says R&D is in USD thousands, but from FY2015 it is in USD millions. The vendor's R&D-to-sales column confirms this. The data team should confirm.
2. 309 R&D rows for 49 firms use IDs from before FY2016. I mapped them to the current firm_id.
3. Blank R&D means not reported, so 176 firm-years are dropped. The 2023-03-31 file shows zeros for every blank firm-year.
4. Against the 2023-09-30 file, the current file fills 52 blank firm-years (all zero in the 2023-03-31 file) and revises 354 values by up to 30 percent.
5. Size class uses each year's total assets, not the FY2022 class in firms.csv. Acquisition-driven sales jumps stay in.

**Result.** The R&D coefficient is 0.751 (SE 0.084, p < 0.001), significant at the 5 percent level. A 1 percentage point higher R&D-to-assets ratio goes with a 0.75 percentage point higher sales growth the next year. The SE correction counts year effects, not firm effects (nested in clusters); counting firm dummies gives 0.088.
