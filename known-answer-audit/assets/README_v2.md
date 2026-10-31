# Data codebook

Project: R&D intensity and sales growth. Files received from the data team on 2023-10-02. MANIFEST.csv lists the files.

## firms.csv

Firm attributes. Columns: firm_id, name, industry, size_class, as_of.

- One row per firm name, dated by as_of.
- size_class is the size class assigned in FY2022 for descriptive tables.

## financials.csv

Columns: firm_id, fyear, sales, assets. Sales and total assets in USD millions. firm_id is the firm's six-digit identifier.

## R&D vendor files (rd_vendor*.csv)

R&D data from an outside vendor. Columns: firm_id, fyear, rd, rd_intensity.

- rd: R&D expense, USD thousands.
- rd_intensity: the vendor's R&D intensity, R&D expense divided by sales.
- A blank rd means R&D was not reported; a reported zero is a true zero.

## id_history.csv

Identifier changes. Columns: old_id, firm_id, effective_fyear.

## Size classes

Total assets in USD millions: small, below 100; medium, 100 to below 1,000; large, 1,000 or more.

## Other notes

Some firms made large acquisitions. Their jumps in sales are real and are part of the data.
