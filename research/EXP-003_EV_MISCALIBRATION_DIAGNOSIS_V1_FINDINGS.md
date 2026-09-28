# EXP-003 EV Miscalibration Diagnosis V1 Findings

Status: COMPLETE

Source run: 36348182305

Artifact: exp003-ev-miscalibration-diagnosis-v1

FINAL_OOS 2025 was not accessed.

## Core diagnosis

EXP-003 positive predicted EV is primarily caused by class-probability miscalibration in the positive-EV tail:

- SUCCESS probability is overpredicted;
- FAILURE probability is underpredicted;
- the error worsens as predicted EV increases.

The unresolved-expiry-P&L regressor is not the dominant source of the optimism gap.

A second major contributor is feature-distribution shift / extrapolation, especially in 2024 and especially for BUY positive-EV tails.

## BUY

### T0

DEVELOPMENT_TEST:
- n = 6,031 complete rows
- predicted mean EV_F10 = +0.1384
- realized mean NET_F10 = -0.4727
- calibration gap = +0.6111

Probability errors:
- P(SUCCESS) overpredicted by +0.0549
- P(FAILURE) underpredicted by -0.0834
- P(UNRESOLVED) overpredicted by +0.0294

Unresolved-P&L prediction error:
- +0.2552

Counterfactual EV_GROSS:
- model EV: +0.2384
- realized class rates + predicted unresolved P&L: -0.2945
- predicted class rates + realized unresolved P&L: +0.1760
- fully realized components: -0.3727

Interpretation:
replacing only the class probabilities with realized frequencies flips the EV strongly negative, while replacing only unresolved P&L still leaves positive modeled EV. Therefore class-probability error dominates.

### Higher BUY EV thresholds

T25:
- predicted EV_F10 +0.4031
- realized NET_F10 -0.4325
- gap +0.8356
- SUCCESS overprediction +0.0854
- FAILURE underprediction -0.1201

T50:
- predicted EV_F10 +0.6687
- realized NET_F10 -0.4019
- gap +1.0705
- SUCCESS overprediction +0.1340
- FAILURE underprediction -0.1089

T75:
- predicted EV_F10 +0.9230
- realized NET_F10 -0.6240
- gap +1.5470
- SUCCESS overprediction +0.2291
- FAILURE underprediction -0.1128

The positive-EV tail becomes progressively more overconfident rather than better calibrated.

## SELL

### T0

DEVELOPMENT_TEST:
- n = 12,868 complete rows
- predicted mean EV_F10 = +0.1531
- realized mean NET_F10 = -0.4472
- calibration gap = +0.6003

Probability errors:
- P(SUCCESS) overpredicted by +0.0516
- P(FAILURE) underpredicted by -0.0958
- P(UNRESOLVED) overpredicted by +0.0442

Unresolved-P&L prediction error:
- +0.0533

Counterfactual EV_GROSS:
- model EV: +0.2531
- realized class rates + predicted unresolved P&L: -0.3332
- predicted class rates + realized unresolved P&L: +0.2201
- fully realized components: -0.3472

Again, the class probabilities—not unresolved-P&L regression—are the dominant source of optimism.

### Higher SELL EV thresholds

T25:
- predicted EV_F10 +0.3999
- realized NET_F10 -0.5318
- gap +0.9318
- SUCCESS overprediction +0.0889
- FAILURE underprediction -0.1463

T50:
- predicted EV_F10 +0.6429
- realized NET_F10 -1.1323
- gap +1.7752
- SUCCESS overprediction +0.1901
- FAILURE underprediction -0.2404

T75:
- predicted EV_F10 +0.8767
- realized NET_F10 -1.0901
- gap +1.9668
- SUCCESS overprediction +0.2565
- FAILURE underprediction -0.2865

SELL tail probability calibration degrades severely as predicted EV rises.

## Temporal drift

BUY T0:
- 2023 predicted EV_F10 +0.1384 vs realized -0.3482; gap +0.4866
- 2024 predicted +0.1382 vs realized -0.6191; gap +0.7573

SELL T0:
- 2023 predicted +0.1550 vs realized -0.3957; gap +0.5507
- 2024 predicted +0.1513 vs realized -0.4946; gap +0.6459

The same model optimism exists in both years, but 2024 is materially worse for BUY and remains worse for SELL.

## Sequential opportunity-level calibration

The raw-row miscalibration survives one-position-at-a-time execution.

T0 BUY_ONLY:
- predicted mean entry EV_F10 +0.0922
- realized mean NET_F10 -0.5337
- gap +0.6259
- 2024 gap +0.7910

T0 SELL_ONLY:
- predicted +0.0914
- realized -0.3898
- gap +0.4812

T0 COMBINED:
- predicted +0.0936
- realized -0.4593
- gap +0.5529

At higher thresholds the opportunity-level gap becomes even larger.

Therefore clustering suppression does not fix the EV miscalibration.

## Feature-distribution shift

Largest normalized median shifts versus TRAIN:

### VALIDATION 2022
Notable shifts already existed in:
- recent_5dollar_range_frequency_240m: +0.75 TRAIN-IQR units
- spread_max_15m: +0.75
- spread_close_1m: +0.74
- spread_mean_5m: +0.68
- spread_mean_60m: +0.67
- tr_mean_60m: +0.61

### DEVELOPMENT_TEST 2023
Shifts were more moderate:
- recent_5dollar_range_frequency_240m: +0.54
- spread_close_1m: +0.42
- rv_240m: +0.38
- tr_mean_60m: +0.37

### DEVELOPMENT_TEST 2024
The distribution shift became much larger:
- recent_5dollar_range_frequency_240m: +1.49
- tr_mean_60m: +1.08
- rv_240m: +1.08
- rv_120m: +1.03
- rv_60m: +0.99
- session_rv_60m: +0.97
- rv_15m: +0.95
- spread_mean_60m: +0.90
- spread_mean_15m: +0.89
- spread_close_1m: +0.89

This supports a genuine market-state distribution-shift explanation, especially for 2024.

## TRAIN-support extrapolation

Positive-EV rows frequently lie outside the TRAIN 1%-99% feature support.

BUY:
- T0: 76.9% have at least one out-of-support feature; median 2
- T25: 92.7%; median 5
- T50: 96.6%; median 6
- T75: 92.7%; median 6

SELL:
- T0: 62.6%; median 1
- T25: 67.4%; median 2
- T50: 76.5%; median 2
- T75: 78.9%; median 2

The BUY positive-EV tail is particularly dominated by extrapolative market states.

## Conclusion

The dominant measured EXP-003 failure mechanisms are:

1. **class-probability tail miscalibration**:
   - SUCCESS is overpredicted;
   - FAILURE is underpredicted;
   - the error worsens as predicted EV increases;

2. **distribution shift / extrapolation**:
   - 2024 volatility, attainability, and spread states are materially shifted from TRAIN;
   - positive-EV tails frequently occur outside TRAIN feature support;

3. **not primarily unresolved-P&L regression**:
   - substituting realized unresolved P&L alone does not remove the positive modeled EV;
   - substituting realized class frequencies does.

4. **not solved by opportunity-level suppression**:
   - the same optimism persists in actual sequential entries.

This means a future EXP-004 should not merely change the EV threshold. Any new experiment must explicitly address:
- probability calibration under temporal shift;
- extrapolation / out-of-support uncertainty;
- and/or a model objective that penalizes tail miscalibration more directly.

No EXP-004 specification is created by this diagnostic.

2025 remains sealed.
