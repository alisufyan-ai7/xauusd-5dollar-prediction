# BLS 2017-2021 Schedule Snapshot Provenance

Status: **VERIFIED NORMALIZED REFERENCE METADATA**

Purpose:

Complete the D-070 transport fallback required before the one-shot 2016-2021 Stage 2 TRAIN build.

The official BLS historical schedule pages are the admitted source. GitHub Actions has previously received HTTP 403 from BLS, so the repository stores only the small normalized schedule metadata needed for reproducible causal alignment.

## Official sources

- 2017: `https://www.bls.gov/schedule/2017/home.htm`
- 2018: `https://www.bls.gov/schedule/2018/home.htm`
- 2019: `https://www.bls.gov/schedule/2019/home.htm`
- 2020: `https://www.bls.gov/schedule/2020/home.htm`
- 2021: `https://www.bls.gov/schedule/2021/home.htm`

The schedule dates/times were checked against these first-party historical pages before the snapshots were frozen.

## Included families

Each annual snapshot contains:

- Employment Situation / NFP: 12 rows
- Consumer Price Index / CPI: 12 rows
- Job Openings and Labor Turnover Survey / JOLTS: 12 rows

Total per year:
- 36 rows

No release actual, forecast, previous, revision, consensus or surprise value is present.

## Normalization

- BLS source times are interpreted in `America/New_York`.
- Historical DST conversion is performed with IANA timezone rules.
- Every row stores the exact official BLS year-page URL.
- `scheduled_time_local` retains the historical Eastern UTC offset.
- `scheduled_time_utc` is the deterministic UTC conversion.
- Event IDs follow the frozen Stage 2 identity rule:
  `SHA256("BLS|family|scheduled_time_utc|release_stage|source_url")[:20]`.
- Normalization version:
  `IPV1_MACRO_SCHEDULE_V1`.

## Frozen files and identities

### 2017

File:
`research/reference/information-parity-v1/bls-schedule-2017.csv`

Rows:
36

Normalized file SHA-256:
`8bdaa70a399ff3ebf7e150b939a0ee364f9e627d89b9bc0ac7e8ea2d24efd38b`

Git blob identity at verification:
`bf177ee4929ddc0d0a4ede353afd49bfdd593499`

### 2018

File:
`research/reference/information-parity-v1/bls-schedule-2018.csv`

Rows:
36

Normalized file SHA-256:
`f4a30236da8c45899036d88954fc97811ececc6da5095c853c21d070798c4444`

Git blob identity at verification:
`19a10efa50cc36ac5747c7189a4a459e646cd913`

### 2019

File:
`research/reference/information-parity-v1/bls-schedule-2019.csv`

Rows:
36

Normalized file SHA-256:
`eda778d20cb4519a8a7d7992528929def9e7813259ce65382d6118d588d85f85`

Git blob identity at verification:
`644fc24127636c0c37a6ec840069e36bdea2858e`

### 2020

File:
`research/reference/information-parity-v1/bls-schedule-2020.csv`

Rows:
36

Normalized file SHA-256:
`dfd17e66d06a59c2582bf01c5686dad6709047f4feb2d26aa45bfea92af198ea`

Git blob identity at verification:
`fabaff1aadf884eaf78f44057d68e6f088ddd01a`

### 2021

File:
`research/reference/information-parity-v1/bls-schedule-2021.csv`

Rows:
36

Normalized file SHA-256:
`becb90360ea820f91a11f621f51c17b836d666bc74e009f5e9badfbeff52fbbb`

Git blob identity at verification:
`859f01b6e5930d0aad20cc299013aa89e7152617`

## Integrity boundary

These files contain schedule metadata only.

They do not contain:
- economic release values;
- consensus/forecast values;
- revisions;
- surprise calculations;
- XAUUSD future outcomes;
- trade labels;
- P&L.

They are repository-controlled reference metadata, not raw provider-market data.

The existing 2016 snapshot remains governed by:
`research/INFORMATION_PARITY_V1_BLS_2016_SNAPSHOT_PROVENANCE.md`.

With 2016-2021 snapshots present, the full-TRAIN static input verifier can fail fast before any expensive provider acquisition if a snapshot is missing or malformed.
