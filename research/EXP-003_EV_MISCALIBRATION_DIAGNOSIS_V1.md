# EXP-003 — EV Miscalibration Diagnosis V1

Status: FROZEN BEFORE DIAGNOSTIC RESULTS

## Purpose

Explain why the frozen EXP-003 V1 expected-value score is materially more optimistic than realized executable P&L in the positive-EV region.

This milestone is diagnostic only. It does not create EXP-004.

FINAL_OOS 2025 remains sealed.

## Scope

Reproduce exactly the frozen EXP-003 V1 models using:

- TRAIN 2016-2021 for fitting;
- VALIDATION 2022 for reference calibration;
- DEVELOPMENT_TEST 2023-2024 for diagnosis.

No model, feature, target, threshold, friction, or execution rule may be changed.

## Primary diagnostic question

For each direction, why does:

predicted EV_F10

fail to match:

realized executable NET_F10?

Decompose the gap into:

1. SUCCESS-probability error;
2. FAILURE-probability error;
3. UNRESOLVED-probability error;
4. conditional UNRESOLVED expiry-P&L error.

## Frozen analysis populations

Report all diagnostics for:

- ALL scored rows;
- T0: EV_F10 > 0.00;
- T25: EV_F10 >= 0.25;
- T50: EV_F10 >= 0.50;
- T75: EV_F10 >= 0.75.

These are the already-preregistered EXP-003 thresholds only.

Do not introduce new cutoffs.

## D1 — Predicted versus realized outcome components

For each direction / partition / frozen threshold population report:

Predicted:
- mean P(SUCCESS);
- mean P(FAILURE);
- mean P(UNRESOLVED);
- mean predicted unresolved expiry P&L;
- mean predicted EV_GROSS;
- mean predicted EV_F10.

Realized:
- SUCCESS share;
- FAILURE share;
- UNRESOLVED share;
- AMBIGUOUS share;
- realized mean unresolved expiry P&L;
- realized mean gross P&L;
- realized mean NET_F10.

Errors:
- P(SUCCESS) prediction error;
- P(FAILURE) prediction error;
- P(UNRESOLVED) prediction error;
- unresolved conditional-P&L prediction error;
- EV_F10 calibration error = predicted mean EV_F10 - realized mean NET_F10.

Purpose:
identify which component creates the economic optimism.

## D2 — Counterfactual component substitution

For each population compute:

A. MODEL_EV:
use all model-predicted components.

B. ACTUAL_CLASS_RATES_EV:
replace predicted class probabilities with realized class frequencies while retaining predicted mean unresolved expiry P&L.

C. ACTUAL_UNRESOLVED_PNL_EV:
retain predicted class probabilities but replace predicted unresolved expiry P&L with realized unresolved mean.

D. FULL_COMPONENT_REALIZED_EV:
use realized class frequencies and realized unresolved mean.

All values use the frozen +5 / -3 / F10 economics.

Purpose:
quantify whether class-probability error or unresolved-P&L regression error dominates the EV gap.

This is diagnostic arithmetic only, not a trading policy.

## D3 — Class-specific calibration in positive-EV tails

For SUCCESS, FAILURE, and UNRESOLVED separately:

- split predicted class probability into fixed bins:
  - [0.00,0.10)
  - [0.10,0.20)
  - [0.20,0.30)
  - [0.30,0.40)
  - [0.40,0.50)
  - [0.50,0.60)
  - [0.60,0.70)
  - [0.70,0.80)
  - [0.80,0.90)
  - [0.90,1.00]
- report predicted mean probability and realized frequency.

Report separately for:
- VALIDATION 2022;
- DEVELOPMENT_TEST 2023;
- DEVELOPMENT_TEST 2024.

Purpose:
detect probability-calibration drift, especially underestimation of FAILURE.

## D4 — Temporal drift

For each frozen threshold population and direction, report component decomposition for:

- VALIDATION 2022;
- 2023;
- 2024;
- each 2023-2024 quarter.

Purpose:
determine whether EXP-003 fails because the relationship learned from TRAIN/VALIDATION changes materially in 2024.

## D5 — Predicted-EV error distribution

For rows with complete executable outcomes define:

EV_ERROR = predicted EV_F10 - realized NET_F10.

Report:
- mean;
- median;
- p10 / p25 / p75 / p90;
- RMSE;
- MAE.

Report for:
- ALL;
- T0;
- T25;
- T50;
- T75;
- 2023 and 2024 separately.

Purpose:
distinguish broad bias from a small number of extreme misses.

## D6 — Error by realized outcome

For each threshold population report EV_ERROR separately for realized:

- SUCCESS;
- FAILURE;
- UNRESOLVED;
- AMBIGUOUS.

Purpose:
test whether positive predicted EV is specifically overconfident on eventual FAILURE rows.

## D7 — Sequential opportunity calibration

Using the already-frozen one-position-at-a-time rules for BUY_ONLY and SELL_ONLY:

At T0/T25/T50/T75 report executed trades with:
- mean predicted entry EV_F10;
- mean realized NET_F10;
- calibration gap;
- outcome composition;
- 2023 / 2024 split.

For COMBINED, use the frozen 0.25 conflict rule.

Purpose:
verify whether raw-row miscalibration survives at actual executed opportunity level.

## D8 — Feature-distribution shift summary

TRAIN feature-distribution reference:
- use the same deterministic every-5th eligible chronological TRAIN-row thinning already frozen for EXP-003 classifier fitting;
- require feature_complete and a finite frozen feature vector;
- this sampling rule is fixed before diagnostic results and is used for D8 and D9 only.

Using only the frozen EXP-003 feature vector, compare the TRAIN reference versus:

- VALIDATION 2022;
- DEVELOPMENT_TEST 2023;
- DEVELOPMENT_TEST 2024.

For each feature report:
- TRAIN median and IQR;
- target-period median and IQR;
- median shift normalized by TRAIN IQR.

Rank by absolute normalized median shift.

This is descriptive only.

No feature may be selected, removed, or added from this ranking within EXP-003.

Purpose:
identify whether large causal market-state distribution shifts plausibly accompany the 2024 calibration failure.

## D9 — Tail support / extrapolation

Using the same frozen TRAIN reference from D8, for T0/T25/T50/T75 rows report, for each frozen feature:

- share below TRAIN 1st percentile;
- share above TRAIN 99th percentile.

Also report:
- share of rows with at least one feature outside TRAIN 1%-99% support;
- median number of out-of-support features per row.

Purpose:
test whether positive-EV signals occur disproportionately in market states weakly represented in TRAIN.

## Governance

This diagnosis MUST NOT:

- access 2025;
- fit a new model;
- recalibrate probabilities;
- tune thresholds;
- add or remove features;
- select regimes;
- promote BUY-only or SELL-only;
- reinterpret failed EXP-003 gates;
- proceed to Exness demo/live.

## Exit criterion

The milestone ends with a documented diagnosis that identifies the dominant measured sources of EV miscalibration.

Only after that diagnosis is sealed may EXP-004 be designed and preregistered.

2025 remains sealed.
