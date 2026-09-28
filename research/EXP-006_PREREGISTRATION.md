# EXP-006 — Causal Path-State Representation V1

Status: FROZEN BEFORE EMPIRICAL RESULTS

## Purpose

Test whether the failure of EXP-005 is primarily a representation problem.

EXP-006 keeps the EXP-005 targets, models, economic thresholds, early-failure definition,
execution semantics, and advancement rules unchanged, and changes only the market-state
feature representation.

FINAL_OOS 2025 remains sealed.

## Motivation

EXP-005 established two facts:

1. <=5-minute adverse-barrier failure is predictably rankable with the existing 48-feature
   representation (DEV ROC-AUC approximately 0.81-0.84);
2. direct executable-P&L prediction using the same representation has almost no useful
   correlation with realized P&L, and low-risk opportunity sets become too sparse.

The next clean question is therefore:

Can richer causal price-path structure improve trade-quality discrimination while retaining
the useful downside-risk signal?

## Data and partitions

Use synchronized Dukascopy XAUUSD M1 BID+ASK.

Chronological partitions remain:
- TRAIN: 2016-2021
- VALIDATION: 2022
- DEVELOPMENT_TEST: 2023-2024
- FINAL_OOS: 2025 — SEALED
- 2026: reserved for later forward/shadow work

No EXP-006 workflow may access 2025.

## Executable semantics

Reuse EXP-005 unchanged.

BUY:
- entry next M1 ASK open;
- target +5 on BID before adverse -3 on BID.

SELL:
- entry next M1 BID open;
- target -5 on ASK before adverse +3 on ASK.

Horizon:
- exactly 60 calendar minutes with complete synchronized coverage.

Economic outcomes:
- SUCCESS = +5
- FAILURE = -3
- UNRESOLVED = actual executable 60-minute expiry P&L
- AMBIGUOUS = excluded from fitting and treated as -3 in evaluation

## Representation arms

### REP_A_BASE48

Exact EXP-005 48-feature representation.

Purpose:
benchmark only. REP_A is not eligible for advancement because EXP-005 already failed.

### REP_B_PATH84

Use the exact 48 BASE features plus 36 new causal path-state features defined below.

REP_B is eligible for advancement.

No feature selection or post-hoc removal is permitted.

## New path-state features

All new features use BID M1 observations at or before the current decision-bar close.

The new representation uses windows:

- 5m
- 15m
- 30m
- 60m
- 120m
- 240m

For each window W, define these six features.

### 1. path_efficiency_W

abs(close_t - close_{t-W}) /
sum_{k=t-W+1..t} abs(close_k - close_{k-1})

Range:
- 0 = highly reversing/choppy path
- 1 = perfectly one-directional path

If denominator is zero, use 0.

### 2. sign_change_rate_W

Among consecutive nonzero one-minute return signs inside the trailing W-minute window,
the fraction of adjacent sign pairs that change sign.

If fewer than two nonzero signs exist, use 0.

### 3. jump_concentration_W

max absolute 1-minute return inside the trailing W-minute window /
sum absolute 1-minute returns in that window.

If denominator is zero, use 0.

### 4. time_since_high_W

Minutes since the most recent occurrence of the trailing-W highest HIGH.

Range:
- 0 through W-1.

### 5. time_since_low_W

Minutes since the most recent occurrence of the trailing-W lowest LOW.

Range:
- 0 through W-1.

### 6. synthetic_body_range_ratio_W

Treat the trailing W M1 bars as one causal synthetic bar:

- open = OPEN at t-W+1
- close = CLOSE at t
- high = max HIGH over t-W+1..t
- low = min LOW over t-W+1..t

Feature:

abs(close - open) / (high - low)

If range is zero, use 0.

Total new features:
6 windows x 6 features = 36.

Total REP_B_PATH84 features:
48 + 36 = 84.

## Causality / completeness

A REP_B row is feature-complete only when:

- the original EXP-005 feature row is complete;
- the preceding 240 minutes are exactly contiguous at one-minute spacing;
- every new path feature is finite.

No forward row may be used.

## Models

For each representation and direction, reuse EXP-005 models unchanged.

### Model A — direct executable gross-P&L regressor

HistGradientBoostingRegressor:
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

TRAIN thinning:
- every 5th eligible chronological TRAIN row.

Target:
- SUCCESS +5
- FAILURE -3
- UNRESOLVED actual expiry P&L

AMBIGUOUS excluded.

Predicted gross P&L clipped to [-3,+5].

DIRECT_NET_F10 = predicted gross P&L - 0.10.

