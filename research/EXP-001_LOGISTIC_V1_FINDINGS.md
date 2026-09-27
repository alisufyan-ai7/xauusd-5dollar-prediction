# EXP-001 Logistic Regression V1 Findings

Status: COMPLETE

Source run: 36268335102

Artifact: exp001-logistic-v1

FINAL_OOS 2025 was not accessed.

## BUY model

TRAIN:
- n: 1,534,406
- base rate: 6.35%
- ROC-AUC: 0.6826
- PR-AUC: 0.1580

VALIDATION 2022:
- n: 270,169
- base rate: 11.27%
- ROC-AUC: 0.6359
- PR-AUC: 0.1917

DEVELOPMENT_TEST 2023-2024:
- n: 530,979
- base rate: 12.98%
- ROC-AUC: 0.6194
- PR-AUC: 0.2022

Predicted-probability cutoffs retained monotonic realized success:
- VALIDATION >=0.20: 20.68%; >=0.40: 22.49%; >=0.60: 23.79%
- DEVELOPMENT_TEST >=0.20: 21.90%; >=0.40: 23.48%; >=0.60: 24.55%

Interpretation:
BUY contains meaningful chronological signal and probability ranking, but discrimination weakens from TRAIN to VALIDATION to DEVELOPMENT_TEST. This indicates regime drift and/or model underfit/miscalibration.

## SELL model

TRAIN:
- n: 1,534,317
- base rate: 7.08%
- ROC-AUC: 0.5787
- PR-AUC: 0.1354

VALIDATION 2022:
- n: 270,133
- base rate: 11.77%
- ROC-AUC: 0.5816
- PR-AUC: 0.1786

DEVELOPMENT_TEST 2023-2024:
- n: 530,856
- base rate: 13.26%
- ROC-AUC: 0.5549
- PR-AUC: 0.1890

Predicted-probability cutoffs also retained monotonic realized success:
- VALIDATION >=0.20: 22.91%; >=0.40: 24.63%; >=0.60: 25.42%
- DEVELOPMENT_TEST >=0.20: 23.16%; >=0.40: 24.86%; >=0.60: 26.30%

Interpretation:
SELL ranking discrimination is weak, especially in DEVELOPMENT_TEST, but the high-score tail still shows materially higher realized success than the unconditional base rate.

## Cross-direction conclusion

1. V2 features contain real predictive information.
2. BUY generalizes materially better than SELL under a linear logistic model.
3. Higher predicted probability corresponds to higher realized success for both directions.
4. Absolute calibration is poor across time because base rates changed materially and log loss/Brier deteriorated chronologically.
5. The fixed linear model is likely too simple for interactions between volatility, session, location, and directional structure.
6. These results justify the preregistered next model class: gradient-boosted trees.
7. No live threshold is selected here.
8. 2025 remains sealed.
