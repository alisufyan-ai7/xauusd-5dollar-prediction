# EXP-004 Shift-Aware Calibrated Economic Value V1 Findings

Status: COMPLETE — NO ADVANCEMENT POLICY PASSES

Source run: 36394304605

Artifact: exp004-shift-aware-calibrated-ev-v1

FINAL_OOS 2025 was not accessed.

## Core result

No preregistered ARM B or ARM C threshold/mode combination passed the frozen advancement rule.

Passing policies:
- none

ARM A (RAW_EV) is benchmark-only and was not eligible to advance.

## Calibration effect

Calibration improved aggregate probability fit modestly.

DEVELOPMENT_TEST BUY:
- RAW multiclass log loss: 0.8035
- CAL multiclass log loss: 0.7991
- RAW aggregate EV calibration gap: -0.0560
- CAL aggregate EV calibration gap: -0.0737

DEVELOPMENT_TEST SELL:
- RAW multiclass log loss: 0.8028
- CAL multiclass log loss: 0.8003
- RAW aggregate EV calibration gap: +0.0501
- CAL aggregate EV calibration gap: approximately 0.0000

Therefore chronological probability calibration improved broad aggregate calibration, especially for SELL.

However, aggregate calibration did not translate into profitable positive-EV sequential opportunities.

## ARM B — Calibrated EV

### T0

BUY_ONLY:
- trades: 191
- mean NET_F10: -0.4237
- profit factor: 0.6498
- 2023: -0.1843
- 2024: -0.9099
- bootstrap 95% CI: [-0.7169, -0.0953]

SELL_ONLY:
- trades: 161
- mean NET_F10: -0.4339
- profit factor: 0.6523
- 2023: -0.3914
- 2024: -0.4982
- bootstrap 95% CI: [-0.8024, -0.0377]

COMBINED:
- trades: 350
- mean NET_F10: -0.4413
- profit factor: 0.6424
- 2023: -0.2925
- 2024: -0.7024
- bootstrap 95% CI: [-0.6906, -0.1939]

All fail economically and also miss the 250-trade minimum for BUY_ONLY/SELL_ONLY.

### T25

The calibrated positive-EV tail becomes extremely sparse:

BUY_ONLY:
- trades: 9
- mean NET_F10: +0.5479
- 2023 only; no 2024 trades
- bootstrap CI crosses zero
- trade-count gates fail

SELL_ONLY:
- trades: 7
- mean NET_F10: -0.0060
- trade-count gates fail

COMBINED:
- trades: 16
- mean NET_F10: +0.3056
- bootstrap CI crosses zero
- trade-count and quarter-concentration gates fail

T50 / T75:
- zero executed trades.

Interpretation:
calibration removed much of the false-positive tail, but the remaining high-EV region became too sparse and unstable to support a trading policy.

## ARM C — Calibrated EV + support gate

DEVELOPMENT_TEST support eligibility:
- eligible: 83.06%
- rejected: 16.94%

### T0

BUY_ONLY:
- trades: 170
- mean NET_F10: -0.3922
- profit factor: 0.6675
- 2023: -0.1754
- 2024: -0.8335
- bootstrap 95% CI: [-0.7168, -0.0500]

SELL_ONLY:
- trades: 118
- mean NET_F10: -0.4379
- profit factor: 0.6330
- 2023: -0.4554
- 2024: -0.4094
- bootstrap 95% CI: [-0.8621, -0.0389]

COMBINED:
- trades: 287
- mean NET_F10: -0.4204
- profit factor: 0.6465
- 2023: -0.2986
- 2024: -0.6446
- bootstrap 95% CI: [-0.6946, -0.1432]

The support gate does not rescue economics.

### T25

Only 7 BUY, 2 SELL, and 9 COMBINED trades execute.

The sample is far below preregistered minimums and has no 2024 coverage for these variants.

T50 / T75:
- zero executed trades.

## Interpretation

EXP-004 provides a clean separation of effects:

1. chronological probability calibration improves global probability fit;
2. support-aware abstention removes a meaningful fraction of shifted observations;
3. neither change creates positive robust sequential economics;
4. calibration sharply reduces the number of apparently positive-EV observations;
5. the few remaining higher-EV opportunities are too sparse and temporally unstable;
6. 2024 remains particularly weak for BUY;
7. the existing frozen feature representation / base learner does not appear sufficient to identify a robust positive-expectancy tail under the current target and execution rules.

This means EXP-004 does not justify a pre-OOS candidate freeze.

Do not:
- open 2025;
- loosen support thresholds post hoc;
- add intermediate EV cutoffs;
- alter calibration hyperparameters based on these results;
- promote sparse T25 variants;
- proceed to Exness demo/live.

## Next implication

A future experiment should no longer be a small calibration or threshold adjustment to the same representation.

The next research question should be whether a materially different predictive representation or target formulation can separate:
- true favorable trade opportunities;
- rapid adverse-barrier failures;
- regime-shift / high-volatility states.

That future experiment must be separately designed and preregistered.

2025 remains sealed.
