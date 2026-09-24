# DATA_SOURCE_001 — Free public XAU/USD feed

## Decision

Primary historical source for EXP-001: Dukascopy public historical data feed, accessed through the pinned `dukascopy-node` CLI.

- Instrument: `xauusd`
- Primary resolution for first implementation: `m1`
- Timestamp basis: UTC / Unix epoch milliseconds
- Primary price side: BID for the initial M1 feasibility dataset
- Access method: public historical feed, no API key or paid subscription
- Downloader version: `dukascopy-node@1.50.0`

Dukascopy's public historical-data tooling exposes XAU/USD data and the selected downloader documents XAU/USD M1 availability back to 2003.

## Why M1 first

EXP-001's first purpose is to test the feasibility of the +$5 / -$3 / 60-minute labeling and the predictive pipeline. M1 is sufficient to:

1. construct a large chronological dataset;
2. implement deterministic first-pass labels;
3. identify potentially ambiguous same-minute barrier touches;
4. measure how often M1 granularity is insufficient.

Any sample where target and adverse barrier could both have occurred inside one M1 bar without provable ordering must be marked ambiguous and excluded from directional success/failure statistics until tick-level adjudication is added.

## Secondary cross-check

Stooq may be used later only for coarse daily-level sanity checks. It is not the primary EXP-001 research feed.

## Data storage policy

Do not commit large raw historical datasets to Git.

Generated historical data should live under ignored local paths such as:

`data/raw/dukascopy/xauusd/m1/`

Small deterministic smoke-test fixtures may be committed under `tests/fixtures/`.

## Reproducibility

Every downloaded production/research file should eventually receive:

- source identifier;
- instrument;
- timeframe;
- date range;
- download tool/version;
- SHA-256;
- row count;
- first timestamp;
- last timestamp;
- validation status.
