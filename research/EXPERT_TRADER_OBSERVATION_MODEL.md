# Expert Trader Observation Model

Status: DESIGN PRINCIPLE / RESEARCH ROADMAP

## Design goal

The system should reason like a disciplined expert XAU/USD trader, but it should not imitate human cognitive weaknesses.

It should observe the same kinds of market context a strong discretionary trader considers, convert those observations into objective timestamp-safe variables, and test whether those variables actually improve the probability of reaching the EXP-001 target before the adverse barrier.

The system must not assume that a commonly discussed trading concept is useful merely because human traders use it.

Every observation layer must ultimately be testable.

## Expert-style observation layers

### 1. Higher-timeframe context

Questions an expert asks:

- Is gold trending, ranging, transitioning, or breaking out?
- What is the H4 / H1 directional structure?
- Where is current price relative to important recent swing highs/lows?
- Has price already extended far from its recent equilibrium?

Machine representation candidates:

- H4/H1/M15/M5 returns;
- rolling swing structure;
- distance to higher-timeframe highs/lows;
- trend persistence;
- trend slope;
- range position.

### 2. Current market structure

Questions:

- Higher highs / higher lows?
- Lower highs / lower lows?
- Compression?
- Breakout?
- Retest?
- Failed breakout?
- Rejection?
- Chaotic/noisy state?

Candidates:

- objective swing-point logic;
- breakout distance;
- retest distance;
- compression ratio;
- directional sequence statistics.

### 3. Location

Experts care about where a setup occurs.

Candidates:

- distance to recent local highs/lows;
- previous-day high/low;
- previous-week high/low;
- range midpoint;
- breakout levels;
- round-number proximity;
- distance from recent impulse origin.

### 4. Momentum and acceleration

Questions:

- Is movement persistent?
- Is momentum strengthening or weakening?
- Is the move already exhausted?
- Is a pullback losing force?

Candidates:

- 1m/3m/5m/15m/30m/60m/4h returns;
- return acceleration;
- directional consistency;
- impulse/pullback ratio;
- close-location within candle/range.

### 5. Volatility regime

Question:

Can the market plausibly travel $5 within the 60-minute horizon?

Candidates:

- realized volatility;
- ATR/range measures;
- volatility percentile;
- compression/expansion state;
- recent gap behavior.

The model must be allowed to output NO TRADE when the target is structurally unlikely within the horizon.

### 6. Price-action/candle behavior

Not simplistic pattern labels.

Candidates:

- body/range ratio;
- wick asymmetry;
- consecutive directional bars;
- closes near highs/lows;
- expansion after compression;
- rejection strength;
- failed-breakout behavior.

### 7. Multi-timeframe agreement

An expert may combine H1 context, M15 structure, and M5/M1 trigger behavior.

The machine should eventually model cross-timeframe alignment explicitly.

### 8. Session and liquidity context

Gold behavior differs across:

- Asia;
- London/Europe;
- New York;
- London/New York overlap;
- rollover;
- reopen periods.

Session is context, not a trading signal by itself.

### 9. Economic-event risk

Future candidate context:

- CPI;
- NFP;
- FOMC;
- PCE;
- GDP;
- jobless claims;
- major central-bank communication.

Possible behaviors:

- avoid entry near major events;
- classify an event regime;
- study post-event normalization separately.

Event handling must use only information known before the decision timestamp.

### 10. Related-market context

Potential future candidates:

- USD strength;
- US Treasury yields;
- real yields;
- silver;
- broader risk sentiment.

These must be point-in-time aligned and added only if they materially improve out-of-sample evidence.

### 11. Reward versus adverse path

The system is not simply predicting direction.

EXP-001 asks:

- BUY: probability +$5 occurs before -$3 within 60 minutes;
- SELL: probability -$5 occurs before +$3 within 60 minutes.

This is a path-dependent probability problem.

### 12. Setup quality and abstention

A disciplined trader does not force a fixed number of trades.

The machine must support:

- BUY;
- SELL;
- NO TRADE.

Opportunity frequency is measured separately from predictive quality.

## Confluence

Human experts often describe confluence qualitatively:

- trend aligned;
- pullback into support;
- selling pressure weakening;
- session active;
- volatility expanding;
- level reclaimed;
- no imminent event risk.

The machine equivalent should not rely on prose intuition.

Each component should become a measurable input, and combinations should be tested empirically.

## What not to imitate from humans

Do not reproduce:

- FOMO;
- revenge trading;
- emotional stop movement;
- trade quotas;
- loss-chasing;
- hindsight pattern recognition;
- subjective exceptions after seeing outcomes.

## Intended architecture

Market observation
→ Context / regime
→ Setup recognition
→ Probability estimation
→ Confluence / quality
→ BUY / SELL / NO TRADE
→ Deterministic risk and execution

## Research principle

Expert-style observation is useful only if objective historical testing shows that it improves calibration, discrimination, robustness, and opportunity quality.

A concept is not admitted merely because experienced traders commonly discuss it.