### Model B — <=5-minute EARLY_FAILURE classifier

Definition unchanged from EXP-005:

EARLY_FAILURE = 1 iff a realized FAILURE reaches the adverse barrier within <=5 calendar
minutes after executable entry.

Same HistGradientBoostingClassifier hyperparameters as EXP-005.

No model or hyperparameter search.

## Validation-derived downside gates

For each representation and direction separately, derive from VALIDATION 2022 predicted
EARLY_FAILURE risk:

- EF_Q50
- EF_Q25
- EF_Q10

Definitions unchanged from EXP-005.

This allows each representation to be judged using its own frozen validation ranking distribution.

No additional risk quantiles may be introduced.

## Policy arms within each representation

For both REP_A and REP_B:

- DIRECT_ONLY
- DIRECT_EF_Q50
- DIRECT_EF_Q25
- DIRECT_EF_Q10

Only REP_B policies are eligible for advancement.

## Direct-score thresholds

Reuse unchanged:

- T0: DIRECT_NET_F10 > 0.00
- T25: >= +0.25
- T50: >= +0.50
- T75: >= +0.75

No additional thresholds.

## Direction conflict rule

Unchanged:
- neither qualifies => NO_TRADE
- exactly one qualifies => that direction
- both qualify => choose larger DIRECT_NET_F10 only if absolute score difference >=0.25
- otherwise NO_TRADE

## Sequential execution

Unchanged:
- one global position at a time
- no pyramiding
- no averaging
- no reversal while open
- suppress later signals until exit

## Required representation comparison

For BASE48 versus PATH84, BUY and SELL separately, report on VALIDATION and DEVELOPMENT_TEST:

Direct regressor:
- MAE
- RMSE
- mean predicted / realized gross P&L
- Pearson correlation
- realized gross P&L by predicted-score decile
- fixed DIRECT_NET_F10 bands

EARLY_FAILURE:
- base rate
- ROC-AUC
- PR-AUC
- Brier score
- risk deciles vs realized early-failure frequency
- 2023 and 2024 separately

Representation delta:
- change in direct-P&L Pearson correlation
- change in early-failure ROC-AUC / PR-AUC
- change in high-score realized NET_F10
- change in qualifying raw-signal counts

## Required sequential economics

For:
- REP_A / REP_B
- DIRECT_ONLY / Q50 / Q25 / Q10
- T0 / T25 / T50 / T75
- BUY_ONLY / SELL_ONLY / COMBINED

report:
- raw qualifying observations
- executed trades
- suppression ratio
- outcome counts
- EARLY_FAILURE count/share
- F0/F05/F10/F20
- DEVELOPMENT_TEST overall
- 2023
- 2024
- each quarter
- profit factor
- cumulative P&L
- max drawdown
- active days
- trade frequency
- holding-time quantiles

## Dependence-aware uncertainty

For REP_B policies:
- UTC entry-date block bootstrap
- 2,000 replicates
- seed = 6
- 95% percentile CI of mean NET_F10

## Advancement rule

A REP_B policy may advance only if ALL:

1. mean NET_F10 >0 in 2023
2. mean NET_F10 >0 in 2024
3. overall F10 profit factor >1
4. UTC-day bootstrap lower 95% bound >0
5. >=250 DEVELOPMENT_TEST trades
6. >=75 trades in each 2023 and 2024
7. no single quarter contributes >40% of total positive F10 P&L
8. AMBIGUOUS treated as -3
9. 2025 untouched

REP_A cannot advance regardless of result.

Passing does not automatically open 2025.

## Interpretation

- REP_B materially improves predictive diagnostics and passes economics:
  representation was a key missing ingredient.

- REP_B improves diagnostics but no policy passes:
  richer path structure helps but is still insufficient.

- REP_B does not improve diagnostics:
  the current model family/target may be the limiting factor rather than representation.

## Governance

EXP-006 must not:
- access 2025
- add external event/news data
- tune model hyperparameters
- select/drop new features after results
- change the <=5-minute early-failure definition
- add risk quantiles
- add score thresholds
- add post-hoc regime filters
- proceed to Exness demo/live

External event/session research is explicitly deferred so EXP-006 isolates price-path representation.

## Exit states

A. NO REP_B POLICY PASSES
- 2025 remains sealed
- diagnose
- next experiment may change model family or add separately preregistered external context

B. ONE OR MORE REP_B POLICIES PASS
- 2025 remains sealed
- freeze all passers in a separate milestone
- audit implementation/leakage before any FINAL_OOS access

2025 remains sealed in all cases.
