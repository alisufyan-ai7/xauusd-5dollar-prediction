# EXP-001 Gradient-Boosted Trees V1 Findings

Status: COMPLETE

Source run: 36307804733

Artifact: exp001-gbt-v1

FINAL_OOS 2025 was not accessed.

## BUY model

TRAIN:
- n: 1,534,406
- base rate: 6.35%
- ROC-AUC: 0.8439
- PR-AUC: 0.2745
- Brier: 0.0518
- log loss: 0.1856

VALIDATION 2022:
- n: 270,169
- base rate: 11.27%
- ROC-AUC: 0.7452
- PR-AUC: 0.2554
- Brier: 0.0918
- log loss: 0.3134

DEVELOPMENT_TEST 2023-2024:
- n: 530,979
- base rate: 12.98%
- ROC-AUC: 0.7378
- PR-AUC: 0.2662
- Brier: 0.1042
- log loss: 0.3463

Top permutation-importance features on VALIDATION:
1. tr_mean_60m
2. minutes_to_session_transition
3. rv_15m
4. rv_240m
5. slope_240m
6. rv_60m
7. compression_expansion_ratio
8. rv_120m

## SELL model

TRAIN:
- n: 1,534,317
- base rate: 7.08%
- ROC-AUC: 0.8415
- PR-AUC: 0.2888
- Brier: 0.0570
- log loss: 0.2007

VALIDATION 2022:
- n: 270,133
- base rate: 11.77%
- ROC-AUC: 0.7407
- PR-AUC: 0.2500
- Brier: 0.0958
- log loss: 0.3240

DEVELOPMENT_TEST 2023-2024:
- n: 530,856
- base rate: 13.26%
- ROC-AUC: 0.7452
- PR-AUC: 0.2805
- Brier: 0.1048
- log loss: 0.3464

Top permutation-importance features on VALIDATION:
1. tr_mean_60m
2. rv_15m
3. minutes_to_session_transition
4. rv_240m
5. compression_expansion_ratio
6. rv_120m
7. current_day_range_position
8. range_position_240m

## Comparison to Logistic V1

GBT V1 materially improves chronological discrimination for both directions.

BUY ROC-AUC:
- Logistic VALIDATION 0.6359 -> GBT 0.7452
- Logistic DEVELOPMENT_TEST 0.6194 -> GBT 0.7378

SELL ROC-AUC:
- Logistic VALIDATION 0.5816 -> GBT 0.7407
- Logistic DEVELOPMENT_TEST 0.5549 -> GBT 0.7452

PR-AUC also improves materially.

## Important calibration observation

The raw GBT probabilities are compressed: no observations reached the descriptive 0.60 cutoff in TRAIN, VALIDATION, or DEVELOPMENT_TEST.

Therefore:
- raw GBT probability values must not be interpreted directly as calibrated trade confidence;
- the next milestone should evaluate calibration and percentile/rank-based abstention on VALIDATION and DEVELOPMENT_TEST;
- no live threshold is selected here.

## Conclusion

1. Nonlinear interactions among V2 features add substantial predictive information over Logistic V1.
2. The signal survives chronologically into 2022 and 2023-2024.
3. BUY and SELL both now show similar useful discrimination.
4. Volatility/attainability and session-transition context dominate feature importance.
5. Probability calibration and abstention research is now justified.
6. 2025 remains sealed.
