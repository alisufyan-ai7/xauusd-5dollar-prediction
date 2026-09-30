# Root-Reset V3 Structural Setup Family Screening Findings

Status: COMPLETE — NO FAMILY ELIGIBLE

Source run: 36711334369

Artifact:
root-reset-v3-setup-screening

Artifact digest:
sha256:b0de2c3f2e085012f085008cf9223b1c6cd905650e0a723ea16cd5956b421951

Scope:
- synchronized Dukascopy XAUUSD M1 BID/ASK;
- 2016-2021 only;
- no model fitting;
- no 2022-2025 access.

Selected family:
- none

## Core result

None of the three preregistered structural setup families produced a stable positive path edge.

All three had:
- negative overall median MFE60 - MAE60;
- zero positive YEAR_PATH_EDGE years out of six;
- median MFE60 materially below median MAE60;
- overall median MFE60 / median MAE60 well below the frozen 1.10 requirement.

Therefore no family is eligible for 2022 validation.

## A — Breakout-Retest Continuation

Candidates:
- 21,829
- BUY: 10,893
- SELL: 10,936

Overall:
- median MFE60: $0.880
- median MAE60: $1.560
- median MFE/median MAE: 0.564
- mean MFE60: $1.685
- mean MAE60: $2.256
- +$3 rate: 16.33%
- +$5 rate: 7.00%
- +$5-before-$3 rate: 6.09%
- overall YEAR_PATH_EDGE: -$0.691

Year stability:
- positive YEAR_PATH_EDGE years: 0 / 6
- median yearly edge: -$0.677
- minimum yearly edge: -$1.126

Conclusion:
breakout-retest continuation is decisively adverse-dominant under the frozen definition.

## B — Sweep-Reclaim Reversal

Candidates:
- 9,792
- BUY: 4,945
- SELL: 4,847

Overall:
- median MFE60: $0.953
- median MAE60: $1.555
- median MFE/median MAE: 0.613
- mean MFE60: $1.666
- mean MAE60: $2.442
- +$3 rate: 16.29%
- +$5 rate: 6.68%
- +$5-before-$3 rate: 5.41%
- overall YEAR_PATH_EDGE: -$0.604

Year stability:
- positive YEAR_PATH_EDGE years: 0 / 6
- median yearly edge: -$0.641
- minimum yearly edge: -$0.861

Conclusion:
sweep-reclaim reversal is also adverse-dominant and does not show stable path superiority.

## C — Impulse-Pullback Continuation

Candidates:
- 2,018
- BUY: 945
- SELL: 1,073

Overall:
- median MFE60: $1.018
- median MAE60: $1.584
- median MFE/median MAE: 0.643
- mean MFE60: $2.059
- mean MAE60: $2.310
- +$3 rate: 19.62%
- +$5 rate: 9.66%
- +$5-before-$3 rate: 8.03%
- overall YEAR_PATH_EDGE: -$0.4995

Year stability:
- positive YEAR_PATH_EDGE years: 0 / 6
- median yearly edge: -$0.504
- minimum yearly edge: -$0.832

This is the least-bad of the three families, but it still fails every path-edge stability criterion.

Even in 2020, when +$5 hits were much more frequent:
- +$5 rate: 25.66%
- +$5-before-$3 rate: 19.17%
- YEAR_PATH_EDGE: -$0.794

Conclusion:
impulse-pullback continuation does not provide a defensible price-only edge under the frozen mechanics.

## Root-cause conclusion

This screening materially strengthens the conclusion from the earlier reset work.

The failure is not confined to:
- minute-by-minute sampling;
- fixed +$5/-$3 labels;
- stop construction;
- target calibration;
- generic continuation events.

Three distinct mechanically defined price-action families also show adverse excursion dominating favorable excursion across every TRAIN year.

Therefore continuing to invent more price-only patterns is not justified.

## Governance decision

Do not:
- promote any V3 setup family;
- access 2022 validation;
- tweak pattern thresholds post hoc;
- add more price-only setup families;
- access 2023-2025.

The next admissible research step must introduce genuinely new timestamp-safe information before or at candidate generation.

Priority should be:
1. scheduled macro-event context;
2. session/liquidity context;
3. public cross-market context such as USD/rates only if timestamp-safe and reproducible.

A new milestone should first establish data availability, timestamp integrity, licensing/reproducibility, and causal alignment before any profitability test.

2022-2025 remain untouched.
