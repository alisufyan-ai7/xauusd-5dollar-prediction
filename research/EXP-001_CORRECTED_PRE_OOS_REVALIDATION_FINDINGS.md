# EXP-001 Corrected Pre-OOS Revalidation Findings

Status: COMPLETE

Source run: 36311818762

Artifact: exp001-pre-oos-corrected-revalidation

FINAL_OOS 2025 was not accessed.

## Corrected GBT discrimination

BUY:
- VALIDATION ROC-AUC: 0.7486
- DEVELOPMENT_TEST ROC-AUC: 0.7360
- DEVELOPMENT_TEST PR-AUC: 0.2659

SELL:
- VALIDATION ROC-AUC: 0.7406
- DEVELOPMENT_TEST ROC-AUC: 0.7455
- DEVELOPMENT_TEST PR-AUC: 0.2843

The label-correctness repairs did not remove the nonlinear predictive ranking edge.

## Corrected abstention transfer

BUY:
- top 10%: VALIDATION 30.92%, DEVELOPMENT_TEST 30.97%
- top 5%: VALIDATION 33.69%, DEVELOPMENT_TEST 33.95%
- top 2.5%: VALIDATION 34.96%, DEVELOPMENT_TEST 34.22%
- top 1%: VALIDATION 37.80%, DEVELOPMENT_TEST 34.38%

SELL:
- top 10%: VALIDATION 29.79%, DEVELOPMENT_TEST 33.08%
- top 5%: VALIDATION 32.31%, DEVELOPMENT_TEST 35.49%
- top 2.5%: VALIDATION 33.41%, DEVELOPMENT_TEST 37.04%
- top 1%: VALIDATION 35.24%, DEVELOPMENT_TEST 38.46%

## Corrected robustness

BUY:
- top 10% lift: 2.376x; bootstrap 95% CI [2.244, 2.529]
- top 5% lift: 2.604x; CI [2.437, 2.792]
- top 2.5% lift: 2.625x; CI [2.426, 2.840]
- top 1% lift: 2.637x; CI [2.380, 2.908]

SELL:
- top 10% lift: 2.485x; bootstrap 95% CI [2.336, 2.636]
- top 5% lift: 2.666x; CI [2.491, 2.847]
- top 2.5% lift: 2.783x; CI [2.580, 2.996]
- top 1% lift: 2.890x; CI [2.605, 3.178]

All candidate policies remained above unconditional performance in both years and at least 6 of 8 quarters.

## Interpretation

1. The corrected contiguous-horizon label semantics preserve the core predictive ranking evidence.
2. SELL top-1% now exceeds the simple 37.5% +5/-3 break-even hit-rate benchmark before costs, but this is not yet a profitability conclusion.
3. BUY top-1% remains below 37.5%, but unresolved trades are not necessarily full -$3 losses.
4. Therefore the next required milestone is deterministic execution-economics testing with frozen expiry and cost semantics on non-sealed data.
5. 2025 remains sealed.
