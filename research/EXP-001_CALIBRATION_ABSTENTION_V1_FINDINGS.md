# EXP-001 Calibration and Abstention V1 Findings

Status: COMPLETE

Source run: 36308557202

Artifact: exp001-calibration-abstention-v1

FINAL_OOS 2025 was not accessed.

## Calibration

### BUY

VALIDATION:
- raw Brier: 0.091847
- calibrated Brier: 0.091761
- raw log loss: 0.313442
- calibrated log loss: 0.312894

DEVELOPMENT_TEST:
- raw Brier: 0.104214
- calibrated Brier: 0.103970
- raw log loss: 0.346317
- calibrated log loss: 0.344930

Interpretation:
Platt calibration improves BUY probability quality modestly both in-sample on VALIDATION and out-of-time on DEVELOPMENT_TEST.

### SELL

VALIDATION:
- raw Brier: 0.095837
- calibrated Brier: 0.095778
- raw log loss: 0.324005
- calibrated log loss: 0.323909

DEVELOPMENT_TEST:
- raw Brier: 0.104843
- calibrated Brier: 0.104896
- raw log loss: 0.346380
- calibrated log loss: 0.346551

Interpretation:
SELL calibration is essentially neutral on VALIDATION and slightly worse out-of-time. The raw GBT score ranking is more useful than calibrated SELL probabilities.

## Validation-derived abstention bands

### BUY

Fixed score cutoffs derived on VALIDATION transferred strongly to DEVELOPMENT_TEST:

- top 50%: VALIDATION 18.14%, DEVELOPMENT_TEST 19.83%
- top 30%: VALIDATION 23.34%, DEVELOPMENT_TEST 24.40%
- top 20%: VALIDATION 26.97%, DEVELOPMENT_TEST 27.21%
- top 10%: VALIDATION 30.96%, DEVELOPMENT_TEST 30.84%
- top 5%: VALIDATION 33.42%, DEVELOPMENT_TEST 33.40%
- top 2.5%: VALIDATION 34.54%, DEVELOPMENT_TEST 34.37%
- top 1%: VALIDATION 36.38%, DEVELOPMENT_TEST 35.81%

The realized success rate increased monotonically with selectivity in both VALIDATION and DEVELOPMENT_TEST.

The transfer is especially stable at:
- top 5% absolute success-rate difference: 0.02 percentage points;
- top 2.5% difference: 0.17 percentage points;
- top 1% difference: 0.57 percentage points.

### SELL

- top 50%: VALIDATION 19.04%, DEVELOPMENT_TEST 20.70%
- top 30%: VALIDATION 23.85%, DEVELOPMENT_TEST 25.18%
- top 20%: VALIDATION 26.86%, DEVELOPMENT_TEST 28.63%
- top 10%: VALIDATION 29.62%, DEVELOPMENT_TEST 32.77%
- top 5%: VALIDATION 32.16%, DEVELOPMENT_TEST 34.58%
- top 2.5%: VALIDATION 32.54%, DEVELOPMENT_TEST 35.72%
- top 1%: VALIDATION 31.79%, DEVELOPMENT_TEST 36.97%

SELL is monotonic in DEVELOPMENT_TEST but not perfectly monotonic in VALIDATION at the extreme tail. Nevertheless, fixed validation-derived thresholds transfer with materially higher success rates in DEVELOPMENT_TEST.

## Main conclusion

1. GBT score ranking is robust enough to support abstention research.
2. BUY score bands are especially stable across 2022 -> 2023-2024.
3. SELL score bands are useful but less orderly in the validation extreme tail.
4. Platt calibration is modestly beneficial for BUY and not beneficial for SELL out-of-time.
5. Raw/calibrated probability should not yet be treated as literal live confidence.
6. The next milestone should freeze one or more candidate abstention policies for robustness testing rather than continue model tuning.
7. 2025 remains sealed.
