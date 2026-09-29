# EXP-008 Competing Hazard Target-Before-Adverse V1 Findings

Status: COMPLETE — NO POLICY PASSES

Source run: 36616276558

Artifact: exp008-competing-hazard-v1

Artifact digest:
sha256:b7a0e068256443eb73d37ad3009fab48570256010905af4bef5ae409138c5f3d

FINAL_OOS 2025 was not accessed.

## Core result

No preregistered EXP-008 policy passed the frozen advancement rule.

Passing policies:
- none

## Aggregate hazard calibration

### BUY DEVELOPMENT_TEST

- multiclass log loss: 1.3539
- macro Brier: 0.6011

Predicted vs realized:
- SUCCESS: 9.43% vs 10.99%
- FAILURE: 35.32% vs 35.67%
- UNRESOLVED: 55.25% vs 53.28%
- EARLY_FAILURE: 4.59% vs 4.35%

Mean EV_HAZARD_F10:
- predicted: -0.5041
- realized: -0.4350
- gap: -0.0691

T0 raw rows:
- n = 638
- predicted mean EV: +0.0588
- realized mean NET_F10: -0.0250

### SELL DEVELOPMENT_TEST

- multiclass log loss: 1.3653
- macro Brier: 0.6069

Predicted vs realized:
- SUCCESS: 11.22% vs 11.27%
- FAILURE: 34.23% vs 36.29%
- UNRESOLVED: 54.55% vs 52.36%
- EARLY_FAILURE: 3.93% vs 4.07%

Mean EV_HAZARD_F10:
- predicted: -0.4637
- realized: -0.4848
- gap: +0.0211

T0 raw rows:
- n = 670
- predicted mean EV: +0.0775
- realized mean NET_F10: -0.2490

Interpretation:
the competing-hazard representation improves aggregate probability calibration relative to several prior formulations, particularly SELL, but the positive-EV tail still fails economically.

## Sequential economics

### A_HAZARD_EV — T0

BUY_ONLY:
- 102 trades
- mean NET_F10: -0.4043
- profit factor: 0.6670
- 2023: -0.2770
- 2024: -0.7579
- bootstrap 95% CI: [-0.8629, +0.0878]

SELL_ONLY:
- 168 trades
- mean NET_F10: -0.3412
- profit factor: 0.7940
- 2023: -0.5181
- 2024: -0.2178
- bootstrap 95% CI: [-0.8227, +0.1622]

COMBINED:
- 270 trades
- mean NET_F10: -0.3650
- profit factor: 0.7549
- 2023: -0.3925
- 2024: -0.3336
- bootstrap 95% CI: [-0.7249, +0.0048]

No T0 mode passes.

### Early-failure-gated T0 arms

Q50:
- BUY_ONLY: 60 trades, -0.5710
- SELL_ONLY: 40 trades, -0.1618
- COMBINED: 100 trades, -0.4073

Q25:
- BUY_ONLY: 23 trades, -0.5474
- SELL_ONLY: 9 trades, -0.6479
- COMBINED: 32 trades, -0.5757

Q10:
- BUY_ONLY: 4 trades, -1.0510
- SELL_ONLY: 1 trade, -0.9700
- COMBINED: 5 trades, -1.0348

Risk gating again collapses sample size without producing robust economics.

## T25 pocket

A_HAZARD_EV / T25 / SELL_ONLY:
- 10 trades
- mean NET_F10: +1.2290
- 2023: +0.1900
- 2024: +1.3444
- bootstrap 95% CI: [-2.4420, +3.1742]
- positive-quarter concentration: 54.5%

A_HAZARD_EV / T25 / COMBINED:
- 11 trades
- mean NET_F10: +0.9594
- 2023: -0.7735
- 2024: +1.3444
- bootstrap 95% CI: [-2.0973, +2.7503]

These tiny positive subsets are not admissible evidence because they fail:
- minimum total trades;
- minimum annual trades;
- bootstrap lower bound;
- quarter concentration;
- for COMBINED, 2023 positivity.

They must not be promoted.

## Main interpretation

EXP-008 provides a cleaner calibrated competing-risk representation than direct P&L regression,
but still does not identify a robust positive-expectancy executable tail.

The result suggests:

1. target/adverse timing structure is informative enough to improve aggregate calibration;
2. positive-EV opportunity counts remain sparse;
3. T0 sequential economics remain negative;
4. early-failure gating does not rescue the policy;
5. tiny T25 SELL pockets are too small and unstable to constitute evidence.

Therefore no EXP-008 candidate should advance.

Do not:
- open 2025;
- promote the 10-trade T25 SELL pocket;
- change hazard bin boundaries post hoc;
- add intermediate EV thresholds;
- loosen trade-count or bootstrap gates;
- proceed to Exness demo/live.

## Next implication

The remaining defensible research direction is to add a separately preregistered information source
rather than keep reformulating the same price-only state.

A future experiment should test timestamp-safe exogenous context such as:
- scheduled high-impact macro event proximity;
- session/liquidity regime;
- possibly public cross-market context if timestamp-safe and reproducible.

2025 remains sealed.
