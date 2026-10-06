# Information Parity V1 — Stage 3 Teacher Time-Domain Feasibility

Status: **BLOCKED BEFORE ANY 2026 MARKET ACCESS OR STAGE 3 FITTING**

Parent:
- `research/INFORMATION_PARITY_V1_ROADMAP.md`
- D-087 accepted Information Parity V1 Stage 2

Badar source repository:
`alisufyan-ai7/unpack-human-trading-strategies-claude`

Pinned source-layer identity for this audit:
- Badar repository commit: `2df3d588c4b6d82761df2ee0c6f6639e82ce3414`
- source-layer teacher table: `dataset/live_trades.csv`
- teacher-table blob: `ea620cb44937f276be2e65ae7da25ae9503be655`

Provenance boundary:
- everything outside `derived/` is source-layer evidence of what Badar said/showed, subject to transcript/observation uncertainty;
- everything inside `derived/` is Claude interpretation and was not used for this audit.

## Purpose

Stage 3 is intended to test whether Information Parity V1 can recognize Badar-like decision moments by reconstructing causal market state immediately before sufficiently timestamp-resolvable Badar entries and comparing those entries with matched non-trade timestamps.

Before implementing that benchmark, the teacher labels and the accepted Information Parity market epoch must overlap in time.

They currently do not.

## Accepted market epoch

D-087 froze Information Parity V1 Stage 2 on:

`2016-01-01 <= TRAIN < 2022-01-01`

The project chronology remains:
- 2016-2021: TRAIN
- 2022: sealed validation
- 2023-2024: sealed development test
- 2025: sealed final OOS
- 2026: reserved for later forward/shadow comparison

Therefore 2026 must not be silently consumed for model development.

## Pinned Badar live-trade epoch

The pinned source-layer `dataset/live_trades.csv` contains:
- rows: **119**
- streams: **43**
- first date: **2026-07-06**
- last date: **2026-10-02**
- observed years: **2026 only**
- XAUUSD-like rows: **118**
- non-XAUUSD rows: **1**
- direction labels: 52 long / 67 short

There are **zero** teacher rows in 2016-2021.

Therefore no row from the admitted Badar live-trade table can currently be joined to the accepted Stage 2 TRAIN market layer.

## Timestamp/evidence quality audit

All 119 rows contain:
- a stream identifier;
- a date;
- a direction;
- a source-layer stream time;
- a source-layer chart time.

However:
- 110 / 119 chart-time strings contain approximate notation;
- 43 / 119 stream-time strings contain approximate notation;
- entry price is missing on 5 rows.

The source-layer table's `confidence` column is an **evidence/readability confidence rating**, not Badar's trading-confidence label:
- high: 16
- medium: 65
- low: 38

It must not be renamed or treated as teacher confidence.

The source-layer `setup_id` field is a researcher-added organizational index according to the Badar repository provenance. It is not a Badar-authored class label and must not be used as a supervised target or attributed to him.

Observed outcome/result fields are also unnecessary for the Stage 3 recognition benchmark and must not enter model inputs.

## Scientific consequence

The Stage 3 benchmark as currently written cannot be executed honestly on the accepted 2016-2021 Information Parity layer.

Using the 2026 teacher rows would require acquiring/reconstructing 2026 market state and using 2026 as a development/supervision epoch. That would consume a period currently reserved for later forward/shadow comparison.

That is a material chronology/governance change, not an implementation detail.

## Prohibited shortcuts

Do not:
- apply Claude-derived Badar rules to 2016-2021 and call the resulting rows Badar labels;
- treat `derived/dataset/live_trades_labelled.csv` or other `derived/` outputs as Badar supervision;
- use source-layer `setup_id` as if it were a Badar-authored setup class;
- use evidence `confidence` as if it were Badar's trade confidence;
- access 2022-2025 XAUUSD;
- acquire 2026 XAUUSD for fitting without a separately frozen chronology decision;
- open 2026 merely because Stage 2 completed.

## Safe work that remains allowed

Without touching 2026 market data, Stage 3 preparation may:
1. pin the Badar source commit and teacher-table blob;
2. define deterministic teacher-row timestamp-resolution rules;
3. define exclusions for non-XAUUSD / student / paper / ambiguous rows using source evidence only, with every exclusion traceable to the source layer;
4. define stream/day grouping for leakage protection;
5. define matched-non-trade construction conceptually;
6. define the fixed baseline/full-information comparison and metrics.

But no empirical Stage 3 fitting can start until the time-domain policy is resolved.

## Required next governance decision

Exactly one of the following must be separately frozen before Stage 3 market reconstruction:

### Option A — preserve 2026 reserve

Keep 2026 untouched.

Then the current live-trade teacher dataset cannot be used for supervised Stage 3 fitting. A different timestamp-resolvable expert teacher source overlapping 2016-2021 would be required, or the finite roadmap must be revised so Stage 3 is not a supervised Badar-entry benchmark.

No such replacement source is currently admitted.

### Option B — repurpose a bounded 2026 teacher window

Explicitly authorize a narrowly bounded 2026 teacher-supervision window, separate it from any later economic forward/shadow evaluation, and preregister:
- exact dates/streams;
- exact market sources;
- no economic/P&L target use;
- grouped holdout protocol;
- what remains reserved after teacher fitting.

This would consume part of the currently reserved 2026 period and therefore requires an explicit chronology change before any acquisition.

## Current decision

Until a separate chronology decision exists:

**Stage 3 empirical fitting is blocked.**

The blocker is temporal supervision mismatch, not failure of the accepted Stage 2 information layer.

No 2022-2026 XAUUSD market data should be newly accessed for Stage 3 under the present authorization.
