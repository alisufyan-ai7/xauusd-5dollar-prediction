# EXP-007 Causal Sequence Model V1 Findings

Status: COMPLETE — NO POLICY PASSES

Source run: 36485293055

Artifact: exp007-causal-sequence-v1

Artifact digest:
sha256:54bd2143bf752937287510c6b254cea3c476d7b41ac725e9c27dc5817339a304

FINAL_OOS 2025 was not accessed.

## Core result

No EXP-007 sequence-model policy passed the frozen advancement rule.

Passing policies:
- none

## Predictive diagnostics

### BUY

DEVELOPMENT_TEST:
- direct-P&L Pearson: -0.0269
- MAE: 2.2444
- RMSE: 2.7176
- mean predicted gross P&L: -0.3915
- mean realized gross P&L: -0.3397

EARLY_FAILURE:
- base rate: 4.55%
- ROC-AUC: 0.8883
- PR-AUC: 0.4249
- Brier: 0.0330

The BUY direct regressor shows a severe positive-tail failure:
- >= +0.75 DIRECT_NET_F10 band: 1,846 rows
- mean predicted gross P&L: +4.9901
- mean realized gross P&L: -2.9558

This is catastrophic tail miscalibration.

### SELL

DEVELOPMENT_TEST:
- direct-P&L Pearson: +0.0667
- MAE: 2.2310
- RMSE: 2.6752
- mean predicted gross P&L: -0.2909
- mean realized gross P&L: -0.3921

EARLY_FAILURE:
- base rate: 4.27%
- ROC-AUC: 0.8835
- PR-AUC: 0.4211
- Brier: 0.0312

SELL direct-P&L correlation improved modestly versus prior tree experiments, but remains too weak for robust economic use.

## Sequential economics

### A_SEQ_DIRECT_ONLY — T0

BUY_ONLY:
- 1,780 trades
- mean NET_F10: -3.0200
- profit factor: 0.0136
- 2023: -3.0300
- 2024: -2.9988
- bootstrap 95% CI: [-3.0694, -1.2862]

SELL_ONLY:
- 637 trades
- mean NET_F10: -0.2913
- profit factor: 0.8490
- 2023: +0.0023
- 2024: -0.4367
- bootstrap 95% CI: [-0.5687, -0.0215]

COMBINED:
- 2,394 trades
- mean NET_F10: -2.3099
- profit factor: 0.1650
- 2023: -2.6025
- 2024: -1.8941
- bootstrap 95% CI: [-2.6959, -0.3839]

### Higher direct-score thresholds

BUY remains catastrophically negative because the sequence regressor's positive tail is miscalibrated.

Examples:
- T25 BUY_ONLY: mean NET_F10 -3.0987
- T50 BUY_ONLY: mean NET_F10 -3.0987
- T75 BUY_ONLY: mean NET_F10 -3.0987

SELL higher-score variants are sparse and still fail frozen year/trade-count/uncertainty gates.

### EARLY_FAILURE-gated arms

The Q50/Q25/Q10 gates collapse the sequence opportunity set to tiny samples and do not rescue economics.

Q50 T0:
- BUY_ONLY: 7 trades, mean NET_F10 -1.0200
- SELL_ONLY: 5 trades, -1.0248
- COMBINED: 12 trades, -1.0220

Q25/Q10 are even sparser and remain negative.

## Main interpretation

EXP-007 answers the sequence-model question negatively.

1. A small temporal CNN can rank <=5-minute EARLY_FAILURE very well.
2. It does not produce reliable executable-P&L prediction.
3. BUY direct-P&L tail behavior is severely miscalibrated and saturates near the +5 clip while realizing near -3.
4. SELL direct-P&L correlation improves modestly but is still insufficient.
5. Downside gating removes many dangerous states but leaves too few opportunities and does not create positive robust economics.

The result does not justify architecture tuning within EXP-007.

No EXP-007 candidate should advance.

Do not:
- open 2025;
- reduce epochs or alter architecture after seeing this result;
- add dropout/attention/recurrent layers post hoc;
- clip BUY predictions differently;
- cherry-pick SELL-only sparse subsets;
- proceed to Exness demo/live.

## Next implication

After tree models, enriched path features, and a small sequence model all fail to predict executable trade quality while repeatedly succeeding at rapid-downside classification, the remaining research should change the target/information problem itself.

A future experiment should test one of:
- explicit target-before-adverse competing-hazard modeling rather than direct P&L regression;
- timestamp-safe exogenous event/session context;
- or a two-stage setup model that first predicts attainable directional opportunity and separately applies the strong downside-risk model.

2025 remains sealed.
