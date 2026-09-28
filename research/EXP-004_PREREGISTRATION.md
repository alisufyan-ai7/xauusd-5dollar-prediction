# EXP-004 — Shift-Aware Calibrated Economic Value V1

Status: FROZEN BEFORE EMPIRICAL RESULTS

## Purpose

Test whether EXP-003's economic-value failure can be repaired by:

1. calibrating SUCCESS / FAILURE / UNRESOLVED probabilities using strictly out-of-time TRAIN predictions; and
2. abstaining when the current market state is materially outside the frozen TRAIN feature support.

EXP-004 is a new experiment descended from EXP-003.

FINAL_OOS 2025 remains sealed.

## Motivation

EXP-003 diagnosis established:

- positive-EV tails systematically overpredicted SUCCESS;
- positive-EV tails systematically underpredicted FAILURE;
- the error worsened as predicted EV increased;
- unresolved-expiry-P&L regression was not the dominant source of EV optimism;
- 2024 showed large volatility / attainability / spread distribution shifts;
- many positive-EV rows were outside TRAIN 1%-99% feature support;
- sequential opportunity filtering did not remove the calibration gap.

EXP-004 therefore changes only probability calibration and support-aware abstention.

It does NOT add trading indicators, search model hyperparameters, or alter executable label semantics.

## Data and partitions

Primary source remains synchronized Dukascopy XAUUSD M1 BID+ASK.

Research scope:
- 2016-2024 only.

Chronological partitions:
- TRAIN: 2016-2021
- VALIDATION: 2022
- DEVELOPMENT_TEST: 2023-2024
- FINAL_OOS: 2025 — SEALED
- 2026: later forward/shadow only

No 2025 data may be requested, downloaded, labeled, featurized, scored, summarized, or inspected.

## Executable path semantics

Reuse EXP-002 / EXP-003 semantics unchanged:

BUY:
- entry next M1 ASK open;
- SUCCESS at BID +5 before BID -3;
- FAILURE at BID -3 first.

SELL:
- entry next M1 BID open;
- SUCCESS at ASK -5 before ASK +3;
- FAILURE at ASK +3 first.

Horizon:
- exact 60 calendar minutes with synchronized BID/ASK coverage.

UNRESOLVED:
- actual executable 60-minute expiry P&L.

AMBIGUOUS:
- excluded from model fitting;
- treated as -3 in economic evaluation.

## Frozen feature vector

Reuse the exact EXP-003 feature vector.

No feature additions, deletions, transformations, or selection are permitted in EXP-004 V1.

## Base predictive models

Reuse EXP-003 V1 base architecture unchanged for BUY and SELL separately.

### Three-class outcome model

Classes:
- SUCCESS
- FAILURE
- UNRESOLVED

Model:
- HistGradientBoostingClassifier
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

### UNRESOLVED expiry-P&L model

Reuse EXP-003 V1 unchanged:

- HistGradientBoostingRegressor
- loss = squared_error
- learning_rate = 0.05
- max_iter = 200
- max_leaf_nodes = 15
- max_depth = None
- min_samples_leaf = 200
- l2_regularization = 1.0
- max_bins = 255
- early_stopping = false
- random_state = 1

Fit only realized UNRESOLVED TRAIN rows.

Predictions clipped to [-3,+5].

## Chronological calibration dataset

Calibration MUST be built from predictions that are out of time relative to each predicted year.

Frozen expanding-window folds:

- fit base classifier on 2016 -> predict 2017;
- fit on 2016-2017 -> predict 2018;
- fit on 2016-2018 -> predict 2019;
- fit on 2016-2019 -> predict 2020;
- fit on 2016-2020 -> predict 2021.

Rules:
- each fold uses only rows earlier than the prediction year;
- the same frozen feature vector and base hyperparameters are used;
- the same every-5th eligible chronological thinning is applied inside each fold's fitting sample;
- AMBIGUOUS rows are excluded;
- calibration targets are the realized three-class outcomes of 2017-2021;
- no 2022+ row participates in calibrator fitting.

## Probability calibrator

For BUY and SELL independently:

Inputs:
- log of clipped base probabilities:
  - log(P_success)
  - log(P_failure)
  - log(P_unresolved)

Clip base probabilities to [1e-6, 1-1e-6] before log transform.

Calibrator:
- multinomial LogisticRegression
- penalty = L2
- C = 1.0
- solver = lbfgs
- max_iter = 1000
- class_weight = None
- random_state = 1

Purpose:
allow class-specific correction of systematic probability bias while remaining low complexity.

No calibration hyperparameter search.

After calibration fitting:
- refit the frozen base classifier on full TRAIN 2016-2021;
- score 2022 and 2023-2024;
- apply the frozen calibrator to those base probabilities.

## UNRESOLVED regression

The unresolved-P&L regressor is not recalibrated in EXP-004 V1.

Reason:
EXP-003 diagnosis showed class-probability error dominated the EV optimism gap.

The full TRAIN 2016-2021 unresolved regressor is reused unchanged.

## Calibrated economic value

For each direction:

EV_CAL_GROSS =
  5 * P_cal(SUCCESS)
  - 3 * P_cal(FAILURE)
  + P_cal(UNRESOLVED) * predicted_unresolved_expiry_PnL

Primary score:

EV_CAL_F10 = EV_CAL_GROSS - 0.10

## Frozen support reference

Build TRAIN support reference from the same deterministic every-5th eligible TRAIN rows used for EXP-003 model fitting.

For each frozen feature store:
- TRAIN 1st percentile;
- TRAIN 25th percentile;
- TRAIN 75th percentile;
- TRAIN 99th percentile.

For each scored row:

outside_count =
number of features below TRAIN p01 or above TRAIN p99.

For each feature, normalized exceedance is:

