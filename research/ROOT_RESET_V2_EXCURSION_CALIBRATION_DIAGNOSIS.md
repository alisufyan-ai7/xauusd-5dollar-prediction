# Root-Reset V2 Excursion Calibration Diagnosis

Status: FROZEN BEFORE DIAGNOSTIC RESULTS

## Scope

Use only:
- TRAIN 2016-2021 for fitting the already-frozen V2 models;
- VALIDATION 2022 for diagnosis.

Do NOT access:
- DEVELOPMENT_TEST 2023-2024;
- FINAL_OOS 2025.

## Purpose

Root-Reset V2 showed that MFE/MAE quantile models contain useful ranking signal but raw q70/q80
predictions are too optimistic to be used literally as target/stop distances.

This diagnosis measures the mapping from predicted excursion to realized executable excursion
without changing any V2 trading policy.

## Frozen model reuse

Reuse Root-Reset V2 exactly:
- same event sampler;
- same BASE48 inputs;
- same BUY/SELL separation;
- same MFE q50/q70/q80 models;
- same MAE q50/q70/q80 models;
- same training years and hyperparameters.

No refitting rule, hyperparameter, feature, event detector, target, or quantile may change.

## Required diagnostics

For BUY and SELL separately, and for each of:
- MFE q50
- MFE q70
- MFE q80
- MAE q50
- MAE q70
- MAE q80

report:

1. predicted quantiles:
   - p01, p05, p10, p25, p50, p75, p90, p95, p99, max

2. realized excursion conditional on predicted decile:
   - count
   - predicted mean
   - predicted median
   - realized mean
   - realized median
   - realized p25
   - realized p50
   - realized p75

3. calibration ratio by decile:
   - realized median / predicted median
   - realized mean / predicted mean

4. absolute calibration error:
   - predicted median minus realized median
   - predicted mean minus realized mean

5. monotonicity:
   - Pearson
   - Spearman

6. quantile coverage:
   - share realized <= predicted q

## Conservative calibration candidates

For MFE q70 and q80 separately, compute validation-only shrinkage candidates:

- S50 = median over deciles of realized_median / predicted_median
- S25 = 25th percentile over deciles of realized_median / predicted_median
- S10 = 10th percentile over deciles of realized_median / predicted_median

Apply each shrinkage factor to raw predicted excursion and report:
- predicted calibrated target distribution
- realized hit rate of calibrated target
- mean realized overshoot / shortfall relative to calibrated target

These are diagnostic candidates only.

## Risk-anchor comparison

Compare three risk anchors on validation events:

A. raw predicted MAE q50
B. raw predicted MAE q70
C. structural invalidation distance from Root-Reset V1:
   trailing 15-minute structure invalidation + 0.25 * ATR15_PROXY

For each anchor report:
- median / p75 / p90 distance
- realized stop-hit rate within 60 minutes
- realized MFE conditional on stop not being hit first
- correlation with realized MAE
- ratio of realized MAE median to anchor median

Also compare candidate-specific reward/risk using:
- calibrated MFE candidate / MAE q50
- calibrated MFE candidate / structural invalidation distance

No trading policy is authorized by this diagnosis.

## Interpretation rule

The diagnosis may support one or more of:

1. use shrinkage-calibrated MFE as the target basis;
2. use structural invalidation rather than predicted MAE as the stop basis;
3. use predicted MAE only as a veto / uncertainty signal, not literal stop;
4. abandon excursion geometry if calibration remains too unstable.

No V3 policy may be specified until these findings are recorded.

2023-2024 and 2025 remain untouched.
