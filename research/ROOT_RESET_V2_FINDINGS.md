# Root-Reset V2 Joint Excursion Findings

Status: COMPLETE — STOPPED AT VALIDATION

Source run: 36696884026

Artifact:
root-reset-v2-joint-excursion

Artifact digest:
sha256:9298568c1a728a05c4eeddc60637126c45ba5b2bcdf40881aeccf5684d8061e5

DEVELOPMENT_TEST 2023-2024 was not accessed.

FINAL_OOS 2025 was not accessed.

## Core result

No V2 policy qualified on VALIDATION 2022.

Selected policy:
- none

Therefore the workflow correctly stopped before DEVELOPMENT_TEST.

## Excursion model diagnostics

The quantile regressors contain meaningful but moderate signal.

### BUY

MFE q70:
- Pearson: 0.3885
- Spearman: 0.3537
- coverage: 68.07%

MAE q70:
- Pearson: 0.4033
- Spearman: 0.3783
- coverage: 67.44%

### SELL

MFE q70:
- Pearson: 0.4133
- Spearman: 0.3554
- coverage: 68.73%

MAE q70:
- Pearson: 0.4646
- Spearman: 0.4037
- coverage: 69.62%

Interpretation:
joint excursion prediction is materially more informative than prior direct-P&L regression, but not accurate enough to use upper quantiles naively as literal trade targets/stops.

## Validation policy results

### G50-H

- 17 trades
- mean NET_F10: +0.1237
- profit factor: 1.0591
- mean target: $5.7808
- mean stop: $4.4067
- median realized MFE60: $4.966
- 88.2% of targets >= $5

This is the only positive validation policy, but it fails the frozen minimum of 100 validation trades.

### G50-B3

- 17 trades
- mean NET_F10: -0.1290
- profit factor: 0.9175

Moving to protected breakeven at +$3 reduced performance in this tiny G50 sample.

### G70-H

- 66 trades
- mean NET_F10: -1.8413
- profit factor: 0.4468
- mean target: $7.4000
- mean stop: $5.6207
- median realized MFE60: $3.527

### G70-B3

- 67 trades
- mean NET_F10: -1.0678
- profit factor: 0.5494

Breakeven protection improves G70 relative to HOLD but remains materially negative.

### G80-H

- 96 trades
- mean NET_F10: -1.3636
- profit factor: 0.5666
- mean target: $7.9075
- mean stop: $5.9784
- median realized MFE60: $4.078

### G80-B3

- 97 trades
- mean NET_F10: -0.7496
- profit factor: 0.6601

Again B3 reduces losses but does not create positive expectancy.

## Main root-cause finding

V2 fixed the V1 hard-stop rejection problem, but exposed a second geometry problem:

The upper conditional excursion quantiles are useful for ranking, but are too optimistic to be used directly as executable target distances.

Examples:

- G70 average target ~$7.4 while realized median MFE is only ~$3.5.
- G80 average target ~$7.9 while realized median MFE is only ~$4.1.
- stops also widen toward ~$5.6-$6.0.

This causes many trades to hit wide stops or time out before reaching the predicted quantile target.

The quantile models should therefore be treated as state/ranking estimates rather than literal target/stop levels.

## Important secondary finding

G50-H is mildly positive on validation:
- +$0.124 NET_F10
- PF 1.059

but with only 17 trades.

This is not sufficient evidence and must not be promoted.

It does suggest that more conservative excursion geometry may be closer to executable reality.

B3 protection is not universally beneficial:
- it worsens G50;
- it reduces losses for G70/G80.

Therefore +$3 protection is regime/geometry dependent rather than an automatic rule.

## Implication for next design

Do not:
- lower the validation trade-count gate;
- promote G50-H;
- tune G50/G70/G80 post hoc;
- access 2023-2024;
- access 2025.

The next admissible step is a validation-only calibration diagnosis of predicted excursion versus realized executable excursion.

That diagnosis should estimate:
- conditional realized MFE given predicted q50/q70/q80;
- conditional realized MAE given predicted q50/q70/q80;
- shrinkage / calibration mapping from predicted excursion to realized excursion;
- whether target should be based on a calibrated lower-bound or expected attainable excursion rather than raw quantile;
- whether stop should be tied to predicted adverse excursion or structural invalidation separately.

No new trading policy should be run until that calibration diagnosis is frozen and completed.

2025 remains sealed.
