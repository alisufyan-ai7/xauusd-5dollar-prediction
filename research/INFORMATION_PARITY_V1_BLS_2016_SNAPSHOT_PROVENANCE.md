# BLS 2016 Schedule Snapshot Provenance

Status: **VERIFIED NORMALIZED REFERENCE METADATA**

File:
`research/reference/information-parity-v1/bls-schedule-2016.csv`

Purpose:
Transport fallback under D-070 for the Stage 2 bounded 2016 smoke build.

Official source:
`https://www.bls.gov/schedule/2016/home.htm`

Included families:
- Employment Situation / NFP: 12 rows
- Consumer Price Index / CPI: 12 rows
- Job Openings and Labor Turnover Survey / JOLTS: 12 rows

Total rows:
36

Normalization:
- BLS source times are Eastern Time.
- `America/New_York` is used for historical DST conversion to UTC.
- Each row stores the official BLS schedule URL.
- No actual, previous, forecast, consensus, revision or surprise values are included.
- Event IDs are deterministic SHA-256 prefixes over agency/family/UTC/stage/source identity.

Why committed:
The official page is publicly readable, but GitHub Actions receives HTTP 403 from BLS. The repository stores only the small normalized schedule metadata needed for reproducible causal alignment, not the raw BLS HTML page.

Verification basis:
The official 2016 BLS schedule was inspected before this snapshot was frozen. The dates/times in the snapshot correspond to the 12 scheduled releases in each included family.

This snapshot is valid only for 2016. Equivalent 2017-2021 snapshots require separate source verification before full TRAIN use.
