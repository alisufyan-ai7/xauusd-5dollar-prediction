# Root-Reset V1 Gate-Overlap Diagnosis

Status: FROZEN BEFORE DIAGNOSTIC RESULTS

## Scope

This diagnosis is restricted to:
- TRAIN 2016-2021 for fitting;
- VALIDATION 2022 for diagnosis.

It MUST NOT access:
- DEVELOPMENT_TEST 2023-2024;
- FINAL_OOS 2025.

## Purpose

Determine why Root-Cause Reset V1 produced zero qualifying validation trades despite meaningful OPPORTUNITY_5 ranking.

The diagnosis must measure each gate independently and jointly without changing any V1 rule.

## Frozen inputs and models

Reuse Root-Cause Reset V1 exactly:
- event sampler;
- ATR15 proxy;
- continuation direction;
- BASE48 opportunity model;
- dynamic initial-stop rule;
- OPPORTUNITY_5 target;
- EARLY_DAMAGE target;
- direction-specific validation Q50 risk cutoff.

No model refit rule, feature, event threshold, stop rule, or target definition may change.

## Required diagnostics

For BUY and SELL separately:

### Opportunity score distribution

Report predicted P(OPPORTUNITY_5) quantiles:
- p01
- p05
- p10
- p25
- p50
- p75
- p90
- p95
- p99
- max

Report counts and realized OPPORTUNITY_5 rate for score thresholds:
- >=0.10
- >=0.15
- >=0.20
- >=0.25
- >=0.30
- >=0.40
- >=0.50
- >=0.60
- >=0.70
- >=0.80

These thresholds are diagnostic only and MUST NOT become V2 trading thresholds automatically.

### Stop admissibility

Report:
- total events;
- stop-admissible count/share;
- stop-distance quantiles;
- OPPORTUNITY_5 rate among admissible vs rejected events;
- opportunity-score quantiles among admissible vs rejected events.

### EARLY_DAMAGE risk

Report predicted risk quantiles:
- p01
- p05
- p10
- p25
- p50
- p75
- p90
- p95
- p99
- max

Report realized EARLY_DAMAGE rate:
- all events;
- stop-admissible events;
- below/above Q50 risk cutoff.

### Gate intersections

For each diagnostic opportunity threshold above, report counts for:
- opportunity only;
- stop only;
- risk only;
- opportunity + stop;
- opportunity + risk;
- stop + risk;
- opportunity + stop + risk.

Also report realized:
- OPPORTUNITY_5 rate;
- mean MFE60;
- median MFE60;
- mean MAE60;
- median MAE60

for the three-way intersection.

### Opportunity-score deciles

For each score decile report:
- count;
- realized OPPORTUNITY_5 rate;
- mean MFE60;
- median MFE60;
- mean MAE60;
- median MAE60;
- stop-admissible share;
- risk-pass share.

## Interpretation rule

This diagnosis does not authorize trading or Reset V2.

It may support one of these conclusions:

1. OPPORTUNITY score is useful but V1 thresholds are mis-scaled.
2. Stop admissibility is the dominant bottleneck.
3. EARLY_DAMAGE risk veto is the dominant bottleneck.
4. Gate interactions destroy otherwise useful opportunity ranking.
5. Opportunity ranking itself is too weak after admissibility conditioning.

Reset V2 may be specified only after these diagnostics are recorded.

2023-2024 and 2025 remain untouched.
