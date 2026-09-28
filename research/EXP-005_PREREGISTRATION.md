# EXP-005 — Downside-First Direct Economic Model V1

Status: FROZEN BEFORE EMPIRICAL RESULTS

## Purpose

Test whether XAU/USD opportunities can be identified more robustly by modeling:

1. realized executable trade P&L directly; and
2. the risk of rapid adverse-barrier failure separately.

EXP-005 is a new experiment descended from EXP-004.

FINAL_OOS 2025 remains sealed.

## Motivation

Prior experiments established:

- binary SUCCESS ranking had signal but negative sequential economics;
- derived EV from SUCCESS / FAILURE / UNRESOLVED probabilities remained badly miscalibrated in positive-EV tails;
- chronological calibration improved aggregate fit but did not create robust trading economics;
- support gating did not rescue performance;
- rapid <=5 minute outcomes were strongly negative in prior diagnostics;
- 2024 remained materially difficult.

EXP-005 therefore changes the prediction objective rather than retuning calibration or thresholds.

## Data and partitions

Use synchronized Dukascopy XAUUSD M1 BID+ASK.

Chronological partitions remain:

- TRAIN: 2016-2021
- VALIDATION: 2022
- DEVELOPMENT_TEST: 2023-2024
- FINAL_OOS: 2025 — SEALED
- 2026: reserved for later forward/shadow work

No EXP-005 development workflow may request, read, label, featurize, score, summarize, or inspect 2025.

## Executable semantics

Reuse EXP-002+ unchanged.

BUY:
- enter next-bar ASK open;
- target +5 evaluated on BID;
- adverse -3 evaluated on BID.

SELL:
- enter next-bar BID open;
- target -5 evaluated on ASK;
- adverse +3 evaluated on ASK.

Horizon:
- 60 calendar minutes;
- exact synchronized coverage required.

Realized gross P&L:
- SUCCESS = +5;
- FAILURE = -3;
- UNRESOLVED = actual executable 60-minute expiry P&L;
- AMBIGUOUS = excluded from model fitting and treated as -3 for evaluation.

## Frozen feature vector

Reuse the exact EXP-004 / EXP-003 feature vector.

No new feature engineering, selection, deletion, or transformation in EXP-005 V1.

Reason:
EXP-005 is testing a new target/objective representation.

## Model A — Direct executable-P&L regressor

For BUY and SELL separately.

Training population:
- TRAIN 2016-2021;
- partition-boundary eligible;
- coverage complete;
- feature complete;
- AMBIGUOUS excluded.

Target:
- realized executable gross P&L:
  - SUCCESS +5;
  - FAILURE -3;
  - UNRESOLVED actual expiry P&L.

Model:
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

TRAIN thinning:
- every 5th eligible chronological TRAIN row.

Predicted gross P&L is clipped to [-3,+5].

Primary direct economic score:

DIRECT_NET_F10 =
predicted gross P&L - 0.10

No regressor hyperparameter search.

## Model B — Early-failure risk classifier

For BUY and SELL separately.

Target:

EARLY_FAILURE = 1 iff:
- realized label is FAILURE; and
- the adverse barrier terminal time is <= 5 calendar minutes after entry/decision time.

Otherwise:
EARLY_FAILURE = 0.

AMBIGUOUS rows are excluded from fitting.

The 5-minute threshold is frozen before EXP-005 results and is motivated by the prior completed diagnosis showing strongly negative economics among <=5-minute completed trades.

Model:
- HistGradientBoostingClassifier
- binary log loss
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

No hyperparameter search.

## Validation-derived downside gates

The early-failure model is used as a ranking risk score, not assumed to be a perfectly calibrated literal probability.

For BUY and SELL independently, calculate the EARLY_FAILURE predicted probability distribution on VALIDATION 2022.

Freeze these three maximum-risk cutoffs from VALIDATION:

- EF_Q50 = 50th percentile of VALIDATION predicted EARLY_FAILURE risk;
- EF_Q25 = 25th percentile;
- EF_Q10 = 10th percentile.

Lower predicted EARLY_FAILURE risk is better.

These quantile definitions are frozen before any EXP-005 result.

No additional risk quantile may be introduced after results.

## Experimental arms

### ARM A — DIRECT_ONLY

Trade eligibility is based only on DIRECT_NET_F10.

Purpose:
test direct executable-P&L regression alone.

### ARM B — DIRECT_EF_Q50

DIRECT_NET_F10 must qualify and predicted EARLY_FAILURE risk must be <= the frozen VALIDATION Q50 cutoff for that direction.

