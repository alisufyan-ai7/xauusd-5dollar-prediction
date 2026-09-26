# EXP-001 Logistic Regression Milestone V1

Status: FROZEN BEFORE EXECUTION

## Purpose

Test whether the timestamp-safe V2 expert features contain incremental predictive information for the original event:

- BUY: +$5 before -$3 within 60 minutes;
- SELL: -$5 before +$3 within 60 minutes.

This is the first predictive model. It is intentionally simple.

## Data partitions

- TRAIN: 2016-2021 — model fitting only.
- VALIDATION: 2022 — first chronological evaluation.
- DEVELOPMENT_TEST: 2023-2024 — second chronological evaluation.
- FINAL_OOS: 2025 — strictly not accessed.
- AMBIGUOUS rows excluded.
- FAILURE and UNRESOLVED are both target 0.
- SUCCESS is target 1.
- Rows require complete outcome coverage, partition eligibility, and V2 feature completeness.

## Frozen feature set

Use numeric V2 features only:

- ret_5m
- ret_15m
- ret_30m
- ret_60m
- ret_120m
- ret_240m
- rv_15m
- rv_60m
- rv_120m
- rv_240m
- tr_mean_60m
- rv_short_long_ratio
- compression_expansion_ratio
- rv60_percentile_240m
- recent_5dollar_range_frequency_240m
- range_position_60m
- range_position_240m
- slope_15m
- slope_60m
- slope_240m
- trend_persistence_15m
- trend_persistence_60m
- trend_persistence_240m
- directional_agreement_m5_m15_h1_h4
- body_range_ratio_1m
- close_location_1m
- wick_asymmetry_1m
- impulse_15m
- pullback_depth_15m
- impulse_pullback_ratio_15m
- return_acceleration_5v15
- directional_consistency_5m
- directional_consistency_15m
- directional_consistency_30m
- current_day_range_position
- distance_round_5
- distance_round_10
- minutes_to_session_transition
- europe_us_overlap
- session_rv_60m

Session category itself is not one-hot encoded in V1; session timing/volatility features are present.

## Direction handling

Fit two separate logistic models:

- BUY model using buy_label.
- SELL model using sell_label.

No shared parameters between directions.

## Preprocessing

- Compute feature mean and population standard deviation on TRAIN only.
- Apply those fixed TRAIN statistics to all partitions.
- Missing/non-finite feature rows are excluded.
- Standard deviation values effectively equal to zero are replaced by 1.

## Optimizer

Use deterministic streaming logistic regression with:

- full chronological TRAIN passes;
- 4 epochs;
- learning rate 0.03 / sqrt(epoch);
- L2 coefficient 1e-4;
- probability clipping at 1e-12 for log loss;
- no class weighting;
- no threshold tuning in this milestone.

The optimizer is deliberately fixed before seeing VALIDATION or DEVELOPMENT_TEST results.

## Required evaluation

For BUY and SELL separately, report on TRAIN, VALIDATION, and DEVELOPMENT_TEST:

- row count;
- positive count / base rate;
- ROC-AUC;
- PR-AUC;
- Brier score;
- log loss;
- 10-bin calibration table;
- predicted-probability quantiles;
- success rate and count for candidate reporting cutoffs 0.20, 0.30, 0.40, 0.50, 0.60.

Candidate cutoffs are descriptive only and are not live trading thresholds.

## Model acceptance interpretation

This milestone does not define a pass/fail trading rule.

The question is whether:
1. discrimination is materially above chance chronologically;
2. probability calibration is usable;
3. higher predicted probability corresponds to materially higher realized success;
4. the relationship survives from TRAIN into VALIDATION and DEVELOPMENT_TEST.

## Governance

- 2025 must not be read or summarized.
- No feature changes, hyperparameter changes, or threshold changes are permitted after seeing the first V1 results without opening a new documented experiment iteration.
- A weak or negative result is admissible.
