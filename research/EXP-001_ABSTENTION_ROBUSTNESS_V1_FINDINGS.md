# EXP-001 Abstention Robustness V1 Findings

Status: COMPLETE

Source run: 36310814632

Artifact: exp001-abstention-robustness-v1

FINAL_OOS 2025 was not accessed.

## Overall DEVELOPMENT_TEST robustness

### BUY

- top 10%: success 30.84%, lift 2.376x, selected n 63,458, bootstrap lift 95% CI [2.232, 2.544]
- top 5%: success 33.40%, lift 2.573x, selected n 34,090, bootstrap lift 95% CI [2.393, 2.782]
- top 2.5%: success 34.37%, lift 2.648x, selected n 17,487, bootstrap lift 95% CI [2.443, 2.893]
- top 1%: success 35.81%, lift 2.759x, selected n 6,704, bootstrap lift 95% CI [2.514, 3.044]

All four BUY policies were above unconditional success in both 2023 and 2024 and in every populated quarter.

### SELL

- top 10%: success 32.77%, lift 2.471x, selected n 64,433, bootstrap lift 95% CI [2.327, 2.625]
- top 5%: success 34.58%, lift 2.608x, selected n 33,324, bootstrap lift 95% CI [2.432, 2.797]
- top 2.5%: success 35.72%, lift 2.693x, selected n 15,942, bootstrap lift 95% CI [2.482, 2.911]
- top 1%: success 36.97%, lift 2.788x, selected n 5,699, bootstrap lift 95% CI [2.498, 3.098]

All four SELL policies were above unconditional success in both 2023 and 2024 and in every populated quarter.

## Time robustness

For BUY and SELL, all candidate policies were above the same-block unconditional base rate in every populated quarter from 2023-Q1 through 2024-Q4.

The magnitude of lift varied materially by quarter, which is expected under changing volatility/base-rate regimes, but the direction of the edge remained positive.

## Session robustness

ASIA, EUROPE, and US all showed strong positive lift when selected observations existed.

Coverage caveat:
- LATE had zero or only a handful of selected observations for most policies.
- Therefore absence of a negative LATE result is not evidence of robust LATE-session performance.

## Volatility-regime robustness

Critical finding:
- top 1%, top 2.5%, and top 5% policies selected only HIGH-volatility observations for both BUY and SELL.
- BUY top 10% selected only 4 MID rows and zero LOW rows.
- SELL top 10% also selected only HIGH-volatility observations.

Therefore the high-score edge is empirically a HIGH-volatility-regime phenomenon in DEVELOPMENT_TEST.

The generated stability flag all_volatility_regimes_above_unconditional must not be interpreted as evidence across LOW/MID regimes when those regimes contain zero selected rows.

## Dependence-aware uncertainty

All candidate policies had paired UTC-day bootstrap lift 95% confidence intervals entirely above 1.0.

This is important because the raw M1 rows overlap heavily through the 60-minute forward label horizon. The day-block result provides stronger evidence than a naive independent-row confidence interval.

## Conclusion

1. Fixed validation-derived abstention policies transfer robustly across 2023 and 2024.
2. The edge persists in every populated quarter for both BUY and SELL.
3. Daily block-bootstrap lift intervals remain comfortably above 1 for all four policies.
4. The apparent edge is concentrated almost entirely in HIGH-volatility conditions.
5. LATE-session and LOW/MID-volatility robustness are not demonstrated because the candidate policies rarely or never fire there.
6. The next milestone should freeze one candidate operating policy and perform a pre-OOS specification audit before any 2025 opening.
7. 2025 remains sealed.