### ARM C — DIRECT_EF_Q25

DIRECT_NET_F10 must qualify and predicted EARLY_FAILURE risk must be <= the frozen VALIDATION Q25 cutoff.

### ARM D — DIRECT_EF_Q10

DIRECT_NET_F10 must qualify and predicted EARLY_FAILURE risk must be <= the frozen VALIDATION Q10 cutoff.

All four arms are eligible for advancement.

## Frozen direct-score thresholds

Reuse the established economic margins:

- T0: DIRECT_NET_F10 > 0.00
- T25: DIRECT_NET_F10 >= +0.25
- T50: DIRECT_NET_F10 >= +0.50
- T75: DIRECT_NET_F10 >= +0.75

No additional direct-score cutoff may be introduced after results.

## Direction conflict rule

For each arm and threshold:

- neither BUY nor SELL qualifies => NO TRADE;
- exactly one qualifies => that direction;
- both qualify:
  - choose larger DIRECT_NET_F10 only if absolute difference >= 0.25;
  - otherwise NO TRADE.

The conflict margin remains frozen at 0.25.

## Opportunity-level execution

Reuse prior rules:

- one global position at a time;
- no pyramiding;
- no averaging;
- no reversal while a trade is open;
- later qualifying observations are ignored until exit.

Raw signal counts and suppression ratios must still be reported.

## Required predictive diagnostics

For BUY and SELL separately report on VALIDATION and DEVELOPMENT_TEST:

Direct regressor:
- MAE;
- RMSE;
- mean predicted gross P&L;
- mean realized gross P&L;
- Pearson correlation;
- realized gross P&L by predicted-score decile;
- predicted-vs-realized mean by fixed DIRECT_NET_F10 bands:
  - <= -0.50
  - (-0.50,0]
  - (0,0.25)
  - [0.25,0.50)
  - [0.50,0.75)
  - >=0.75

Early-failure classifier:
- base EARLY_FAILURE rate;
- ROC-AUC;
- PR-AUC;
- Brier score;
- predicted risk deciles versus realized EARLY_FAILURE frequency;
- 2023 and 2024 separately.

## Required sequential economics

For:

- ARM A/B/C/D;
- T0/T25/T50/T75;
- BUY_ONLY / SELL_ONLY / COMBINED;

report:

- raw qualifying observations;
- executed trades;
- suppression ratio;
- SUCCESS / FAILURE / UNRESOLVED / AMBIGUOUS counts;
- EARLY_FAILURE count/share among executed trades;
- F0 / F05 / F10 / F20;
- overall DEVELOPMENT_TEST;
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

For every arm/threshold/mode on DEVELOPMENT_TEST:

- group completed trades by UTC entry date;
- bootstrap whole dates with replacement;
- 2,000 replicates;
- seed = 5;
- report 95% percentile CI of mean NET_F10.

## Advancement rule

An arm/threshold/mode may advance only if ALL hold:

1. mean NET_F10 > 0 in 2023;
2. mean NET_F10 > 0 in 2024;
3. overall F10 profit factor > 1;
4. UTC-day bootstrap 95% lower bound > 0;
5. at least 250 DEVELOPMENT_TEST trades overall;
6. at least 75 trades in each of 2023 and 2024;
7. no single calendar quarter contributes >40% of total positive F10 P&L;
8. AMBIGUOUS treated as -3;
9. 2025 untouched.

Passing does not automatically open 2025.

If multiple policies pass, retain all passers for a separate immutable pre-OOS candidate-freeze milestone.

No post-hoc winner selection in EXP-005.

## Interpretation

The experiment distinguishes:

- DIRECT_ONLY passes:
  direct economic target was sufficient.

- DIRECT_ONLY fails but one or more downside-gated arms pass:
  explicit rapid-downside discrimination was necessary.

- all arms fail:
  the current frozen feature representation still cannot isolate a robust executable edge, and a later experiment may require new market-state representation.

## Governance

EXP-005 must not:

- access 2025;
- tune model hyperparameters;
- change the 5-minute EARLY_FAILURE definition;
- add risk quantiles;
- add direct-score thresholds;
- introduce support/regime filters post hoc;
- add/remove features;
- proceed to Exness demo/live.

Negative results are admissible.

## Exit states

A. NO POLICY PASSES
- keep 2025 sealed;
- diagnose;
- redesign only in a new preregistered experiment.

B. ONE OR MORE POLICIES PASS
- keep 2025 sealed;
- freeze all passers separately;
- conduct implementation/leakage audit before any FINAL_OOS access.

2025 remains sealed in all cases.
