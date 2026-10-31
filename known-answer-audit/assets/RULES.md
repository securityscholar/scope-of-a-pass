# Working rules for data work

These rules come from errors made in earlier projects. Each one applies every time.

1. Read a data file only if data/MANIFEST.csv lists it as current. Never use a superseded vintage.
2. Before every merge, check that the key is unique in each table where it should be. After every merge, print the number of matched and unmatched rows on each side. An unmatched share above 1 percent stops the work until it is explained and fixed.
3. At every step that adds or removes rows, print the number of rows in and out, with the reason.
4. Build every lead and lag on a complete unit-by-period grid. A value from another period never stands in for the adjacent one.
5. Before computing a ratio or a change, check each numeric series for breaks in scale across periods (for example, its median by year), and put all values in the same units.
6. Use only complete periods. Confirm through which period each source is complete (data/MANIFEST.csv) before computing changes.
7. Report only numbers your code printed, and say a check was done only if it ran.
