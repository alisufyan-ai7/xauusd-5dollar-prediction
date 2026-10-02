# Information Parity V1 — Stage 2 Implementation Addendum

Status: **FROZEN BEFORE STAGE 2 EMPIRICAL BUILD**

Parent:
`research/INFORMATION_PARITY_V1_STAGE2_SCHEMA_PREREGISTRATION.md`

Purpose:

Resolve implementation details that were underspecified in the frozen Stage 2 schema **before any full TRAIN information-layer build is run**.

No XAUUSD outcome/P&L information was inspected to make these choices.

## A1 — Add logical `macro_event_state` table

The parent specification requires event-state fields at each decision timestamp but the minimum logical-table list accidentally omitted a dedicated table.

Stage 2 therefore adds:

`macro_event_state`

Key:
- `decision_time_ms`

Required fields:
- `previous_event_families`
- `minutes_since_previous_event`
- `next_event_families`
- `minutes_to_next_event`
- `events_prior_120m_count`
- `events_next_120m_count`
- `event_0_15m_before`
- `event_15_60m_before`
- `event_0_15m_after`
- `event_15_60m_after`
- `event_60_120m_after`
- `macro_schedule_available`

When simultaneous events occur:
- families are sorted lexicographically and joined with `|`;
- the distance refers to the shared event timestamp.

This is a schema-completeness correction, not a new information source.

## A2 — Higher-timeframe provider-volume aggregation

For M3/M5/M15/M30/H1/H4:

`volume = sum(bid_volume + ask_volume)`

across the exact completed constituent M1 bars.

This is named/documented as a **provider participation proxy**, not centralized traded volume.

D1 and W1 sum the already-normalized child-bar volume.

## A3 — Nearest active FVG selection

At each XAUUSD decision time and for each timeframe M5/M15/H1/H4:

1. process all completed-timeframe FVG creation/invalidation events whose availability time is <= decision time;
2. evaluate currently active FVG intervals against current XAUUSD BID close;
3. interval distance is:
   - 0 when price is inside [lower, upper];
   - lower-price when price < lower;
   - price-upper when price > upper;
4. choose the minimum absolute interval distance;
5. exact distance tie => newest creation time wins;
6. expose lower, upper, signed distance, creation time, and age minutes.

Bullish and bearish FVGs are selected independently.

No age cutoff is introduced in Stage 2.

## A4 — Confirmed swing selection

For M5/M15/H1/H4:
- last confirmed swing high and last confirmed swing low are carried forward separately;
- each includes level, pivot-bar time, and confirmation/availability time;
- no swing becomes visible before its two-right-bar confirmation closes.

## A5 — Physical format

Generated normalized Stage 2 tables use:
- UTF-8 CSV.GZ for full annual tables;
- JSON for manifests/integrity summaries.

Raw provider files remain uncommitted.

## A6 — DXY storage/join

`synthetic_dxy_m1` remains a separate canonical table.

The annual decision index stores:
- `dxy_available`
- `dxy_age_minutes`

but does not duplicate all DXY values.

Later Stage 3 joins DXY by the same frozen backward-availability rule.

## A7 — Macro source coverage

A macro family is not silently synthesized when its historical first-party schedule cannot be reproduced.

The normalized macro schedule must contain coverage metadata by:
- year;
- event family;
- source agency;
- acquisition/parser status.

Decision rows use:
- `macro_schedule_available = true` only when the normalized calendar source coverage for that decision year has passed the Stage 2 macro-integrity checks.

Missing family/year coverage remains explicit in the Stage 2 report.

## A8 — No change to governance

- 2016-2021 only.
- 2022-2025 remain sealed.
- no profitability model;
- no future outcome labels;
- no source substitution based on predictive/economic results.
