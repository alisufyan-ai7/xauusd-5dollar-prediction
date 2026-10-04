# Information Parity V1 — Stage 2 Full-TRAIN Continuity Addendum

Status: **FROZEN BEFORE FULL 2016-2021 BUILD**

Parent:
- `research/INFORMATION_PARITY_V1_STAGE2_SCHEMA_PREREGISTRATION.md`
- `research/INFORMATION_PARITY_V1_STAGE2_IMPLEMENTATION_ADDENDUM.md`
- D-078 corrected bounded smoke acceptance

## Purpose

Prevent artificial information resets at calendar-year boundaries in the full TRAIN Information Parity Layer.

This clarification was made before the full 2016-2021 build and without inspecting any economic outcome.

## A15 — TRAIN is one continuous causal history

The full Stage 2 TRAIN interval is:

`2016-01-01 00:00 UTC <= bar_start < 2022-01-01 00:00 UTC`

It must be treated as one continuous causal history.

Only the beginning of 2016 is a permitted cold start.

The following must **not** reset merely because the calendar year changes from 2016→2017, 2017→2018, etc.:

- rolling M1 volume/spread context;
- completed multi-timeframe history;
- confirmed swing state;
- active FVG state;
- D1/W1 history;
- previous-day state;
- synthetic-DXY changes / rolling realized-volatility state;
- backward DXY availability state.

## A16 — Annual physical partitioning is storage only

Annual output files remain permitted for storage/audit convenience.

However:

> year partitioning occurs only **after** the relevant causal state has been computed from the continuous 2016-2021 TRAIN history.

A January decision row in 2017-2021 may therefore use prior TRAIN information from the preceding year when that information was already available at the decision timestamp.

No pre-2016 market acquisition is introduced.

## A17 — Continuous DXY

The six Dukascopy FX constituent histories must be concatenated in chronological order across 2016-2021 before the canonical synthetic DXY transforms are computed.

Do not independently reset:
- 1m/5m/15m/60m/240m DXY changes;
- 15m/60m/240m DXY rolling-volatility state
at January 1 of each year.

## A18 — Full-build same-snapshot rule

The accepted full TRAIN run must:

1. acquire all permitted 2016-2021 XAUUSD and DXY-constituent M1 files in one workflow job;
2. hash those exact raw annual files;
3. concatenate/normalize from those exact files;
4. acquire/normalize the 2016-2021 macro schedule in the same workflow job;
5. build the continuous causal state once;
6. partition normalized outputs by year only after state construction;
7. validate every annual partition plus full-range continuity checks;
8. upload only compact reports/manifests/hashes, not raw provider files or the full normalized layer.

## A19 — Boundary integrity checks

The full TRAIN validator/summary must explicitly check at least the 2016→2017, 2017→2018, 2018→2019, 2019→2020 and 2020→2021 boundaries.

For each boundary, record whether the first decision rows of the new year have causally available:
- rolling market readiness;
- previous-day state;
- DXY state.

Expected missingness is allowed only when the underlying provider history itself is missing or the frozen causal rule legitimately has no available state.

A blanket January-1 reset is invalid.
