# Information Parity V1 — Stage 2 Schema and Timestamp-Alignment Preregistration

Status: **FROZEN BEFORE FULL TRAIN ACQUISITION / INTEGRATION**

Decision context:
- D-064: pause new strategy/model experiments until information parity is built.
- D-065: freeze the five-stage Information Parity V1 roadmap.
- D-067: Stage 1 complete; Stage 2 source set frozen.

Parent roadmap:
`research/INFORMATION_PARITY_V1_ROADMAP.md`

Stage 1 findings:
`research/INFORMATION_PARITY_V1_STAGE1_SOURCE_FEASIBILITY_FINDINGS.md`

## 1. Purpose

Stage 2 builds the causal **Information Parity Layer V1** for 2016-2021 TRAIN.

It does not:
- train a predictive model;
- calculate trading P&L;
- select BUY/SELL policies;
- tune thresholds against future XAUUSD outcomes;
- access 2022-2025 XAUUSD evaluation periods.

The goal is to produce one reproducible, timestamp-safe information environment from which later Stage 3 expert-decision recognition can be built.

## 2. Frozen Stage 2 source set

Admitted inputs:

1. XAUUSD synchronized Dukascopy M1 BID/ASK OHLC.
2. Contemporaneous BID/ASK spread.
3. Dukascopy XAUUSD M1 provider volume.
4. Causal XAUUSD multi-timeframe bars and deterministic structural/session context.
5. `SYNTHETIC_DXY_DUKASCOPY_BID`.
6. Composite first-party scheduled U.S. macro-event calendar.
7. Optional targeted Dukascopy XAUUSD tick microstructure, only when a concrete Stage 2 field requires it.
8. A separate trade/account/risk-state interface.

Explicitly excluded from V1:

- intraday US 10Y/rate channel;
- macro actual/forecast/consensus/surprise;
- global order flow;
- official ICE DXY prints as a complete 2016-2021 source;
- full six-year tick ingestion by default;
- new external information channels not admitted by D-067.

## 3. Canonical decision-time semantics

### 3.1 Base M1 timestamp

Dukascopy M1 `timestamp` is treated as the UTC **bar-start** timestamp.

For an M1 bar beginning at `t`:

- bar interval = `[t, t + 60 seconds)`;
- the bar close is considered available at:
  `decision_time_ms = t + 60,000`.

A decision row indexed by bar-start `t` may use only information whose **availability time** is <= `decision_time_ms`.

This preserves the semantics already used by the project:
- `scripts/build_features.py`
- EXP-002 executable-entry preregistration.

### 3.2 No partial-bar leakage

A higher-timeframe candle may be used only after that candle is complete.

Example:

For an H1 candle covering 13:00:00-13:59:59 UTC:
- label/availability time = 14:00:00 UTC;
- it is not visible to a decision at 13:59:00;
- it is visible at 14:00:00.

The same rule applies to all derived timeframes.

### 3.3 No forward labels in Stage 2

Stage 2 outputs contain no future MFE/MAE, target-before-stop, P&L, or future-return fields.

Any later labels belong to a separately frozen later stage.

## 4. XAUUSD base synchronization contract

Reuse the established EXP-002 synchronization rule in
`scripts/synchronize_exp002_m1.py`.

For each year:

- acquire XAUUSD BID M1 and ASK M1 separately;
- take the union of observed timestamps;
- if exactly one side is missing, allow a zero-volume flat reconstruction at that side's immediately prior observed close only when executable-side OHLC consistency remains valid;
- never create timestamps absent on both sides;
- drop leading unpaired rows with no prior quote;
- drop stale reconstructions that would invert executable-side BID/ASK OHLC;
- assert timestamp equality after synchronization.

Required base columns:

- `timestamp_ms`
- `decision_time_ms`
- `bid_open`
- `bid_high`
- `bid_low`
- `bid_close`
- `bid_volume`
- `ask_open`
- `ask_high`
- `ask_low`
- `ask_close`
- `ask_volume`
- `spread_open`
- `spread_close`
- `bid_flat_fill`
- `ask_flat_fill`

Where:
- `spread_open = ask_open - bid_open`
- `spread_close = ask_close - bid_close`.

Negative spreads are invalid.

## 5. Canonical XAUUSD timeframe tables

Stage 2 must build completed causal bars for:

- M3
- M5
- M15
- M30
- H1
- H4
- D1
- W1

Monthly context is deferred from V1 unless it can be produced without introducing a new acquisition/warm-up requirement.

### 5.1 Intraday aggregation

M3 through H4:

