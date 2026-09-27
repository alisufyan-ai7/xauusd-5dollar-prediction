# EXP-003 Initial Economic-Value Model V1 Findings

Status: COMPLETE — INITIAL DIAGNOSTICS ONLY

Source run: 36334117385

Artifact: exp003-initial-model

FINAL_OOS 2025 was not accessed.

## Purpose of this run

This run evaluated model calibration and the relationship between predicted EV_F10 and realized executable F10 P&L.

It did NOT run the frozen sequential T0/T25/T50/T75 threshold policies. Therefore this run alone cannot pass or fail EXP-003 advancement.

## BUY

VALIDATION:
- multiclass log loss: 0.7928
- unresolved MAE: 1.2740
- unresolved mean predicted P&L: +0.3485
- unresolved mean realized P&L: +0.2994

DEVELOPMENT_TEST:
- multiclass log loss: 0.8017
- unresolved MAE: 1.2289
- unresolved mean predicted P&L: +0.3235
- unresolved mean realized P&L: +0.3396

DEVELOPMENT_TEST EV_F10:
- median: -0.4666
- 97.5th percentile: -0.0973
- 99th percentile: +0.0206

Frozen threshold raw counts:
- T0: 6,688
- T25: 1,055
- T50: 257
- T75: 76

Highest EV decile realized mean NET_F10:
- -0.4232

## SELL

VALIDATION:
- multiclass log loss: 0.7955
- unresolved MAE: 1.2447
- unresolved mean predicted P&L: +0.1711
- unresolved mean realized P&L: +0.3552

DEVELOPMENT_TEST:
- multiclass log loss: 0.8007
- unresolved MAE: 1.2111
- unresolved mean predicted P&L: +0.1786
- unresolved mean realized P&L: +0.2703

DEVELOPMENT_TEST EV_F10:
- median: -0.4165
- 97.5th percentile: +0.0272
- 99th percentile: +0.1999

Frozen threshold raw counts:
- T0: 16,673
- T25: 4,447
- T50: 1,635
- T75: 760

Highest EV decile realized mean NET_F10:
- -0.4747

## Interpretation

1. Most scored observations have negative predicted EV_F10, as intended for an abstaining system.
2. The unresolved-P&L regression is directionally reasonable in aggregate, but individual error remains material.
3. Broad EV ranking is not monotonic enough to establish economic value from decile diagnostics alone.
4. The highest EV decile remains negative in realized F10 P&L for both BUY and SELL.
5. The preregistered positive-EV thresholds select much smaller subsets than the full top decile. Their sequential economics must be tested exactly as preregistered before EXP-003 can be judged.
6. 2025 remains sealed.
