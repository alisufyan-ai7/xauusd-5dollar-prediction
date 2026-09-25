# EXP-001 Expert Feature Milestone V2

Status: FROZEN DESIGN BEFORE IMPLEMENTATION

## Objective

Expand the feature set from basic returns/session/volatility into an objective approximation of how a disciplined expert XAU/USD trader reads market context.

This milestone is informed only by TRAIN / VALIDATION / DEVELOPMENT_TEST baseline evidence. FINAL_OOS 2025 remains unavailable to model selection.

## Priority 1 — Volatility and target attainability

Add:

- realized movement: 5m, 15m, 30m, 60m, 120m, 240m;
- rolling true-range statistics;
- volatility percentile versus trailing history;
- short-vs-long volatility ratio;
- compression/expansion ratio;
- recent $5-range frequency;
- recent 60-minute maximum excursion;
- distance of current volatility from TRAIN-derived regime thresholds.

Reason:
Baseline evidence shows volatility is the strongest first-order discriminator.

## Priority 2 — Multi-timeframe trend and structure

Construct deterministic M5, M15, H1, H4 context from M1 data.

Add:

- timeframe returns;
- rolling slope;
- higher-high / lower-low sequence features;
- swing high / swing low distances;
- range position;
- distance to recent breakout levels;
- trend persistence;
- directional agreement across M5/M15/H1/H4.

Reason:
Directional momentum helps, but simple 60-minute return alone cannot distinguish continuation, pullback, exhaustion, and reversal.

## Priority 3 — Location

Add:

- distance to previous-day high/low;
- distance to current-day high/low;
- distance to rolling 1h/4h highs/lows;
- position within current 1h/4h/day range;
- distance to recent impulse origin;
- distance to round $5 / $10 levels as an exploratory descriptive feature only.

Reason:
Expert traders care about where a move begins, not just whether momentum exists.

## Priority 4 — Impulse, pullback, and candle sequence

Add:

- body/range ratio;
- close location within bar;
- wick asymmetry;
- consecutive directional bars;
- impulse magnitude;
- pullback depth;
- impulse-to-pullback ratio;
- return acceleration;
- directional consistency over 5/15/30 minutes;
- expansion after compression.

Reason:
This approximates expert assessment of conviction, rejection, continuation, and exhaustion without relying on subjective chart-pattern names.

## Priority 5 — Session transition context

Add:

- minutes since Europe-session start;
- minutes since US-session start;
- Europe/US overlap flag;
- minutes to session transition;
- session-specific trailing volatility.

Reason:
Baseline session effects are large and persistent.

## Deferred

Do not add yet:

- RSI/MACD/Stochastic simply because they are common;
- neural networks;
- subjective named candlestick patterns;
- macro-event features;
- USD/yield cross-market features.

Macro and cross-market context will be a separate milestone after price-only structure is evaluated.

## Modeling target

For each direction:

- SUCCESS = 1;
- FAILURE = 0;
- UNRESOLVED = 0;
- AMBIGUOUS excluded;
- incomplete outcome coverage excluded;
- incomplete feature history excluded.

This directly answers the original question: probability the $5 target is reached first within 60 minutes.

## Model progression after feature implementation

1. descriptive conditional tables;
2. logistic regression;
3. gradient-boosted trees;
4. calibration analysis;
5. abstention / confidence threshold research.

No complex model is justified before simpler models establish incremental value.

## Evaluation requirements

Report separately on TRAIN, VALIDATION, DEVELOPMENT_TEST:

- ROC-AUC;
- PR-AUC;
- Brier score;
- calibration curve/bins;
- log loss;
- success rate by predicted-probability bin;
- observation count;
- opportunity frequency above candidate thresholds;
- BUY/SELL symmetry;
- session and volatility stratification.

Because M1 observations overlap heavily, do not treat rows as independent for uncertainty estimates. Use time-blocked evaluation/bootstrapping for uncertainty.

## Final-OOS rule

2025 must remain excluded from:
- feature selection;
- model selection;
- threshold selection;
- hyperparameter tuning;
- model calibration choices.

Open 2025 only after a candidate configuration is frozen and hashed.
