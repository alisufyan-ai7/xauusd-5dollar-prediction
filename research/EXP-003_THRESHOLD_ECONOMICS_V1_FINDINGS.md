# EXP-003 Sequential Threshold Economics V1 Findings

Status: COMPLETE — NO POLICY PASSES

Source run: 36337595939

Artifact: exp003-threshold-economics-v1

FINAL_OOS 2025 was not accessed.

## Core result

No preregistered EXP-003 threshold/mode combination passed the frozen advancement rule.

Passing policies:
- none

This includes all combinations of:
- T0 / T25 / T50 / T75;
- BUY_ONLY / SELL_ONLY / COMBINED.

## T0

BUY_ONLY:
- trades: 1,334
- mean NET_F10: -0.4151
- profit factor: 0.7583
- 2023: -0.2732
- 2024: -0.5604
- bootstrap 95% CI: [-0.5829, -0.2499]

SELL_ONLY:
- trades: 2,346
- mean NET_F10: -0.4040
- profit factor: 0.7703
- 2023: -0.3168
- 2024: -0.4529
- bootstrap 95% CI: [-0.5321, -0.2677]

COMBINED:
- trades: 3,431
- mean NET_F10: -0.4142
- profit factor: 0.7616
- 2023: -0.2832
- 2024: -0.5036
- bootstrap 95% CI: [-0.5197, -0.3046]

## T25

BUY_ONLY:
- trades: 266
- mean NET_F10: -0.5426
- profit factor: 0.7151
- 2023: +0.0245
- 2024: -1.1272
- bootstrap 95% CI: [-0.9723, -0.1356]
- positive-quarter concentration exceeded the frozen limit.

SELL_ONLY:
- trades: 674
- mean NET_F10: -0.5121
- profit factor: 0.7262
- 2023: -0.5064
- 2024: -0.5159
- bootstrap 95% CI: [-0.7533, -0.2861]

COMBINED:
- trades: 927
- mean NET_F10: -0.5099
- profit factor: 0.7279
- 2023: -0.2836
- 2024: -0.6772
- bootstrap 95% CI: [-0.7293, -0.3038]

## T50

BUY_ONLY:
- trades: 52
- mean NET_F10: -0.8219
- profit factor: 0.6124
- below minimum trade-count gate.

SELL_ONLY:
- trades: 172
- mean NET_F10: -0.3934
- profit factor: 0.7830
- below minimum overall trade-count gate.

COMBINED:
- trades: 223
- mean NET_F10: -0.4812
- profit factor: 0.7439
- below minimum overall trade-count gate.

All remain economically negative.

## T75

Trade counts are too small and economics remain negative:

BUY_ONLY:
- trades: 14
- mean NET_F10: -0.8443

SELL_ONLY:
- trades: 40
- mean NET_F10: -0.6858

COMBINED:
- trades: 54
- mean NET_F10: -0.7269

## Interpretation

1. Explicit expected-value modeling did not convert the current frozen feature set into positive sequential economics.
2. Raising the EV threshold did not improve realized expectancy monotonically; in several cases economics became worse.
3. 2024 remains especially problematic and prevents advancement.
4. The failure is therefore deeper than the EXP-002 binary target alone.
5. No EXP-003 V1 policy should be nominated for pre-OOS candidate freeze.

Do not:
- open 2025;
- tune T0/T25/T50/T75 post hoc;
- add a regime filter from these results;
- proceed to Exness demo/live from EXP-003 V1.

Next work should diagnose why predicted EV itself is miscalibrated to realized executable P&L and determine whether a different target/feature representation is justified under a new preregistered experiment.

2025 remains sealed.
