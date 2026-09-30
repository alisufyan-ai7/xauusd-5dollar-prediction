# Root-Reset V2 — Joint Excursion Dynamic Reward/Risk

Status: FROZEN BEFORE EMPIRICAL RESULTS

## Purpose

Correct the primary Root-Reset V1 failure:

- $5 opportunity ranking was useful;
- the fixed $3.333 stop ceiling rejected the highest-quality high-volatility states.

V2 therefore models favorable and adverse excursion jointly and derives candidate-specific
trade geometry from the predicted path distribution.

FINAL_OOS 2025 remains sealed.

## Data boundaries

TRAIN:
- 2016-2021

VALIDATION:
- 2022

DEVELOPMENT_TEST:
- 2023-2024, accessed only if one V2 policy qualifies on validation

FINAL_OOS:
- 2025, sealed

## Event sampling

Reuse Root-Reset V1 exactly:
- same causal ATR15_PROXY;
- same CUSUM continuation event detector;
- same +/-1.0 standardized cumulative threshold;
- same 5-minute cooldown;
- positive event => BUY continuation candidate;
- negative event => SELL continuation candidate.

No reversal setup is introduced.

## Executable excursion targets

For every event candidate over the next 60 minutes:

- MFE60 = maximum favorable executable excursion;
- MAE60 = maximum adverse executable excursion.

BUY:
- entry at next M1 ASK open;
- favorable liquidation on BID;
- adverse excursion on BID.

SELL:
- entry at next M1 BID open;
- favorable liquidation on ASK;
- adverse excursion on ASK.

No fixed stop or target is used to define the learning target.

## Models

Train BUY and SELL independently.

Input:
- exact BASE48 feature vector from V1.

### Favorable excursion model

Predict conditional quantiles of MFE60 using HistGradientBoostingRegressor.

Quantiles:
- q50
- q70
- q80

Loss:
- quantile

Frozen hyperparameters for each quantile model:
- learning_rate = 0.05
- max_iter = 200
- max_leaf_nodes = 15
- max_depth = None
- min_samples_leaf = 100
- l2_regularization = 1.0
- max_bins = 255
- early_stopping = false
- random_state = 2

Predictions clipped to [0, 20].

### Adverse excursion model

Predict conditional quantiles of MAE60 with the same model family/hyperparameters.

Quantiles:
- q50
- q70
- q80

Predictions clipped to [0, 20].

No hyperparameter search.

## Candidate dynamic geometry

Three preregistered geometries:

### G50
- TARGET = max($3, MFE_q50)
- STOP = max($0.75, MAE_q50)

### G70
- TARGET = max($3, MFE_q70)
- STOP = max($0.75, MAE_q70)

### G80
- TARGET = max($3, MFE_q80)
- STOP = max($0.75, MAE_q80)

Caps:
- TARGET capped at $8
- STOP capped at $6

These caps are execution-safety bounds, not optimization variables.

## Minimum opportunity requirement

Owner objective remains that a trade should normally have potential for about $5 or more.

Therefore a candidate is eligible only if:

MFE_q70 >= $5

This is the single V2 opportunity gate.

Reason:
- q50 is too permissive for a $5 objective;
- q80 may be too sparse;
- q70 is the preregistered central criterion.

No opportunity-probability classifier threshold is used in V2.

## Reward/risk gate

For each geometry separately:

TARGET / STOP >= 1.20

This is intentionally lower than V1's 1.50 because the observed gold path distribution shows that
large favorable excursions coexist with large adverse excursions.

No hard stop ceiling is imposed beyond the $6 safety cap.

## Path ordering filter

A candidate is rejected if TRAIN-fitted median excursion predictions imply:

MAE_q50 > MFE_q50

Purpose:
avoid states whose central path estimate is adverse-dominant.

This is frozen before validation.

## Management policies

For each geometry G50/G70/G80, compare two management modes.

### H — HOLD_DYNAMIC_TARGET

- enter with geometry-specific dynamic STOP;
- hold for dynamic TARGET;
- otherwise exit at 60 minutes.

### B3 — PROTECT_AT_3

- enter with geometry-specific dynamic STOP;
- if executable favorable excursion reaches +$3 before exit:
  move stop to entry +$0.10 gross for BUY;
  move stop to entry -$0.10 gross for SELL;
- continue holding for the dynamic TARGET;
- otherwise exit at 60 minutes.

No TAKE_3 policy in V2:
V1 did not reach economics testing, and V2 focuses first on whether adaptive geometry can support
the owner's desired ~$5+ opportunity.

## Validation selection

All six policies are evaluated exactly once on VALIDATION 2022:

- G50-H
- G50-B3
- G70-H
- G70-B3
- G80-H
- G80-B3

A policy qualifies for DEVELOPMENT_TEST only if ALL:

1. >=100 executed validation trades;
2. mean VALIDATION NET_F10 >0;
3. VALIDATION profit factor >1;
4. at least 40% of executed trades have TARGET >= $5;
5. median realized MFE60 of executed trades >= $4.

If zero policies qualify:
- stop V2;
- do not access 2023-2024.

If multiple policies qualify:
- select the policy with highest VALIDATION mean NET_F10;
- tie within $0.05 => prefer larger trade count;
- exact tie => prefer B3, then lower geometry number (G50 before G70 before G80).

This selection rule is frozen before validation results.

## Sequential execution

- one global position at a time;
- no pyramiding;
- no averaging;
- no reversal while open;
- later candidates suppressed until current trade exits.

## Friction

Report:
- F0
- F05
- F10
- F20

Primary selection/evaluation friction:
- F10

## DEVELOPMENT_TEST advancement

If one policy qualifies on 2022 and is frozen, evaluate only that policy on 2023-2024.

It may advance only if ALL:

1. mean NET_F10 >0 in 2023;
2. mean NET_F10 >0 in 2024;
3. overall F10 profit factor >1;
4. UTC-day bootstrap 95% lower bound >0;
5. >=250 DEVELOPMENT_TEST trades;
6. >=75 trades in each year;
7. no quarter contributes >40% of total positive F10 P&L;
8. 2025 untouched.

Bootstrap:
- 2,000 replicates;
- seed = 10.

Passing still does not automatically open 2025.

## Required diagnostics

VALIDATION for each direction:
- MFE q50/q70/q80 prediction calibration;
- MAE q50/q70/q80 prediction calibration;
- realized quantile coverage;
- Pearson/Spearman correlation of predicted q70 with realized excursion;
- eligible-candidate counts;
- TARGET and STOP distributions;
- TARGET/STOP ratio distribution.

For each policy:
- raw eligible events;
- executed trades;
- suppression ratio;
- mean target;
- mean stop;
- target >=$5 share;
- realized MFE/MAE;
- exit reasons;
- economics F0/F05/F10/F20.

## Governance

Do not:
- alter event sampling;
- add new quantiles;
- tune model hyperparameters;
- add new geometry formulas;
- change q70 >=$5 opportunity gate;
- change 1.20 reward/risk gate;
- add a fixed stop ceiling below the $6 safety cap;
- add partial exits;
- access 2023-2024 unless validation qualifies;
- access 2025;
- proceed to Exness demo/live.

Negative results are admissible.

## Interpretation

V2 tests whether the root problem was fixed reward/risk geometry rather than absence of an event-driven edge.

If V2 fails at validation:
- do not continue threshold tuning;
- reconsider the setup family or add genuinely new information.

If V2 qualifies and passes DEVELOPMENT_TEST:
- freeze implementation and audit before any FINAL_OOS decision.
