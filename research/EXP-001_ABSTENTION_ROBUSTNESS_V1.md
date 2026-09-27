# EXP-001 Abstention Robustness Milestone V1

Status: FROZEN BEFORE EXECUTION

## Purpose

Test whether the already-observed GBT V1 score-ranking edge remains stable when the fixed VALIDATION-derived abstention policies are examined across time, session, volatility regime, and overlapping-observation-aware uncertainty.

This milestone does not change:
- labels;
- V2 features;
- GBT hyperparameters;
- TRAIN thinning rule;
- calibration method;
- chronological partitions.

FINAL_OOS 2025 remains strictly sealed.

## Frozen model reproduction

Reproduce GBT V1 exactly for BUY and SELL:
- HistGradientBoostingClassifier
- learning_rate 0.05
- max_iter 200
- max_leaf_nodes 15
- max_depth null
- min_samples_leaf 200
- l2_regularization 1.0
- max_bins 255
- early_stopping false
- random_state 1
- every 5th eligible TRAIN row in chronological order

## Frozen candidate policies

Derive raw-score cutoffs on VALIDATION only for:
- top 10%;
- top 5%;
- top 2.5%;
- top 1%.

Apply each cutoff unchanged to DEVELOPMENT_TEST.

No new percentile bands may be added after results.

## Primary robustness population

DEVELOPMENT_TEST 2023-2024 only.

VALIDATION is used only to reproduce the already-defined score cutoffs.

## Time-block robustness

For each direction and fixed candidate policy, report on DEVELOPMENT_TEST:
- calendar year 2023;
- calendar year 2024;
- each calendar quarter from 2023-Q1 through 2024-Q4.

For every block:
- selected row count;
- opportunity share;
- realized success rate;
- unconditional success rate in the same block;
- lift = selected success rate / unconditional success rate.

## Session robustness

Using the existing V2 session_utc field, report the same metrics for:
- ASIA;
- EUROPE;
- US;
- LATE.

No session-specific threshold tuning.

## Volatility-regime robustness

Compute rv_60m tertiles from TRAIN only using all eligible TRAIN rows.

Freeze regimes:
- LOW <= TRAIN q33;
- MID > q33 and <= q67;
- HIGH > q67.

Apply those fixed thresholds to DEVELOPMENT_TEST and report the same metrics for each candidate policy.

## Overlapping-observation-aware uncertainty

M1 observations overlap heavily because labels use a 60-minute forward horizon.

For each direction and policy on DEVELOPMENT_TEST:
1. group selected rows by UTC calendar day;
2. aggregate selected successes and selected non-ambiguous observations per day;
3. bootstrap whole UTC days with replacement;
4. use 1,000 deterministic bootstrap replicates with random seed 1;
5. compute percentile 95% interval for selected success rate.

Also bootstrap the same-day unconditional population and report the 95% interval for lift using paired day resampling.

The daily block is frozen before results and is intended to preserve substantial within-day dependence rather than treating M1 rows as independent Bernoulli trials.

## Stability flags

For each policy and direction report descriptive flags:
- all_years_above_unconditional;
- at_least_6_of_8_quarters_above_unconditional;
- all_sessions_above_unconditional;
- all_volatility_regimes_above_unconditional;
- bootstrap_lift_ci_lower_gt_1.

These are descriptive robustness summaries, not a live trading acceptance gate.

## Governance

- 2025 must not be read, summarized, or used.
- No candidate policy is selected for production in this milestone.
- No threshold, feature, model parameter, regime boundary, or bootstrap design may be changed after results without a new documented iteration.
- A negative robustness result is admissible.
