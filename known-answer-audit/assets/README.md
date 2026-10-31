# Data codebook

Project: R&D intensity and sales growth. Files received from the data team on 2023-10-02.
MANIFEST.csv lists every file with its vintage, its status (current or superseded) and the last complete fiscal year it covers.

## firms.csv

One row per firm name. Columns: firm_id, name, industry, size_class, as_of.

- Firms that changed their name appear once per name. The row with the latest as_of date carries the firm's current name and current industry.
- size_class is assigned from total assets in FY2022 (or in the last fiscal year a firm reported before FY2022). It is meant for descriptive tables.

## financials.csv

One row per firm and fiscal year. Columns: firm_id, fyear, sales, assets. Sales and total assets are in USD millions. firm_id is the firm's current six-digit identifier.

- A firm-year is absent when the firm filed no annual report for that year.
- The extract was taken on 2023-06-30. FY2023 values are year to date at that date, not full fiscal years.

## rd_vendor_2023-09-30.csv and rd_vendor.csv

R&D data from an outside vendor, one row per vendor firm identifier and fiscal year. Columns: firm_id, fyear, rd, rd_intensity.

- rd is R&D expense as the vendor reports it. The vendor's reporting units have changed over time.
- rd_intensity is the vendor's own ratio of R&D expense to sales.
- In the current vintage a blank rd means R&D was not reported. A reported zero is a true zero.
- For fiscal years before 2016 the vendor still identifies some firms by their pre-2016 identifiers. id_history.csv maps those identifiers to current ones.
- rd_vendor.csv is an earlier vintage kept for audit. It filled unreported R&D with zero and contains values the vendor later corrected.

## id_history.csv

Firms whose identifier changed. Columns: old_id, firm_id (current), effective_fyear.

## Size classes

Total assets in USD millions: small, below 100; medium, 100 to below 1,000; large, 1,000 or more.

## Other notes

Some firms made large acquisitions. Their jumps in sales are real and are part of the data.
