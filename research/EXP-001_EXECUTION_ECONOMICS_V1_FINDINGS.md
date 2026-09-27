# EXP-001 Execution Economics V1 Findings

Status: COMPLETE

Source run: 36314782089

Artifact: exp001-execution-economics-v1

FINAL_OOS 2025 was not accessed.

## Scope

Execution Economics V1 is a BID-path economic proxy with frozen all-in round-trip cost deductions. It is not a broker-exact BID/ASK reconstruction.

## Combined sequential engine

### Top 1%

Trades: 2,193

C0:
- mean net P&L: +0.1765 price units/trade
- profit factor: 1.100
- 2023 mean: +0.3548
- 2024 mean: +0.1316
- bootstrap 95% CI: [0.0110, 0.3620]

C10:
- mean net P&L: +0.0765
- profit factor: 1.042
- 2023 mean: +0.2548
- 2024 mean: +0.0316
- bootstrap 95% CI: [-0.0890, 0.2620]

C20:
- mean net P&L: -0.0235
- profit factor: 0.988
- 2023 mean: +0.1548
- 2024 mean: -0.0684
- bootstrap 95% CI: [-0.1890, 0.1620]

Therefore top 1% does not pass the frozen C20 combined-policy advancement gate.

### Top 2.5%

At C20:
- mean net P&L: -0.1200
- profit factor: 0.937
- 2023 mean: -0.0136
- 2024 mean: -0.1538
- bootstrap 95% CI: [-0.2584, 0.0146]

Does not pass.

### Top 5%

At C20:
- mean net P&L: -0.2457
- profit factor: 0.871
- 2023 mean: -0.0583
- 2024 mean: -0.3210
- bootstrap 95% CI: [-0.3812, -0.1072]

Does not pass.

### Top 10%

At C20:
- mean net P&L: -0.2125
- profit factor: 0.881
- 2023 mean: +0.0630
- 2024 mean: -0.3597
- bootstrap 95% CI: [-0.3283, -0.0840]

Does not pass.

## Direction-specific observation

SELL-only top 1% remained positive under C20:
- 1,501 trades
- mean net P&L: +0.1365
- profit factor: 1.075
- 2023 mean: +0.5497
- 2024 mean: +0.0446

BUY-only top 1% was negative under C20:
- 1,591 trades
- mean net P&L: -0.2138
- profit factor: 0.891
- 2023 mean: -0.3165
- 2024 mean: -0.1883

This asymmetry is descriptive only. The milestone did not preregister a direction-specific production-policy selection rule, so no SELL-only candidate is frozen from this result.

## Conclusion

1. The combined economic proxy is marginally positive at zero cost for top 1%, but does not survive the preregistered C20 gate.
2. No combined candidate qualifies for final pre-OOS freeze.
3. SELL-only top 1% is the strongest direction-specific economic result, but requires further preregistered investigation rather than post-hoc promotion.
4. Because the historical input is BID-only, side-aware spread execution remains unresolved.
5. Historical execution work should proceed to BID+ASK reconstruction before any 2025 opening.
6. 2025 remains sealed.
