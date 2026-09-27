# EXP-002 Economic Failure Diagnosis V1

Status: FROZEN BEFORE DIAGNOSTIC RESULTS

## Purpose

Explain why EXP-002 preserves strong predictive ranking discrimination but produces negative sequential trading expectancy.

This milestone is diagnostic only.

It must not:
- tune the existing model;
- introduce a new model;
- select a new score threshold;
- promote a direction post hoc;
- access FINAL_OOS 2025.

## Data scope

Use only:
- TRAIN 2016-2021 for reproducing the frozen models;
- VALIDATION 2022 for reproducing frozen score cutoffs;
- DEVELOPMENT_TEST 2023-2024 for diagnosis.

FINAL_OOS 2025 remains sealed.

## Frozen predictive objects

Reproduce exactly:
- EXP-002 GBT V1 BUY model;
- EXP-002 GBT V1 SELL model;
- frozen feature set;
- frozen model hyperparameters;
- frozen top 10%, 5%, 2.5%, 1% VALIDATION-derived cutoffs.

No score-band changes are permitted.

## Diagnostic questions

### D1 — Outcome decomposition

For each direction and score band, report on DEVELOPMENT_TEST:

- signal count before sequential-position filtering;
- SUCCESS count/share;
- FAILURE count/share;
- UNRESOLVED count/share;
- AMBIGUOUS count/share;
- mean executable gross P&L per raw signal using:
  - SUCCESS = +5;
  - FAILURE = -3;
  - AMBIGUOUS = -3;
  - UNRESOLVED = stored executable expiry P&L;
- mean UNRESOLVED expiry P&L;
- median UNRESOLVED expiry P&L;
- p10 / p25 / p75 / p90 UNRESOLVED expiry P&L.

Purpose:
determine whether the main loss source is barrier failure, unresolved expiry behavior, or both.

### D2 — Score deciles inside the selected tail

For each direction:

- take all DEVELOPMENT_TEST scored rows;
- report realized executable gross P&L and label composition by:
  - overall score decile;
  - within top-10% tail split into 10 equal score slices.

Purpose:
test whether higher classifier score is actually monotonic in economic value.

This is descriptive only and may not be used to choose a new threshold.

### D3 — Year and quarter stability

For each frozen score band and direction, report:
- 2023;
- 2024;
- each calendar quarter;
- mean gross P&L;
- outcome shares;
- signal count.

Purpose:
identify temporal concentration or regime drift.

### D4 — Session and volatility decomposition

Use already-frozen causal features:

Session:
- ASIA
- EUROPE
- US
- LATE

Volatility:
- rv60_percentile_240m binned as:
  - LOW: <= 0.33
  - MID: > 0.33 and <= 0.67
  - HIGH: > 0.67

For each direction and frozen score band, report:
- count;
- mean gross P&L;
- outcome composition.

Purpose:
test whether classifier ranking is concentrated in economically poor or unstable regimes.

No new session or volatility thresholds may be introduced after results.

### D5 — Spread decomposition

Use:
- spread_close_1m;
- spread_mean_60m;
- spread_percentile_240m.

For each direction and frozen score band, report gross P&L by preregistered spread-percentile bins:
- Q1: <= 0.25
- Q2: > 0.25 to <= 0.50
- Q3: > 0.50 to <= 0.75
- Q4: > 0.75

Purpose:
measure whether high-score signals disproportionately occur when executable spread conditions are unfavorable.

### D6 — Holding-time decomposition

For sequential trades produced by the frozen top-10/5/2.5/1% BUY_ONLY, SELL_ONLY and COMBINED engines:

- holding minutes;
- median holding time;
- p25 / p75 / p90 holding time;
- holding time by SUCCESS / FAILURE / UNRESOLVED / AMBIGUOUS;
- mean gross P&L by holding-time bin:
  - <=5m
  - >5m to <=15m
  - >15m to <=30m
  - >30m to <=60m.

Purpose:
determine whether losses are associated with early adverse exits or long unresolved stagnation.

### D7 — Signal clustering and overlap

For raw qualifying signals before position filtering:

- inter-signal minutes;
- share of signals within 1m / 5m / 15m / 30m of the prior same-direction qualifying signal;
- number of raw qualifying signals per UTC day;
- p50 / p75 / p90 / p95 signals per active day.

For sequential execution:
- raw qualifying count;
- executed trade count;
- suppression ratio = 1 - executed/raw.

Purpose:
measure whether classifier scores represent many highly correlated observations of the same market episode rather than independent opportunities.

### D8 — Economic break-even comparison

For each frozen score band and direction:

Compute the observed mean executable gross P&L.

Also report:
- realized success probability;
- realized failure probability;
- unresolved probability;
- mean unresolved expiry P&L.

Then show the empirical identity:

EV = 5*P(SUCCESS) - 3*P(FAILURE) - 3*P(AMBIGUOUS) + P(UNRESOLVED)*E[expiry P&L | UNRESOLVED]

Purpose:
make explicit which component prevents positive expectancy.

## No-go rules

This milestone MUST NOT:
- create a new threshold from diagnostic bins;
- rank new candidate policies;
- optimize sessions, volatility regimes, spread bins, holding times, or directions;
- train an expected-value model;
- open 2025.

## Exit criterion

At completion, write a causal diagnosis of the major observed economic failure mechanisms.

Only after this diagnostic is sealed may EXP-003 be designed.

2025 remains sealed.
