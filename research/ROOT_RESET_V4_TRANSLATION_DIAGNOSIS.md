# Root-Reset V4 Translation Diagnosis

Status: FROZEN BEFORE DIAGNOSTIC RESULTS

## Scope

TRAIN only:
- 2016-2021 synchronized Dukascopy XAUUSD M1 BID/ASK.

Do NOT access:
- 2022
- 2023-2024
- 2025

This is a translation diagnosis, not a trading experiment.

## Purpose

V4 produced zero fills because the deterministic translation became too restrictive before entry.

This diagnosis quantifies source-observed alternatives without changing V4's scientific result.

## Frozen upstream stages

Reuse V4 unchanged through:
- H1-led directional gate;
- Asian/London session ranges;
- active H1 FVG overlap;
- M15 liquidity sweep;
- M15 close-back confirmation.

The diagnosis begins only AFTER the V4 M15 confirmation stage.

## Confirmation alternatives

For every V4 M15 close-back confirmation, measure within the next 30 minutes:

### C1 — one-close M5 MSS
BUY:
- first completed M5 close above the frozen pre-sweep M5 swing high.
SELL:
- first completed M5 close below the frozen pre-sweep M5 swing low.

### C2 — frozen V4 two-close M5 MSS
Exact V4 rule.

### C3 — one-close M3 MSS
Same frozen reference swing concept, but use completed M3 bars and a one-close break.

### C4 — one-close M1 MSS
Same directional break concept on completed M1 closes using the most recent confirmed causal M1 swing.

These are diagnostic counts, not policy candidates.

## Displacement/FVG alternatives

For each confirmation alternative:
- whether a same-timeframe 3-bar FVG exists by the confirmation bar;
- if yes, midpoint of that FVG.

No parameter tuning.

## Entry observability

For each confirmation alternative report:

1. direct-close entry:
   - executable next M1 open immediately after confirmation;

2. FVG-midpoint limit:
   - same-side executable touch within 30 minutes;
   - fill rate;
   - median wait-to-fill.

No trade economics are selected from this diagnosis.

## Broader structural target map

At each direct-close diagnostic entry and filled midpoint entry, report distance to:

- frozen Asian opposite high/low;
- frozen London opposite high/low;
- previous UTC-day high/low;
- nearest confirmed H1 swing liquidity in the trade direction;
- nearest confirmed H4 swing liquidity in the trade direction.

PDH/PDL here are diagnostic only and use the explicit UTC-day convention.

For each target family report:
- share with target distance >= $3;
- >= $5;
- >= $7;
- median target distance;
- p75 target distance.

## Source-observed live-style recovery questions

The diagnosis must answer:

1. How many M15 confirmations fail V4 two-close M5 MSS but pass one-close M5 MSS?
2. How many fail M5 two-close but pass M3 or M1 one-close confirmation?
3. How often would direct-close entry exist when midpoint-FVG entry does not fill?
4. Among confirmed setups, how often broader structural liquidity offers >=$5 while Asian/London opposite liquidity does not?
5. Which single V4 translation gate removed the largest number of otherwise source-plausible opportunities?

## Governance

Do not:
- select a new policy;
- compute or optimize a profitability threshold;
- choose a "best" confirmation based on P&L;
- change V4 rules;
- access 2022-2025.

After findings are recorded, a separate V5 preregistration may use the diagnosis to define a more faithful deterministic translation.