- source = synchronized XAUUSD M1 BID market-state bars;
- aggregation origin = Unix epoch;
- bins closed on the left;
- output label = bar-end/availability time;
- OHLC = first/max/min/last;
- volume = sum of provider volume;
- `source_m1_count` retained.

A completed intraday bar is canonical only when:
- it contains the exact expected M1 count;
- constituent timestamps are exactly one minute apart.

Expected counts:
- M3 = 3
- M5 = 5
- M15 = 15
- M30 = 30
- H1 = 60
- H4 = 240

Incomplete bins remain auditable in coverage summaries but must not be supplied as completed bars to later models.

### 5.2 D1

Canonical D1:
- UTC calendar day;
- constructed from completed H1 bars;
- output label = next UTC midnight;
- require at least 20 completed H1 bars;
- retain `completed_h1_count`.

This reuses the conservative convention already implemented in Root-Reset V4 rather than introducing a new hindsight-dependent day definition.

### 5.3 W1

Canonical W1:
- Monday 00:00 UTC through next Monday 00:00 UTC;
- constructed only from completed D1 bars;
- output label = next Monday 00:00 UTC;
- retain `completed_d1_count`;
- require at least 4 completed D1 bars.

No weekly bar is available before its end label.

## 6. Structural/location state

Stage 2 should expose information, not enforce a trade setup.

Allowed deterministic structural descriptors:

### 6.1 Confirmed swings

For M5, M15, H1 and H4:

- pivot candidate uses two bars left and two bars right;
- a swing at bar `i` becomes known only when bar `i+2` closes;
- retain the most recent confirmed swing high and swing low;
- retain their creation and confirmation timestamps;
- distances are computed from current BID close.

This follows the causal swing-confirmation logic already used in Root-Reset V4.

### 6.2 FVG / imbalance state

For M5, M15, H1 and H4:

Bullish FVG:
- high of bar k-2 < low of bar k.

Bearish FVG:
- low of bar k-2 > high of bar k.

Creation time:
- close/availability time of bar k.

Invalidation:
- bullish FVG invalidated by a completed close below its lower boundary;
- bearish FVG invalidated by a completed close above its upper boundary.

Expose:
- nearest active bullish FVG bounds/distance;
- nearest active bearish FVG bounds/distance;
- creation age;
- timeframe.

No model is forced to trade an FVG.

### 6.3 Previous-day state

At each decision row, expose only the most recently completed canonical D1:
- high;
- low;
- open;
- close;
- distance from current BID close.

### 6.4 Session/liquidity state

Use timezone-aware session boundaries:

- Asia start = 00:00 UTC;
- London open = 08:00 `Europe/London`;
- New York open reference = 08:00 `America/New_York`.

For each decision time retain:
- current session label;
- minutes since current session boundary;
- Asia high/low **so far** if Asia is active;
- completed Asia high/low after London opens;
- London high/low **so far** before New York;
- completed pre-NY London high/low after NY open;
- distance to each known session high/low.

DST conversion must use IANA timezone rules, never fixed UTC offsets for London/New York.

### 6.5 Excluded structural heuristics

Stage 2 will not create new deterministic:
- order-block definitions;
- breaker-block definitions;
- equal-high/low tolerances;
- trendline rules;
- arbitrary test-count thresholds.

Raw multi-timeframe bars remain available so a later fixed model may learn such geometry without Stage 2 embedding subjective rules.

## 7. XAUUSD provider-volume channel

Preserve raw:
- `bid_volume`
- `ask_volume`.

Allowed deterministic causal transforms:

- `volume_sum_proxy = bid_volume + ask_volume`
- rolling mean over 5, 15, 60, 240 completed M1 observations;
- current / rolling-60 ratio;
- rolling 240-observation percentile;
- current-session cumulative provider volume;
- current-session volume relative to the same elapsed-minute position on prior observed TRAIN sessions, only if implemented without future rows.

The last item is optional for Stage 2 implementation; if omitted, record it as omitted rather than changing the contract later.

Terminology restriction:

Do not call these fields:
- centralized gold volume;
- exchange volume;
- buy/sell order flow;
- institutional volume.

They are Dukascopy provider participation proxies.

## 8. Spread channel

Preserve raw:
- open spread;
- close spread.

Allowed deterministic causal transforms:
- mean spread 5/15/60;
- max spread 15/60;
- current / mean-60 ratio;
- rolling 240-observation percentile.

These reuse EXP-002 semantics.

## 9. Synthetic DXY contract

Series name:
`SYNTHETIC_DXY_DUKASCOPY_BID`

Constituent M1 BID closes:
- EURUSD
- USDJPY
- GBPUSD
- USDCAD
- USDSEK
- USDCHF

Formula:

