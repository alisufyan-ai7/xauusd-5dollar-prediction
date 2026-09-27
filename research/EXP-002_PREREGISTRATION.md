# EXP-002 — Executable-Side Directional Target V1

Status: FROZEN BEFORE EMPIRICAL RESULTS

## Research question

Does XAUUSD contain timestamp-safe market states in which an actually executable BUY or SELL can reach +$5 price-unit P&L before -$3 price-unit P&L within 60 minutes, after paying the contemporaneous BID/ASK spread at entry and exit?

EXP-002 is a new experiment. It does not repair, retune, or reinterpret EXP-001.

FINAL_OOS 2025 remains sealed.

## Data

Primary historical source:

- Dukascopy public XAUUSD M1 BID
- Dukascopy public XAUUSD M1 ASK
- pinned downloader: dukascopy-node@1.50.0
- UTC
- 2016-2024 for non-sealed development
- 2025 FINAL_OOS remains unopened

BID and ASK files must be structurally validated and synchronized by timestamp.

## BID/ASK M1 synchronization

Dukascopy may omit a flat M1 candle independently on BID or ASK.

Before labeling/features:

- take the union of timestamps observed on BID and ASK;
- when exactly one side has a bar at a timestamp, represent the missing side as a zero-volume flat candle at that side's immediately prior close;
- do not create timestamps absent on both sides;
- if no prior quote exists for the missing side, drop that leading unpaired timestamp;
- downstream exact-contiguity checks still reject true common gaps, weekends, and market closures.

This synchronization rule is frozen before EXP-002 empirical results.

Tick data is NOT required for every minute. It is reserved only for later adjudication of M1 bars where target and adverse barriers are both touched in the same minute and ordering is unknowable from OHLC.

## Partitions

Unchanged chronological partitions:

- TRAIN: 2016-2021
- VALIDATION: 2022
- DEVELOPMENT_TEST: 2023-2024
- FINAL_OOS: 2025
- 2026: forward/shadow only

No label horizon may cross a partition boundary.

## Decision and entry semantics

At M1 timestamp t:

1. all model features are computed from information available through the CLOSE of bar t;
2. the prediction decision occurs at t + 60 seconds;
3. the executable entry is the OPEN of the immediately following M1 bar at t + 60 seconds.

The following bar must exist on both BID and ASK sides at the exact expected timestamp.

BUY entry:
- entry price = ASK open of the next M1 bar.

SELL entry:
- entry price = BID open of the next M1 bar.

The entry bar itself is included in the forward barrier scan because the trade is entered at its open.

## 60-minute executable barrier labels

Horizon:
- exactly 60 calendar minutes beginning at the executable entry timestamp;
- scan the entry bar and the next 59 M1 bars;
- exact contiguous BID and ASK M1 coverage is required.

### BUY

Entry = ASK_open.

Target level:
- entry + 5.00.

Adverse level:
- entry - 3.00.

Executable target touch:
- BID high >= target.

Executable adverse touch:
- BID low <= adverse.

### SELL

Entry = BID_open.

Target level:
- entry - 5.00.

Adverse level:
- entry + 3.00.

Executable target touch:
- ASK low <= target.

Executable adverse touch:
- ASK high >= adverse.

## Outcome ordering

For each direction:

- target first => SUCCESS;
- adverse first => FAILURE;
- neither within 60 minutes => UNRESOLVED;
- both target and adverse touched inside the same M1 bar before ordering is otherwise established => AMBIGUOUS.

AMBIGUOUS is not guessed.

A later tick-adjudication milestone may resolve AMBIGUOUS rows using Dukascopy BID/ASK ticks for only the affected dates/minutes.

## Expiry P&L

If UNRESOLVED:

BUY executable expiry:
- exit at BID close of the 60th scanned M1 bar;
- gross P&L = exit BID - entry ASK.

SELL executable expiry:
- exit at ASK close of the 60th scanned M1 bar;
- gross P&L = entry BID - exit ASK.

This expiry P&L is stored even though the primary classification label remains SUCCESS / FAILURE / UNRESOLVED / AMBIGUOUS.

## Feature set

EXP-002 reuses the timestamp-safe EXP-001 V2 market-context features, calculated from BID history only, because they were already defined before the executable-target results.

EXP-002 additionally adds spread-aware features calculated only from synchronized BID/ASK information available by the decision-bar close:

- spread_close_1m = ASK close - BID close;
- spread_mean_5m;
- spread_mean_15m;
- spread_mean_60m;
- spread_max_15m;
- spread_max_60m;
- spread_ratio_1m_to_60m;
- spread_percentile_240m.

No future spread information may be used.

## Modeling sequence

No broad model search.

1. descriptive executable-label baselines;
2. fixed HistGradientBoostingClassifier using the EXP-001 GBT V1 hyperparameters;
3. separate BUY and SELL models;
4. TRAIN only for fitting;
5. VALIDATION and DEVELOPMENT_TEST reported separately;
6. no 2025 access.

Frozen GBT hyperparameters:

- loss = log_loss
- learning_rate = 0.05
- max_iter = 200
- max_leaf_nodes = 15
- max_depth = None
- min_samples_leaf = 200
- l2_regularization = 1.0
- max_bins = 255
- early_stopping = false
- random_state = 1

TRAIN thinning:
- every 5th eligible chronological TRAIN row.

## Evaluation

For BUY and SELL separately:

- base success rate;
- ROC-AUC;
- PR-AUC;
- Brier score;
- log loss;
- raw-score quantiles;
- realized success by score band.

Primary score-band reporting:

- top 10%;
- top 5%;
- top 2.5%;
- top 1%.

Cutoffs are derived on VALIDATION only and applied unchanged to DEVELOPMENT_TEST.

Operational score-band derivation must not condition on future outcome category.

## Economic screening

After the new executable-label model is evaluated, sequential trade economics are tested on DEVELOPMENT_TEST with:

- one position at a time;
- BUY-only, SELL-only, COMBINED;
- simultaneous BUY+SELL qualification => NO TRADE;
- actual executable label path;
- expiry P&L for unresolved trades;
- additional friction stress:
  - F0 = 0.00
  - F05 = 0.05
  - F10 = 0.10
  - F20 = 0.20 price units/trade.

No score band is promoted merely because it looks best after results.

## Advancement rule before FINAL_OOS

A mode/policy may be nominated for a separate immutable candidate-freeze milestone only if under F10:

1. mean net expectancy > 0 in both 2023 and 2024;
2. overall profit factor > 1;
3. UTC-day block-bootstrap 95% expectancy interval lower bound > 0;
4. trade count is non-trivial;
5. result is not dependent on unadjudicated ambiguous rows;
6. 2025 remains untouched.

Passing does not automatically open 2025.

## Governance

- EXP-001 results are historical evidence only and are not retuned.
- EXP-002 target semantics are frozen before label generation.
- Negative results are admissible.
- No 2025 data or outcome statistics may be accessed.
- No Exness trading or broker mutation is authorized by this experiment.
