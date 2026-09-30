# Root-Reset V2 Excursion Calibration Diagnosis Findings

Status: COMPLETE

Source run: 36700831693

Artifact:
root-reset-v2-excursion-calibration-diagnosis

Artifact digest:
sha256:319b28bff8037ee7ec38b197884b21bc8c4a9af5890871f1766e3c70406de196

Scope:
- TRAIN 2016-2021 used for frozen-model fitting;
- VALIDATION 2022 used for diagnosis;
- DEVELOPMENT_TEST 2023-2024 NOT accessed;
- FINAL_OOS 2025 NOT accessed.

## Core finding

The dominant V2 calibration problem is reward overprediction, not risk underprediction.

Raw MFE q70/q80 predictions are useful rankers but require substantial shrinkage before they resemble realized executable favorable excursion.

Predicted MAE q50 is comparatively well calibrated and is a better risk anchor than structural invalidation distance.

## BUY

### MFE q70

- Pearson: 0.3904
- Spearman: 0.3577
- coverage: 68.26%

Validation shrinkage factors derived from decile median calibration:

- S50: 0.6091
- S25: 0.5884
- S10: 0.5393

Using S50:
- realized hit rate of calibrated target: 49.70%
- median realized minus calibrated target: -$0.014

Using S25:
- realized hit rate: 50.85%
- median realized minus calibrated target: +$0.033

Using S10:
- realized hit rate: 53.51%
- median realized minus calibrated target: +$0.154

Interpretation:
a q70 prediction must be shrunk by roughly 40-46% to behave like a median-attainable executable target.

### MFE q80

Shrinkage:
- S50: 0.4474
- S25: 0.4325
- S10: 0.4162

Again the raw upper quantile is substantially too optimistic as a literal target distance.

### Risk anchors

Predicted MAE q50:
- median anchor: $2.244
- realized MAE median / anchor median: 1.028
- Pearson with realized MAE: 0.423
- Spearman: 0.381
- 60m stop-hit rate: 52.02%

Predicted MAE q70:
- median: $3.189
- realized/anchor median ratio: 0.723
- stop-hit rate: 32.82%

Structure invalidation:
- median: $3.187
- realized/anchor median ratio: 0.724
- Pearson with realized MAE: 0.386
- Spearman: 0.344
- stop-hit rate: 33.25%

Conclusion:
MAE q50 is the closest to realized median adverse excursion and ranks adverse excursion better than structure distance.

## SELL

### MFE q70

- Pearson: 0.4137
- Spearman: 0.3529
- coverage: 68.96%

Shrinkage:
- S50: 0.5658
- S25: 0.5412
- S10: 0.5351

Using S50:
- realized hit rate: 51.39%
- median realized minus calibrated target: +$0.052

Using S25:
- realized hit rate: 52.89%
- median realized minus calibrated target: +$0.114

Using S10:
- realized hit rate: 53.25%
- median realized minus calibrated target: +$0.129

### MFE q80

Shrinkage:
- S50: 0.4188
- S25: 0.3981
- S10: 0.3883

### Risk anchors

Predicted MAE q50:
- median: $2.304
- realized MAE median / anchor median: 0.988
- Pearson: 0.473
- Spearman: 0.402
- stop-hit rate: 49.74%

Predicted MAE q70:
- median: $3.226
- realized/anchor ratio: 0.706
- stop-hit rate: 30.77%

Structure invalidation:
- median: $3.180
- realized/anchor ratio: 0.716
- Pearson: 0.443
- Spearman: 0.376
- stop-hit rate: 30.71%

Conclusion:
again, predicted MAE q50 is the best-calibrated central adverse-excursion anchor.

## Reward/risk after calibration

Even after conservative MFE q70 calibration, candidate-level reward/risk remains weak across the full validation event population.

Using calibrated MFE q70 / predicted MAE q50:

BUY median reward/risk:
- S10: 0.579
- S25: 0.631
- S50: 0.654

SELL median reward/risk:
- S10: 0.591
- S25: 0.597
- S50: 0.625

Using structure invalidation as denominator is worse:
- BUY median RR roughly 0.40-0.45
- SELL roughly 0.42-0.44

This is the most important economic diagnosis.

The continuation event population as a whole has typical attainable favorable excursion smaller than typical adverse excursion.

## Root-cause conclusion

The continuation event sampler can rank large-move states, and excursion models can estimate both MFE and MAE with moderate signal.

However:

1. raw upper favorable-excursion quantiles overstate executable reward;
2. calibrated favorable excursion is much smaller than raw q70/q80;
3. central adverse excursion is already estimated reasonably well by MAE q50;
4. after honest calibration, typical reward/risk remains below 1;
5. structural invalidation is not superior to MAE q50 as a risk anchor.

Therefore the remaining problem is not primarily target calibration or stop construction.

It is entry/setup quality.

The current continuation-event family often experiences adverse excursion comparable to or larger than attainable favorable excursion before/within the 60-minute horizon.

## Governance implication

Do not:
- define a V3 by simply multiplying q70 by a shrinkage factor;
- lower reward/risk gates to force trades;
- use structure stops in place of MAE q50 merely because they are wider;
- access 2023-2024;
- access 2025.

The current continuation setup lineage should be considered exhausted unless a separately preregistered setup family or genuinely new timestamp-safe information source changes the entry population.

Potential next research directions:
- a different mechanically defined setup family such as breakout-retest, sweep-reclaim, or impulse-pullback;
- timestamp-safe macro/session/cross-market context applied before candidate generation;
- or both.

2025 remains sealed.