`50.14348112 × EURUSD^-0.576 × USDJPY^0.136 × GBPUSD^-0.119 × USDCAD^0.091 × USDSEK^0.042 × USDCHF^0.036`

### 9.1 DXY bar availability

For each constituent M1 bar starting at `t`:
- its close is available at `t + 60s`.

A synthetic DXY observation at minute `t` is formed only when all six constituent closes for that exact bar-start timestamp are present.

Its:
- `dxy_bar_start_ms = t`
- `dxy_available_time_ms = t + 60,000`.

### 9.2 Alignment to XAUUSD decision rows

For each XAUUSD `decision_time_ms`:

- use the most recent synthetic DXY observation whose `dxy_available_time_ms <= decision_time_ms`;
- maximum permitted staleness = **5 calendar minutes**;
- record `dxy_age_minutes`;
- if older than 5 minutes, DXY fields are missing;
- never forward-fill across a market closure/weekend.

Preserve:
- DXY level;
- 1m change;
- 5m change;
- 15m change;
- 60m change;
- 240m change;
- rolling realized-volatility proxies over 15/60/240 M1 observations;
- age/missing flag.

All changes use only previously available DXY observations.

## 10. Scheduled macro-event calendar contract

Stage 2 may include **schedule information only**.

Allowed families:

- CPI
- NFP / Employment Situation
- FOMC rate decision / statement
- Initial Jobless Claims
- GDP
- ISM Manufacturing
- ISM Services
- JOLTS

Each normalized event record must contain:

- `event_id`
- `event_family`
- `scheduled_time_utc`
- `scheduled_time_local`
- `source_timezone`
- `source_agency`
- `source_document_id_or_url`
- `release_stage` where relevant, e.g. GDP advance/second/third
- `historical_exception_flag`
- `normalization_version`.

No actual, forecast, consensus, previous, revision or surprise field is allowed in V1.

### 10.1 Event-state alignment

At each XAUUSD decision time derive:

- previous scheduled event family;
- minutes since previous scheduled event;
- next scheduled event family;
- minutes to next scheduled event;
- count of admitted events in the prior 120 minutes;
- count of admitted events in the next 120 minutes;
- boolean windows:
  - 0-15m before;
  - 15-60m before;
  - 0-15m after;
  - 15-60m after;
  - 60-120m after.

A future event timestamp may be used because the public schedule is the information being represented; no future event **outcome** may be used.

If two admitted events share the same timestamp:
- preserve both in the raw event table;
- decision-row categorical fields use a deterministic sorted multi-label representation rather than silently choosing one.

## 11. Tick-microstructure boundary

Stage 2 does not download full 2016-2021 ticks by default.

Permitted tick-derived fields require a separately enumerated targeted window and must be limited to source-integrity or specifically required decision-state context.

For the initial Stage 2 build:
- M1 is sufficient;
- tick fields remain an optional extension;
- no model may depend on a tick field unless Stage 3 preregistration explicitly names it.

This prevents a six-year high-volume data acquisition from becoming an unbounded side project.

## 12. Market-state versus trade/risk-state separation

Stage 2 produces two logical interfaces.

### 12.1 Market state

Contains only observable market/exogenous context:
- XAUUSD;
- spread;
- provider volume;
- structural/session state;
- synthetic DXY;
- macro schedule.

### 12.2 Trade/risk state

Schema is defined but not populated with hindsight-derived policy history during Stage 2.

Fields:

- `position_state`: FLAT / LONG / SHORT
- `open_position_count`
- `entry_price`
- `stop_price`
- `target_price`
- `minutes_in_position`
- `session_realized_pnl`
- `session_trade_count`
- `consecutive_loss_count`
- `risk_fraction_deployed`
- `same_thesis_attempt_count`

For market-only Stage 2 artifacts:
- populate neutral FLAT/zero/null defaults;
- later Stage 5 simulation is responsible for causal state transitions.

Badar teacher records may populate observed trade-state metadata only in Stage 3's separately frozen expert dataset.

## 13. Logical output tables

Stage 2 must produce, at minimum:

1. `xauusd_m1_market_state`
2. `xauusd_m3`
3. `xauusd_m5`
4. `xauusd_m15`
5. `xauusd_m30`
6. `xauusd_h1`
7. `xauusd_h4`
8. `xauusd_d1`
9. `xauusd_w1`
10. `xauusd_structural_state`
11. `synthetic_dxy_m1`
12. `macro_event_schedule`
13. `decision_index`
14. `trade_risk_state_template`
15. `information_parity_manifest`

Physical storage may be CSV/CSV.GZ during implementation, but the logical column contract must not change based on model results.

## 14. Decision index contract

One row per synchronized XAUUSD M1 decision bar.

Required keys:

