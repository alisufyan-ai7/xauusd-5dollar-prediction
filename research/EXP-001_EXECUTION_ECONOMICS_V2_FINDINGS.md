# EXP-001 Execution Economics V2 Findings

Status: COMPLETE — ECONOMIC SCREEN FAILED

Source run: 36316779171

Artifact: exp001-execution-economics-v2

FINAL_OOS 2025 was not accessed.

## Core result

Once historical BID/ASK spread and executable-side entry/exit are modeled directly from Dukascopy ticks, none of the preregistered BUY_ONLY, SELL_ONLY, or COMBINED policies has positive overall expectancy.

This remains true even at F0, before any additional commission/slippage stress.

## Top 1%

### COMBINED

F0:
- trades: 2,275
- average net P&L: -0.3662 price units/trade
- profit factor: 0.8183
- 2023 average: -0.1038
- 2024 average: -0.4331
- day-block bootstrap 95% CI: [-0.5563, -0.1817]

F10:
- average net P&L: -0.4662
- profit factor: 0.7760
- 2023 average: -0.2038
- 2024 average: -0.5331
- bootstrap 95% CI: [-0.6563, -0.2817]

### BUY_ONLY

F0:
- trades: 1,729
- average net P&L: -0.4961
- profit factor: 0.7602
- 2023 average: -0.4742
- 2024 average: -0.5014
- bootstrap 95% CI: [-0.6755, -0.2846]

### SELL_ONLY

F0:
- trades: 1,532
- average net P&L: -0.1828
- profit factor: 0.9066
- 2023 average: +0.0411
- 2024 average: -0.2331
- bootstrap 95% CI: [-0.3921, +0.0068]

F10:
- average net P&L: -0.2828
- profit factor: 0.8601
- 2023 average: -0.0589
- 2024 average: -0.3331
- bootstrap 95% CI: [-0.4921, -0.0932]

SELL_ONLY top 1% is the strongest mode, but it still fails the preregistered V2 advancement criteria.

## Other policies

All top 2.5%, 5%, and 10% policies were negative at F0 and worsened monotonically under F05/F10/F20.

No policy/mode passed the V2 F10 advancement rule.

## Interpretation

The predictive ranking edge discovered under the original BID-close +5/-3 labeling framework does not translate into positive executable-side economics once spread is modeled through ASK/BID entry and exit.

This is not a failure of the tick reconstruction. It is evidence that the current target/model objective is misaligned with executable trading economics.

The largest issue is conceptual:
- the model was trained to predict whether a BID-referenced +5 move occurs before a BID-referenced -3 move;
- live BUY execution pays ASK at entry and exits on BID;
- live SELL exits on ASK;
- spread therefore changes both the effective barrier geometry and expectancy.

## Decision

Do not:
- open 2025;
- freeze any current top-10/5/2.5/1% operating policy;
- promote SELL-only top 1% post hoc;
- proceed to Exness demo trading from this model.

Next research milestone should redesign the prediction target itself around executable BID/ASK economics and then retrain/revalidate from scratch under a new experiment version.

2025 remains sealed.
