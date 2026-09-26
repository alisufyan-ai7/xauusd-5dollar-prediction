# EXP-001 Initial Baseline Findings

Status: COMPLETE — NON-SEALED PARTITIONS ONLY

Source run: GitHub Actions 36156744481

Final OOS 2025 was not accessed by the baseline analysis.

## Data used

Eligible complete-feature rows across TRAIN, VALIDATION, and DEVELOPMENT_TEST:

- 2,860,357 rows

Fresh full-snapshot total rows:

- 3,522,322 rows

The fresh-snapshot audit found changes versus prior byte locks in 2018, 2019, 2020, 2021, 2023, 2024, and 2025. The exact fresh manifest from this run is the source-of-truth record for this result.

## Unconditional success rates

Success means the directional $5 target was reached before the $3 adverse barrier within 60 minutes.

### TRAIN — 2016-2021

- BUY: 5.8884%
- SELL: 6.4968%

### VALIDATION — 2022

- BUY: 10.4284%
- SELL: 10.8127%

### DEVELOPMENT_TEST — 2023-2024

- BUY: 12.3229%
- SELL: 12.5314%

Interpretation:

The absolute $5/$3 problem became materially easier in later years. This strongly suggests that volatility/regime is not just a secondary feature; it is central to the target's attainability.

This is not evidence of a predictive trading edge by itself.

## Volatility is the strongest baseline discriminator

TRAIN-derived 60-minute realized-movement tertiles:

- q33: 0.1879226
- q67: 0.3149316

### TRAIN

BUY:
- LOW: 0.8541%
- MID: 3.2162%
- HIGH: 13.5959%

SELL:
- LOW: 0.9067%
- MID: 3.4488%
- HIGH: 15.1343%

### VALIDATION

BUY:
- LOW: 1.2891%
- MID: 3.8282%
- HIGH: 15.1852%

SELL:
- LOW: 1.1443%
- MID: 4.1792%
- HIGH: 15.6473%

### DEVELOPMENT_TEST

BUY:
- LOW: 1.2293%
- MID: 4.9127%
- HIGH: 17.1297%

SELL:
- LOW: 1.5206%
- MID: 4.6083%
- HIGH: 17.5653%

Interpretation:

A $5 move inside 60 minutes is largely a volatility-regime problem. Low-volatility states are poor candidates for this objective. High-volatility states consistently show a many-fold increase in target-first success probability.

## Session effect

### TRAIN

BUY:
- ASIA: 3.5978%
- EUROPE: 6.4938%
- US: 7.7642%
- LATE: 3.1962%

SELL:
- ASIA: 3.6413%
- EUROPE: 7.5871%
- US: 8.5755%
- LATE: 2.9168%

### VALIDATION

BUY:
- ASIA: 5.2526%
- EUROPE: 13.5455%
- US: 13.5074%
- LATE: 2.5272%

SELL:
- ASIA: 5.1203%
- EUROPE: 14.5323%
- US: 13.8067%
- LATE: 3.9160%

### DEVELOPMENT_TEST

BUY:
- ASIA: 8.4596%
- EUROPE: 13.7434%
- US: 15.5223%
- LATE: 3.1919%

SELL:
- ASIA: 8.4366%
- EUROPE: 13.9644%
- US: 15.9083%
- LATE: 3.8468%

Interpretation:

Europe and US sessions consistently provide substantially more favorable conditions for a $5-in-60m target than Asia or the late session.

Session should be treated as market context, not a standalone signal.

## Momentum-direction effect

Momentum buckets are based on 60-minute price change:

- DOWN: < -$1
- FLAT: -$1 to +$1
- UP: > +$1

### TRAIN

BUY:
- DOWN: 8.0256%
- FLAT: 3.1482%
- UP: 8.5833%

SELL:
- DOWN: 10.2268%
- FLAT: 3.6413%
- UP: 7.8673%

### VALIDATION

BUY:
- DOWN: 11.4152%
- FLAT: 7.0488%
- UP: 12.7055%

SELL:
- DOWN: 12.4050%
- FLAT: 7.5759%
- UP: 12.3234%

### DEVELOPMENT_TEST

BUY:
- DOWN: 13.8319%
- FLAT: 8.1931%
- UP: 14.6599%

SELL:
- DOWN: 15.7060%
- FLAT: 8.3094%
- UP: 13.3978%

Interpretation:

Flat momentum is consistently weaker than directional momentum.

There is also directional asymmetry consistent with continuation:
- BUY is strongest in UP states;
- SELL is strongest in DOWN states.

However, opposite-direction states still show meaningful success rates, so simple trend-following is not sufficient.

## Unresolved outcomes are common

A large fraction of otherwise eligible observations reach neither barrier within 60 minutes.

This reinforces that the system must estimate target attainability and should frequently abstain.

## Main conclusion

The first baseline stage does not prove a trading edge, but it establishes three robust contextual facts for EXP-001:

1. volatility regime is the dominant first-order determinant of whether a $5 target is reachable;
2. Europe/US session context materially changes target attainability;
3. directional momentum contains useful structure, especially when aligned with trade direction.

The next feature milestone should therefore focus on objective expert-trader concepts that refine these three dimensions rather than adding arbitrary indicators.