- `timestamp_ms`
- `decision_time_ms`
- `year`
- `utc_date`
- `ny_date`
- `feature_ready_market`
- `dxy_available`
- `macro_schedule_available`
- `market_state_version`

The decision index must not drop rows because a future trade would succeed or fail.

Readiness is based only on historical coverage needed for the requested context.

## 15. Warm-up policy

No pre-2016 market acquisition is authorized by this Stage 2 specification.

Therefore early-2016 rows may lack:
- long rolling windows;
- completed W1 context;
- prior-day context.

Such rows remain in the audit tables with readiness/missing flags.

They are not backfilled with pre-TRAIN data.

## 16. Missingness policy

### XAUUSD

- follow the synchronized BID/ASK rule;
- never fill timestamps absent on both sides.

### Higher timeframes

- incomplete constituent coverage => no canonical completed bar.

### DXY

- exact six-constituent synthetic observation preferred;
- backward as-of join only;
- <=5m staleness;
- otherwise missing.

### Macro

- missing archive evidence => event absent from normalized schedule, plus source-coverage warning;
- do not infer a release from current generic calendar rules when a historical archived date is unresolved.

### Volume

- reconstructed single-side XAUUSD flat candle receives zero volume on reconstructed side exactly as synchronization logic specifies;
- preserve a reconstruction flag.

No model-facing numeric sentinel such as -999 is permitted. Missingness must be explicit/null plus flags where needed.

## 17. Integrity and leakage tests

Before Stage 2 may be declared complete, implementation must prove:

1. `decision_time_ms = timestamp_ms + 60000`.
2. No XAUUSD market field uses a source bar closing after decision time.
3. No higher-TF state uses an incomplete bar.
4. Confirmed swings appear only after their confirmation bar closes.
5. FVGs appear only after their creation bar closes.
6. DXY `available_time <= decision_time`.
7. DXY staleness never exceeds 5 minutes when marked available.
8. No macro outcome fields exist.
9. Macro schedule joins never convert local time using fixed ET offsets.
10. No 2022-2025 XAUUSD rows or hashes exist.
11. Raw/normalized source hashes and row counts are recorded.
12. Re-running the same acquisition/build snapshot produces the same normalized hashes, or provider drift is explicitly reported.

## 18. Reproducibility manifest

The Stage 2 manifest must record:

- schema version;
- code commit SHA;
- downloader versions;
- per-source instrument/series;
- per-year requested ranges;
- raw SHA-256;
- normalized SHA-256;
- row counts;
- first/last timestamps;
- synchronization fills/drops;
- DXY constituent coverage;
- macro event counts by family/year;
- missingness summaries;
- structural-table row counts;
- timezone library/runtime version where practical;
- sealed-period assertion.

Raw provider files remain uncommitted.

## 19. Same-snapshot guard

Provider drift has already occurred in this project.

The accepted Stage 2 integrity run must:

1. acquire all permitted 2016-2021 sources in one workflow snapshot;
2. build normalized tables from those exact files;
3. hash raw and normalized inputs/outputs;
4. run leakage/integrity checks against that same snapshot;
5. upload only compact manifests/reports and, if size permits, normalized compact diagnostics;
6. never commit raw provider data.

Do not compare counts from separately reacquired snapshots as if differences necessarily came from code.

## 20. Stage 2 completion criteria

Stage 2 is complete only when:

- 2016-2021 Information Parity Layer V1 builds successfully;
- all integrity/leakage tests pass;
- C1 synthetic DXY coverage is quantified by year;
- C3 macro schedule counts are quantified by family/year;
- C5 volume missingness is quantified by year;
- canonical timeframe coverage is quantified;
- decision-index readiness is quantified;
- no future outcome/P&L field exists;
- 2022-2025 remain untouched;
- the accepted run/artifact digest is recorded in findings, decision log and continuity.

## 21. Stage 2 stop conditions

Stop and diagnose instead of silently changing the schema if:

- a source admitted in Stage 1 materially fails full TRAIN coverage;
- timezone/event normalization cannot be made reproducible;
- DXY constituent alignment produces unexpected large holes;
- provider drift breaks reproducibility;
- the layer requires a new external source not admitted in D-067.

Any material source substitution requires a new preregistered decision before implementation continues.

## 22. Stage transition

Passing Stage 2 does **not** authorize economic modeling.

After Stage 2 completion:

1. freeze the accepted information-layer artifact identity;
2. preregister Stage 3 Badar decision-recognition dataset construction;
3. construct matched non-trade examples;
4. define one fixed recognition architecture and grouped evaluation;
5. only then evaluate expert-state recognizability.

2022-2025 remain sealed throughout Stage 2.
