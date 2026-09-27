# EXP-002 Initial Executable-Target GBT V1 Findings

Status: COMPLETE

Source run: 36321788362

Artifact: exp002-initial-model

FINAL_OOS 2025 was not accessed.

## BUY

VALIDATION:
- base success rate: 9.30%
- ROC-AUC: 0.7549
- PR-AUC: 0.2225
- top 10% success: 26.14%
- top 5% success: 28.98%
- top 2.5% success: 30.66%
- top 1% success: 31.96%

DEVELOPMENT_TEST:
- base success rate: 11.01%
- ROC-AUC: 0.7392
- PR-AUC: 0.2315
- top 10% success: 27.21%
- top 5% success: 28.87%
- top 2.5% success: 29.92%
- top 1% success: 29.05%

## SELL

VALIDATION:
- base success rate: 9.72%
- ROC-AUC: 0.7476
- PR-AUC: 0.2181
- top 10% success: 25.59%
- top 5% success: 27.72%
- top 2.5% success: 28.57%
- top 1% success: 30.74%

DEVELOPMENT_TEST:
- base success rate: 11.24%
- ROC-AUC: 0.7482
- PR-AUC: 0.2454
- top 10% success: 28.45%
- top 5% success: 30.15%
- top 2.5% success: 31.32%
- top 1% success: 33.07%

## Label characteristics

DEVELOPMENT_TEST complete-path rows:

BUY:
- SUCCESS: 58,645
- FAILURE: 188,551
- UNRESOLVED: 285,341
- AMBIGUOUS: 323

SELL:
- SUCCESS: 59,837
- FAILURE: 192,246
- UNRESOLVED: 280,353
- AMBIGUOUS: 424

AMBIGUOUS frequency is small, so tick adjudication is unlikely to dominate the result.

## Interpretation

1. The executable-side target retains substantial chronological ranking signal.
2. SELL is stronger than BUY at the extreme tail in DEVELOPMENT_TEST.
3. BUY top-1% is not monotonic relative to top-2.5%, so score-tail behavior is not uniformly ordered.
4. Predictive signal alone is not enough for advancement. The next required milestone is sequential execution economics using the executable entry/barrier/expiry semantics already frozen in EXP-002.
5. 2025 remains sealed.
