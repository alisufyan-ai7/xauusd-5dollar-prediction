# EXP-005 Downside-First Direct Economic Model V1 Findings

Status: COMPLETE — NO POLICY PASSES

Source run: 36445233132

Artifact: exp005-downside-first-direct-v1

FINAL_OOS 2025 was not accessed.

## Core result

No preregistered EXP-005 arm / threshold / mode combination passed the frozen advancement rule.

Passing policies:
- none

## Predictive diagnostics

### BUY

DEVELOPMENT_TEST direct regressor:
- MAE: 2.2364
- RMSE: 2.6886
- mean predicted gross P&L: -0.3949
- mean realized gross P&L: -0.3346
- Pearson correlation: 0.0217

DEVELOPMENT_TEST early-failure classifier:
- base EARLY_FAILURE rate: 4.29%
- ROC-AUC: 0.8369
- PR-AUC: 0.2506
- Brier: 0.0359

2023 early-failure ROC-AUC:
- 0.8180

2024 early-failure ROC-AUC:
- 0.8292

### SELL

DEVELOPMENT_TEST direct regressor:
- MAE: 2.2382
- RMSE: 2.6874
- mean predicted gross P&L: -0.3339
- mean realized gross P&L: -0.3800
- Pearson correlation: 0.0247

DEVELOPMENT_TEST early-failure classifier:
- base EARLY_FAILURE rate: 4.01%
- ROC-AUC: 0.8102
- PR-AUC: 0.2265
- Brier: 0.0343

2023 early-failure ROC-AUC:
- 0.7829

2024 early-failure ROC-AUC:
- 0.8066

Interpretation:
the EARLY_FAILURE classifier has meaningful ranking discrimination, but the direct gross-P&L regressor has almost no linear predictive relationship with realized gross P&L.

## ARM A — DIRECT_ONLY

### T0

BUY_ONLY:
- trades: 864
- mean NET_F10: -0.3519
- profit factor: 0.8093
- 2023: -0.1903
- 2024: -0.4635
- bootstrap 95% CI: [-0.5741, -0.1326]

SELL_ONLY:
- trades: 1,916
- mean NET_F10: -0.4438
- profit factor: 0.7611
- 2023: -0.4178
- 2024: -0.4536
- bootstrap 95% CI: [-0.6020, -0.2729]

COMBINED:
- trades: 2,668
- mean NET_F10: -0.4371
- profit factor: 0.7650
- 2023: -0.3362
- 2024: -0.4832
- bootstrap 95% CI: [-0.5713, -0.3007]

### Higher direct-score thresholds

T25:
- BUY_ONLY: -0.2972
- SELL_ONLY: -0.2881
- COMBINED: -0.2929

2023 improves for SELL/COMBINED, but 2024 remains materially negative.

T50:
- BUY_ONLY: -0.0695
- SELL_ONLY: -0.0786
- COMBINED: -0.0772

These are closer to breakeven, but trade counts are below frozen minimums and 2024 remains negative.

T75:
- sparse and still not robust.

## ARM B — DIRECT_EF_Q50

The Q50 early-failure gate removes all observed <=5-minute early failures from executed trades, but economics remain poor and samples become very small.

T0:
- BUY_ONLY: 13 trades, +0.1272 NET_F10
- SELL_ONLY: 82 trades, -0.8837
- COMBINED: 94 trades, -0.7217

BUY T0 is positive overall but:
- only 13 trades;
- 2024 mean = -0.2334;
- bootstrap CI crosses zero;
- minimum trade-count gates fail.

T25+:
- extremely sparse.

## ARM C — DIRECT_EF_Q25

T0:
- BUY_ONLY: 6 trades, +0.0977
- SELL_ONLY: 17 trades, -0.0689
- COMBINED: 23 trades, -0.0255

The gate removes observed early failures but leaves sample sizes far below the preregistered minimums.

Some 2024 means are positive in these tiny subsets, but they are not statistically or operationally admissible under the frozen gates.

## ARM D — DIRECT_EF_Q10

The strictest early-failure gate nearly eliminates all trades.

T0:
- BUY_ONLY: 1 trade
- SELL_ONLY: 3 trades
- COMBINED: 4 trades

All are economically unusable as research evidence.

## Main interpretation

EXP-005 separates two important facts:

1. the frozen feature set can predict rapid <=5-minute adverse-barrier failure with useful discrimination;
2. the same feature set does not support accurate direct executable-P&L regression.

The downside gate can eliminate many rapid-loss trades, but low-risk opportunities become extremely sparse and do not satisfy minimum trade-count, year-balance, or bootstrap requirements.

Therefore the problem is not simply “avoid early failures.” The remaining trade-quality signal is still too weak or too sparse under the current frozen representation.

No EXP-005 candidate should advance.

Do not:
- open 2025;
- loosen Q50/Q25/Q10 post hoc;
- change the 5-minute definition;
- add new direct-score thresholds;
- promote tiny positive subsets;
- proceed to Exness demo/live.

## Next implication

A future experiment should preserve the useful insight that rapid-loss risk is predictable, but should materially change the market-state representation rather than continue reusing the same frozen 48-feature vector.

Potential direction for a new preregistered experiment:
- richer causal multi-timeframe structure;
- event/session context;
- explicit path-shape / acceleration / drawdown-before-target features;
- or sequence-based representation.

2025 remains sealed.
