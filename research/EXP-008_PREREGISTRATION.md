# EXP-008 — Competing Hazard Target-Before-Adverse V1

Status: FROZEN BEFORE EMPIRICAL RESULTS

## Purpose

Test whether executable trade quality becomes predictable when the target and adverse-barrier
processes are modeled as competing time-to-event outcomes rather than as raw P&L regression.

FINAL_OOS 2025 remains sealed.

## Motivation

Completed experiments established:

- direct executable-P&L regression is weak or catastrophically miscalibrated;
- <=5-minute adverse-barrier failure is consistently highly rankable;
- richer hand-crafted path features did not solve trade quality;
- a small sequence model preserved downside-risk discrimination but did not produce reliable
  positive-tail P&L forecasts.

EXP-008 therefore changes the target formulation itself.

## Data and partitions

Use synchronized Dukascopy XAUUSD M1 BID+ASK.

Chronological partitions:
- TRAIN: 2016-2021
- VALIDATION: 2022
- DEVELOPMENT_TEST: 2023-2024
- FINAL_OOS: 2025 — SEALED
- 2026: later forward/shadow only

No EXP-008 workflow may access 2025.

## Executable semantics

Unchanged.

BUY:
- entry next M1 ASK open;
- target +5 evaluated on BID;
- adverse -3 evaluated on BID.

SELL:
- entry next M1 BID open;
- target -5 evaluated on ASK;
- adverse +3 evaluated on ASK.

Horizon:
- 60 calendar minutes;
- exact synchronized coverage required.

AMBIGUOUS:
- excluded from model fitting;
- treated as -3 in economic evaluation.

## Frozen input representation

Use exact BASE48 representation from EXP-005.

No PATH84 features.
No sequence model.
No external event/news data.

Reason:
EXP-008 is an isolated target-formulation experiment.

## Competing-hazard classes

For each direction, every eligible non-AMBIGUOUS row is assigned exactly one class.

SUCCESS classes:
- S_00_05: target-first terminal time <=5 minutes
- S_06_15: target-first terminal time 6-15 minutes
- S_16_30: target-first terminal time 16-30 minutes
- S_31_60: target-first terminal time 31-60 minutes

FAILURE classes:
- F_00_05: adverse-first terminal time <=5 minutes
- F_06_15: adverse-first terminal time 6-15 minutes
- F_16_30: adverse-first terminal time 16-30 minutes
- F_31_60: adverse-first terminal time 31-60 minutes

UNRESOLVED:
- U_60: neither executable barrier reached within 60 minutes.

Terminal time is computed from executable decision/entry time to the terminal event time,
using the same +1-minute terminal-bar convention already used in prior sequential evaluation.

Any SUCCESS/FAILURE terminal time outside 1-60 minutes is an implementation error.

## Base competing-hazard model

Train BUY and SELL independently.

Model:
HistGradientBoostingClassifier

Frozen hyperparameters:
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

TRAIN sampling:
- every 5th eligible chronological TRAIN row.

No hyperparameter search.

## Chronological probability calibration

Because prior experiments exposed severe positive-tail probability miscalibration,
EXP-008 applies the already-established strictly out-of-time TRAIN calibration protocol.

For BUY and SELL independently:

- train base model on 2016 -> predict 2017;
- train 2016-2017 -> predict 2018;
- train 2016-2018 -> predict 2019;
- train 2016-2019 -> predict 2020;
- train 2016-2020 -> predict 2021.

These out-of-time predictions form the calibrator dataset.

Calibrator inputs:
- log of clipped base probabilities for all nine hazard classes.

Clip:
- [1e-6, 1-1e-6]

Calibrator:
- multinomial LogisticRegression
- L2 penalty
- C = 1.0
- solver = lbfgs
- max_iter = 1000
- class_weight = None
- random_state = 1

No calibrator hyperparameter search.

After calibrator fitting:
- refit base hazard model on full TRAIN 2016-2021;
- score VALIDATION and DEVELOPMENT_TEST;
- apply frozen calibrator.

## UNRESOLVED expiry-P&L model

For rows whose realized class is U_60, train the same frozen TRAIN-only unresolved-expiry
HistGradientBoostingRegressor used in EXP-003/004.

Hyperparameters:
- squared_error
- learning_rate 0.05
- max_iter 200
- max_leaf_nodes 15
- min_samples_leaf 200
- l2_regularization 1.0
- max_bins 255
- early_stopping false
- random_state 1

TRAIN sampling:
- every 5th eligible chronological U_60 row.

Predictions clipped to [-3,+5].

## Hazard-derived probabilities

For each scored row:

P_SUCCESS =
P(S_00_05)+P(S_06_15)+P(S_16_30)+P(S_31_60)

