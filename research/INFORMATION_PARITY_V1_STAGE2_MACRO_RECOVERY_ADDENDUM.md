# Information Parity V1 — Stage 2 Macro Recovery Addendum

Status: **FROZEN AFTER FULL-TRAIN RUN 1 FAILURE, BEFORE MACRO PARSER CORRECTION**

Parent:
- `research/INFORMATION_PARITY_V1_STAGE2_SCHEMA_PREREGISTRATION.md`
- `research/INFORMATION_PARITY_V1_STAGE2_MACRO_ADDENDUM.md`
- D-070 normalized first-party schedule fallback
- D-082 accepted exact-runtime full-TRAIN deterministic preflight

Trigger:
GitHub Actions full-TRAIN run **37434856203** acquired/synchronized 2016-2021 market data and built continuous synthetic DXY successfully, then failed at the scheduled-macro normalization gate.

No XAUUSD economic outcome, trade label, P&L, or sealed-period result was inspected to make this correction.

## A20 — Federal Reserve 2021 FOMC index transport

The legacy URL pattern used successfully for 2016-2020:

`https://www.federalreserve.gov/monetarypolicy/fomchistorical{year}.htm`

returns HTTP 404 for 2021.

For 2021, Stage 2 may discover statement links from the Federal Reserve's first-party FOMC press-release index:

`https://www.federalreserve.gov/newsevents/pressreleases/2021-press-fomc.htm`

The statement pages themselves remain the authoritative source of exact release time, and only links matching the frozen FOMC-statement identity `monetaryYYYYMMDDa.htm` are admitted.

This is a transport/index correction within the already-admitted Federal Reserve source family, not a new information source.

## A21 — BEA national-GDP title and embargo syntax

The BEA national-GDP archive contains legitimate national releases whose titles begin with syntactic variants of the same series name, including:

- `Gross Domestic Product,`
- `Gross Domestic Product:`
- `Gross Domestic Product (`

The previous parser admitted only the comma form. That excluded legitimate national releases and produced GDP counts below the preregistered floor in 2018, 2020 and 2021.

Stage 2 therefore admits a BEA archive candidate only when:
1. its normalized title starts with exactly `Gross Domestic Product`; and
2. the immediately following character is one of comma, colon, or opening parenthesis.

This continues to exclude distinct products such as:
- Gross Domestic Product by State;
- Gross Domestic Product by County;
- Gross Domestic Product by Industry.

The embargo parser may accept punctuation-only variants between `A.M./P.M.` and `EDT/EST/ET`, including both:
- `8:30 A.M. EDT, ...`
- `8:30 A.M., EDT, ...`

No release value is ingested.

## A22 — Do not let macro transport failures consume another full market acquisition

Before another 2016-2021 full-TRAIN provider-data build:
1. add deterministic offline regressions for A20/A21;
2. pass the Stage 2 deterministic preflight off-CI;
3. confirm the changed implementation under the frozen exact runtime;
4. run one intentionally scoped **macro-only network confirmation** for 2016-2021;
5. only if macro coverage is PASS may another full same-snapshot build be launched.

The full-TRAIN workflow must also validate macro readiness before expensive XAUUSD/FX acquisition. This reordering does not weaken the same-snapshot rule: the final accepted full build still acquires and builds all admitted 2016-2021 sources within one workflow job.

## Governance

- 2016-2021 TRAIN only.
- 2022-2025 XAUUSD remain sealed.
- no macro actual/forecast/previous/revision/surprise fields;
- no profitability/model work;
- no third-party economic calendar;
- no source substitution.