- if below p01: (p01 - x) / TRAIN_IQR
- if above p99: (x - p99) / TRAIN_IQR
- otherwise 0

If TRAIN_IQR is zero, any value outside [p01,p99] contributes exceedance 1.0.

total_exceedance =
sum of normalized exceedances across features.

## Frozen support gate

A row is SUPPORT_ELIGIBLE only if BOTH:

- outside_count <= 2
- total_exceedance <= 1.0

Otherwise the system must abstain regardless of EV.

This rule is frozen before EXP-004 empirical results.

No alternative support cutoff may be introduced after results.

## Experimental arms

EXP-004 preregisters three comparison arms.

### ARM A — RAW_EV benchmark

Use the original EXP-003 uncalibrated EV_F10.

No support gate.

Purpose:
reproduce prior behavior as a benchmark only.

ARM A is not eligible for advancement because EXP-003 already failed.

### ARM B — CAL_EV

Use EV_CAL_F10.

No support gate.

Purpose:
isolate the effect of chronological probability calibration.

### ARM C — CAL_EV_SUPPORT

Use EV_CAL_F10 only when SUPPORT_ELIGIBLE.

Purpose:
measure whether explicit out-of-support abstention adds robustness beyond calibration.

Only ARMS B and C are eligible for EXP-004 advancement.

## Frozen EV thresholds

Reuse the already-frozen EXP-003 thresholds unchanged:

- T0: EV > 0.00
- T25: EV >= 0.25
- T50: EV >= 0.50
- T75: EV >= 0.75

No additional thresholds may be introduced.

## Direction conflict rule

Reuse EXP-003 unchanged:

- neither direction qualifies => NO TRADE;
- exactly one qualifies => eligible direction;
- both qualify:
  - choose larger EV only if absolute EV difference >= 0.25;
  - otherwise NO TRADE.

For ARM C, a direction can qualify only if its row is SUPPORT_ELIGIBLE.

## Opportunity-level execution

Reuse EXP-003 unchanged:

- one global position at a time;
- no pyramiding;
- no averaging;
- no reversal while open;
- later signals suppressed until exit.

## Economic realization

SUCCESS:
- +5.00

FAILURE:
- -3.00

UNRESOLVED:
- actual executable expiry P&L

AMBIGUOUS:
- -3.00 conservatively

Stress:
- F0 = gross
- F05 = gross -0.05
- F10 = gross -0.10
- F20 = gross -0.20

Primary advancement metric uses F10.

## Required calibration diagnostics

For RAW_EV and CAL_EV, BUY and SELL separately, report on:

- VALIDATION 2022;
- DEVELOPMENT_TEST 2023;
- DEVELOPMENT_TEST 2024.

Required:
- multiclass log loss;
- per-class Brier;
- predicted vs realized SUCCESS / FAILURE / UNRESOLVED frequencies;
- class calibration by fixed 0.10 probability bins;
- mean predicted EV_F10;
- realized mean NET_F10;
- EV calibration gap.

For ARM C additionally report:
- support-eligible share;
- support-rejected share;
- outside_count distribution;
- total_exceedance distribution.

## Required sequential economics

For ARM A/B/C × T0/T25/T50/T75 × BUY_ONLY/SELL_ONLY/COMBINED report:

- raw qualifying observations;
- executed trades;
- suppression ratio;
- SUCCESS / FAILURE / UNRESOLVED / AMBIGUOUS;
- F0/F05/F10/F20;
- 2023;
- 2024;
- each 2023-2024 quarter;
- profit factor;
- cumulative net P&L;
- max drawdown;
- active trading days;
- trades per active/calendar day;
- holding-time p25 / median / p75 / p90.

## Dependence-aware uncertainty

For every ARM B/C policy:

- group DEVELOPMENT_TEST trades by UTC entry date;
- bootstrap whole dates with replacement;
- 2,000 replicates;
- seed = 4;
- report 95% percentile CI for mean NET_F10.

## Advancement rule

An ARM B or ARM C threshold/mode may advance to a separate immutable pre-OOS candidate-freeze milestone only if ALL hold:

1. mean NET_F10 > 0 in 2023;
2. mean NET_F10 > 0 in 2024;
3. overall F10 profit factor > 1;
4. UTC-day bootstrap 95% lower bound > 0;
5. at least 250 DEVELOPMENT_TEST executed trades overall;
6. at least 75 executed trades in each of 2023 and 2024;
7. no single calendar quarter contributes >40% of total positive F10 P&L;
8. AMBIGUOUS is treated as -3;
9. 2025 remains untouched.

Passing does not automatically open 2025.

If more than one ARM B/C policy passes, all passers are retained; no post-hoc winner is chosen in EXP-004.

## Interpretation rules

The experiment is designed to distinguish:

- ARM B improves over A, ARM C adds little:
  probability calibration was the main fix.

- ARM B remains weak but ARM C improves materially:
  support-aware abstention was essential.

- neither B nor C passes:
  calibration/support gating is insufficient and a future experiment may need a different representation/objective.

No post-hoc regime filter may be introduced.

## Governance

EXP-004 V1 must not:

- access 2025;
- tune calibration hyperparameters;
- tune support thresholds;
- add/remove features;
- tune EV thresholds;
- add a regime filter after seeing results;
- promote BUY-only or SELL-only outside the frozen comparison;
- proceed to Exness demo/live.

Negative results are admissible.

## Exit states

A. NO ARM B/C POLICY PASSES
- 2025 stays sealed;
- diagnose;
- redesign only through a new preregistered experiment.

B. ONE OR MORE ARM B/C POLICIES PASS
- 2025 stays sealed;
- freeze all passers in a separate pre-OOS milestone;
- conduct implementation/leakage audit before any FINAL_OOS opening.

2025 remains sealed in all cases.