P_FAILURE =
P(F_00_05)+P(F_06_15)+P(F_16_30)+P(F_31_60)

P_UNRESOLVED =
P(U_60)

P_EARLY_FAILURE =
P(F_00_05)

All probabilities come from the calibrated nine-class model.

## Hazard economic value

EV_HAZARD_GROSS =
5 * P_SUCCESS
- 3 * P_FAILURE
+ P_UNRESOLVED * predicted_unresolved_expiry_PnL

Primary score:

EV_HAZARD_F10 = EV_HAZARD_GROSS - 0.10

No additional timing bonus or penalty is introduced.
The time bins exist to improve competing-risk representation, not to rewrite realized economics.

## Validation-derived early-failure gates

For BUY and SELL independently, derive from VALIDATION 2022 calibrated P_EARLY_FAILURE:

- EF_Q50 = 50th percentile
- EF_Q25 = 25th percentile
- EF_Q10 = 10th percentile

Lower early-failure risk is better.

No additional early-failure cutoff may be introduced.

## Policy arms

A_HAZARD_EV:
- EV threshold only.

B_HAZARD_EV_EF_Q50:
- EV threshold and P_EARLY_FAILURE <= validation Q50.

C_HAZARD_EV_EF_Q25:
- EV threshold and P_EARLY_FAILURE <= validation Q25.

D_HAZARD_EV_EF_Q10:
- EV threshold and P_EARLY_FAILURE <= validation Q10.

All four arms are eligible for advancement.

## Frozen EV thresholds

Reuse unchanged:
- T0: EV_HAZARD_F10 > 0.00
- T25: >= +0.25
- T50: >= +0.50
- T75: >= +0.75

No additional thresholds.

## Direction conflict rule

Unchanged:
- neither qualifies => NO_TRADE
- exactly one qualifies => that direction
- both qualify:
  - choose larger EV_HAZARD_F10 only if absolute difference >=0.25
  - otherwise NO_TRADE

## Sequential execution

Unchanged:
- one global position at a time
- no pyramiding
- no averaging
- no reversal while open
- later qualifying signals suppressed until current exit

## Required predictive diagnostics

For BUY and SELL separately on VALIDATION 2022, DEVELOPMENT_TEST overall, 2023, and 2024:

Nine-class model:
- multiclass log loss
- macro Brier score
- per-class predicted share versus realized share
- P_SUCCESS predicted versus realized
- P_FAILURE predicted versus realized
- P_UNRESOLVED predicted versus realized
- P_EARLY_FAILURE predicted versus realized

Hazard score:
- mean predicted EV_HAZARD_F10
- mean realized NET_F10
- calibration gap
- realized NET_F10 by predicted EV decile
- realized NET_F10 by T0/T25/T50/T75 raw qualifying rows

## Required sequential economics

For:
- A/B/C/D arms
- T0/T25/T50/T75
- BUY_ONLY / SELL_ONLY / COMBINED

Report:
- raw qualifying observations
- executed trades
- suppression ratio
- outcome counts
- <=5-minute early-failure count/share
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

For every policy:
- group DEVELOPMENT_TEST trades by UTC entry date
- bootstrap whole dates with replacement
- 2,000 replicates
- seed = 8
- report 95% percentile CI for mean NET_F10

## Advancement rule

A policy may advance only if ALL:

1. mean NET_F10 >0 in 2023
2. mean NET_F10 >0 in 2024
3. overall F10 profit factor >1
4. UTC-day bootstrap 95% lower bound >0
5. >=250 DEVELOPMENT_TEST trades
6. >=75 trades in each 2023 and 2024
7. no single quarter contributes >40% of total positive F10 P&L
8. AMBIGUOUS treated as -3
9. 2025 untouched

Passing does not automatically open 2025.

If multiple policies pass, retain all passers for a separate immutable pre-OOS freeze.

## Governance

EXP-008 must not:
- access 2025
- tune time-bin boundaries
- tune model/calibrator hyperparameters
- add/remove BASE48 features
- add PATH84 or sequence inputs
- add external event/news context
- add early-failure cutoffs
- add EV thresholds
- introduce post-hoc regime filters
- proceed to Exness demo/live

Negative results are admissible.

## Exit states

A. NO POLICY PASSES
- keep 2025 sealed
- diagnose whether competing-hazard probabilities were informative/calibrated
- next experiment may add separately preregistered timestamp-safe exogenous context

B. ONE OR MORE POLICIES PASS
- keep 2025 sealed
- freeze all passers separately
- perform implementation/leakage/calibration audit before any FINAL_OOS access

2025 remains sealed in all cases.
