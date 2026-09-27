# EXP-002 Sequential Execution Economics V1 Findings

Status: COMPLETE — ECONOMIC SCREEN FAILED

Source run: 36324128764

Artifact: exp002-execution-economics-v1

FINAL_OOS 2025 was not accessed.

## Core result

No preregistered BUY_ONLY, SELL_ONLY, or COMBINED policy at top 10%, 5%, 2.5%, or 1% passed the frozen F10 advancement rule.

All F10 overall expectancies were negative and all UTC-day bootstrap 95% intervals had negative lower bounds.

## Strongest observed policy

SELL_ONLY top 1% was the least negative policy.

F10:
- trades: 1,348
- average net P&L: -0.3252 price units/trade
- profit factor: 0.8360
- 2023 average net: -0.0895
- 2024 average net: -0.3967
- bootstrap 95% CI: [-0.5159, -0.1290]

Even at F0:
- average gross P&L: -0.2252 price units/trade

Therefore the failure is not caused only by the added F10 friction stress.

## Top 1% COMBINED

F10:
- trades: 2,087
- average net P&L: -0.4806
- profit factor: 0.7648
- 2023 average net: -0.1949
- 2024 average net: -0.5763
- bootstrap 95% CI: [-0.6463, -0.3041]

## Top 1% BUY_ONLY

F10:
- trades: 1,327
- average net P&L: -0.5434
- profit factor: 0.7374
- 2023 average net: -0.2709
- 2024 average net: -0.6402
- bootstrap 95% CI: [-0.7269, -0.3387]

## Interpretation

EXP-002 preserved strong predictive ranking discrimination, but that ranking did not translate into positive sequential economics under the preregistered execution rules.

The gap between classification quality and trading profitability remains material.

Do not:
- open 2025;
- promote any current policy;
- proceed to Exness demo trading from EXP-002 V1.

Next research should investigate why high classifier scores still produce negative sequential expectancy, using only non-sealed 2016-2024 data and without post-hoc threshold promotion.

2025 remains sealed.
