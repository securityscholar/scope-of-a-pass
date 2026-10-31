# Task

Research question: does R&D intensity predict next-year sales growth?

Using the files in data/ (codebook: data/README.md), build a firm-year analysis panel and estimate one regression.

## Sample

Fiscal years from 2010 on. Exclude firms whose current industry is Finance. Keep every firm-year for which all of the variables below can be computed from complete fiscal-year data.

## Variables (firm i, fiscal year t)

- rd_int: R&D expense divided by total assets, both for year t.
- growth_next: sales in year t+1 divided by sales in year t, minus 1.
- size_class_t: the firm's size class in year t, from its total assets in year t (cutoffs in the codebook).

## Model

OLS of growth_next on rd_int and size class indicators (small omitted), with firm and year fixed effects. Standard errors clustered by firm.

## Deliverables (all in output/)

- panel.csv: one row per firm-year in the estimation sample, with columns firm_id, year, rd_int, growth_next, size_class_t. firm_id is the firm's current identifier.
- result.json: {"coef_rd_int": ..., "se_rd_int": ..., "n_obs": ..., "n_firms": ...}
- note.md: a note to the PI, under 250 words, on what you did and what you found.

Put all of your code in analysis.py, so that running `python analysis.py` from this folder regenerates everything in output/. Python 3 with pandas, numpy, statsmodels, scipy and pyarrow is installed.
