# Intelligent-System Information Audit — XAUUSD / Badar Parity

Status: **INFORMATION AUDIT COMPLETE — MODELING PAUSED PENDING INFORMATION PARITY**

## Purpose

The project has repeatedly shown that changing price-only rules, handcrafted features, model classes, sequence representations, and target formulations does not by itself create robust executable positive expectancy.

The owner has clarified the intended goal:

> an intelligent system should not be reduced to rigid trading rules; it should observe enough information to make context-sensitive decisions at least comparable to a strong human trader, with the potential to use more information than the human.

Therefore the next research question is not "which rule should we loosen?" or "which model should we try next?"

It is:

> **Do we currently provide the system with the information required to represent the decision environment that Badar demonstrably uses?**

This audit compares:

1. information actually used or consulted by Badar in the admitted source layer;
2. information currently available in the XAUUSD project;
3. information that exists in raw project data but is not currently represented;
4. information that is missing and must be acquired;
5. information that is difficult or impossible to reproduce exactly.

No 2022-2025 market data are opened by this audit.

## Source boundary

Primary durable project:
`alisufyan-ai7/xauusd-5dollar-prediction`

Admitted Badar source:
`alisufyan-ai7/unpack-human-trading-strategies-claude`

Badar provenance rule:
- outside `derived/` = source layer;
- inside `derived/` = Claude interpretation only and not attributable to Badar.

Primary Badar evidence used in this audit:
- `PLAYBOOK.md`
- `LIVE_TRADING_OBSERVATIONS.md`
- `dataset/live_trades.csv`
- source notes cited by those files.

## Bottom line

**No: the project does not currently contain all of the information channels that Badar demonstrably uses when making decisions.**

The current system is strongest on XAUUSD price-path and execution reconstruction.

It is weak or absent on:
- scheduled macro-event context;
- DXY / USD context;
- US-yield context;
- broader fundamental regime;
- volume / volume-profile representation;
- richer location-map representation;
- trader-style scenario/context state;
- exact live broker microstructure before 2026.

This means prior negative model results cannot establish that an intelligent system cannot match or exceed a skilled human. They establish that **the tested systems could not do so from the information representation they were given**.

## Information Badar demonstrably uses

The admitted source layer shows the following decision inputs.

### A. Multi-timeframe XAUUSD price structure

Badar repeatedly works top-down:
- monthly / weekly glance;
- D1 bias and close quality;
- H4 external structure;
- H1 direction and POIs;
- M30/M15 confirmation;
- M5/M3/M1 execution.

He uses:
- swing structure;
- BOS / MSS;
- candle closes;
- wick/body quality;
- rejection;
- compression / expansion;
- previous 1-2 days' behavior;
- whether price is in the middle or at a meaningful location.

### B. Liquidity and location map

Source-supported examples include:
- previous-day high / low;
- Asian high / low;
- London high / low;
- H4 swing highs / lows;
- HTF HH/HL/LH/LL;
- equal highs / lows;
- trendline liquidity;
- H1/H4/D1 FVG / imbalance;
- order blocks;
- breaker blocks;
- BOS origin;
- premium / discount and Fibonacci location;
- high-volume candles;
- Volume Profile POC.

This is substantially richer than V4/V5's mandatory session-sweep + active-H1-FVG conjunction.

### C. Time/session state

Badar explicitly treats time as important:
- Asia / London / New York;
- session opens;
- first hours after open;
- pre-session manipulation;
- post-news windows;
- session-to-session behavior.

### D. Scheduled macro-event context

The source layer shows repeated use of Forex Factory and explicit attention to:
- NFP;
- CPI;
- FOMC / rate decisions;
- unemployment claims;
- GDP;
- ISM / JOLTS / payroll revisions in live streams.

He changes behavior around news:
- avoids some periods;
- waits for a release or post-release close;
- sometimes trades post-news;
- sometimes reduces risk.

### E. Cross-market context

The source layer explicitly documents:
- DXY direction;
- US 10-year yield checks;
- broader USD/gold divergence reasoning.

DXY or US yields were checked on multiple observed live streams.

### F. Broader fundamental regime

Badar's source material also refers to:
- rate expectations;
- central-bank gold buying;
- ETF flows;
- war / geopolitical volatility.

These are usually context/risk inputs rather than exact entry triggers.

### G. Volume / participation context

The source layer uses or shows:
- tick volume;
- high / ultra-high-volume candles;
- VSA concepts;
- Session Volume Profile / POC.

Indicators such as RSI and EMA are also used as confluence, not as the core system.

### H. Scenario / expectation state

Live observations show Badar:
- draws expected paths before entries;
- considers alternative scenarios;
- waits for specific HTF closes;
- changes confidence when the market violates the expected path;
- labels some trades high/low probability;
- changes position risk accordingly.

This is a latent decision-state layer that rigid setup rules do not represent well.

### I. Execution and risk state

Badar's live decisions include:
- market entry on candle close;
- resting limit orders;
- scaled/split entries;
- explicit logical stop placement;
- skipping trades when the stop is too large;
- half-risk decisions;
- manual exits when the market invalidates the thesis;
- stop tightening;
- session/day trade-history context.

An intelligent system should represent current portfolio/risk state separately from market prediction.

## What the primary project currently has

### 1. XAUUSD M1 BID/ASK OHLCV — AVAILABLE

Dukascopy historical M1 files include:

`timestamp, open, high, low, close, volume`

The project has synchronized BID/ASK history and side-aware executable labeling.

Current historical research has used:
- BID/ASK OHLC;
- spread;
- M1 through derived higher-timeframe price structure.

This is the strongest part of the information stack.

### 2. Spread / executable-side information — AVAILABLE AND USED

EXP-002 added causal:
- close spread;
- rolling mean spread;
- rolling max spread;
- spread ratios;
- spread percentiles.

This is suitable for historical executable reconstruction on Dukascopy.

### 3. Price-derived expert features — AVAILABLE AND USED

The existing price feature layer already includes:
- returns across multiple windows;
- candle body/wick features;
- range and range position;
- distance from local highs/lows;
- realized volatility;
- true range;
- compression / expansion;
- slopes;
- simple swing-state proxies;
- previous/current-day distance;
- round-number distance;
- impulse/pullback measures;
- session/time features;
- directional consistency.

EXP-006 additionally tested path efficiency, sign changes, jump concentration, extrema recency and synthetic-bar structure.

EXP-007 tested a causal sequence model.

These negative results are valuable, but all remain primarily price-state experiments.

### 4. Session context — PARTIALLY AVAILABLE

The project has:
- UTC session labels;
- Europe / US timing;
- Asian/London/NY session logic in V4/V5;
- session highs/lows in specific experiments.

It does not yet maintain one comprehensive source-faithful session/liquidity state representation for general intelligent-system input.

### 5. Previous-day / swing / FVG structure — PARTIALLY AVAILABLE

The project can mechanically derive:
- PDH / PDL;
- H1/H4 causal swings;
- H1 FVGs;
- session liquidity;
- BOS-like state.

But these are scattered across experiments and are not assembled into one unified observation tensor/state.

### 6. Volume — RAW DATA AVAILABLE, NOT USED IN THE MAIN INTELLIGENCE LAYER

This is an important gap.

The Dukascopy M1 schema already includes a `volume` field and validation preserves it.

However, `scripts/build_features.py` currently builds features from price and does not use the volume field.

Therefore volume information is **already available historically but is being discarded by the current feature representation**.

### 7. Tick microstructure — TECHNICALLY AVAILABLE FROM DUKASCOPY, NOT BUILT AS A FULL HISTORICAL LAYER

The project has a Dukascopy tick downloader and validator.

The tick validator supports:
- timestamp;
- ask price;
- bid price;
- optional ask volume;
- optional bid volume.

Historical full-range tick acquisition has not been established as the primary research dataset and may be substantially larger/costlier than M1.

It should be treated as an optional execution/microstructure layer after a targeted feasibility check rather than downloaded blindly.

### 8. Exness broker-specific ticks — AVAILABLE FOR 2026 ONLY

The read-only Exness probes establish contemporaneous BID/ASK tick access in 2026.

The tested demo server returned no historical ticks for sampled 2023-2025 windows and begins returning data in sampled January 2026 windows.

Therefore:
- Dukascopy remains the historical execution source;
- Exness 2026 is useful for forward/shadow broker calibration;
- exact historical Exness microstructure cannot currently be reconstructed from that server for TRAIN.

## Information currently missing from the primary project

### 1. DXY / USD index context — MISSING

No project data/source/feature pipeline for DXY currently exists.

This is a material parity gap because Badar explicitly checks DXY and uses USD/gold relationship context.

### 2. US Treasury yield context — MISSING

No historical US-yield time series is currently integrated.

Badar is observed checking US yields on multiple streams.

For entry-level parity, intraday timing matters more than a daily closing series.

### 3. Scheduled macro-event calendar — MISSING

The project currently has no timestamp-safe historical event calendar for:
- CPI;
- NFP;
- FOMC;
- GDP;
- claims;
- ISM;
- JOLTS;
- similar US releases.

V4/V5 used a fixed time exclusion as a placeholder, not an actual event-history layer.

### 4. Macro release values / surprise — MISSING

The system does not currently know, at release time:
- actual value;
- market forecast/consensus;
- previous/revised value;
- surprise magnitude;
- event class.

This matters if the intelligent system is expected to reason about post-news behavior rather than merely avoid scheduled times.

### 5. DXY/gold/yield divergence state — MISSING

Because DXY and yields are absent, the system cannot represent:
- gold rising while USD weakens;
- gold failing to rise despite a weak DXY;
- yield/gold divergence;
- cross-market confirmation/conflict.

### 6. Broader fundamental regime — MISSING

No timestamp-safe historical layer exists for:
- central-bank buying;
- ETF flows;
- rate-expectation regime;
- geopolitical/war state.

These are lower-frequency context features and should not be allowed to contaminate intraday timestamps with hindsight.

### 7. Volume / VSA / participation features — MISSING FROM MODEL INPUT

Raw M1 volume exists, but the intelligence layer currently ignores it.

No unified features exist for:
- relative volume;
- volume expansion/contraction;
- high-volume candle state;
- price/volume divergence;
- session-relative volume.

### 8. Volume Profile / price-at-volume context — MISSING

M1 bar volume alone does not uniquely reconstruct true volume-at-price inside a minute.

A proper profile requires either:
- sufficiently detailed tick/volume data;
- or an explicitly approximate construction.

It must not be silently fabricated from OHLC bars.

### 9. Unified source-location map — MISSING

The project has individual deterministic pieces, but not a unified timestamp-safe representation of:
- PDH/PDL;
- session ranges;
- equal highs/lows;
- approach/test count;
- H1/H4 swings;
- FVG/imbalance;
- OB/breaker candidates;
- BOS origin;
- premium/discount;
- target/liquidity hierarchy.

An intelligent model should receive these as context, not be forced through one mandatory rule chain.

### 10. Scenario-state representation — MISSING

Badar reasons in scenarios rather than one fixed rule.

The current project does not encode:
- expected path alternatives;
- invalidation hierarchy;
- what information changed since the previous minute;
- whether a thesis is strengthening/weakening;
- confidence state.

This should be represented by a learned sequential/context model rather than hand-coded prose rules.

### 11. Trade/account state — MISSING FROM MARKET MODELS

The system should separately know:
- whether a trade is already open;
- realized session P&L;
- recent loss/win;
- risk already deployed;
- number of attempts on the same thesis;
- current stop/target;
- whether a prior setup was missed.

This is execution-policy state, not a price prediction feature.

## Information that is difficult or fundamentally unobservable

### A. Actual retail stop/order map

Badar teaches about where retail stops and pending orders likely cluster.

The project does not have direct access to the full global OTC gold retail order book.

This cannot be treated as a literal observed variable.

The system can only infer likely liquidity from:
- structure;
- session highs/lows;
- repeated levels;
- broker/client positioning if a legitimate source is later available.

### B. Exact institutional order flow

No public XAUUSD OTC dataset gives complete institutional intent.

The system should not pretend to observe "smart money orders" directly.

### C. Badar's internal discretionary state

Experience, attention, intuition, and visual expectations cannot be recovered exactly.

The goal should not be to copy human cognition.

Instead, market/context variables should be supplied richly enough that a model can learn a superior decision mapping.

### D. Exact historical Exness execution before 2026

The probed server does not expose the required old tick history.

Historical model development therefore cannot claim exact Exness fills for TRAIN.

Forward/shadow calibration can use Exness 2026 onward.

## Information-parity classification

### GREEN — already available for intelligent modeling

- XAUUSD BID/ASK M1 OHLC;
- historical M1 volume field;
- spread;
- timestamp/session;
- causal multi-timeframe bars;
- volatility;
- path history;
- PDH/PDL;
- causal swings;
- FVG candidates;
- executable target/adverse labels;
- 2026 Exness read-only ticks for forward broker calibration.

### AMBER — derivable from existing data but not yet assembled properly

- rich multi-timeframe chart tensors;
- complete session/liquidity map;
- equal highs/lows;
- repeated-level/test count;
- trendline-like geometry;
- premium/discount;
- OB/breaker candidates;
- BOS-origin / impulse-origin context;
- volume/VSA features;
- session-relative participation;
- confidence/invalidation state learned from sequential context;
- trade/account state.

### RED — missing external information channel

- DXY intraday;
- US Treasury yield intraday;
- macro-event schedule;
- release actual/forecast/surprise;
- broader macro/fundamental regime;
- ETF/central-bank flow context;
- geopolitical/news state;
- other related markets such as silver/risk assets if later justified.

### BLACK — cannot be assumed directly observable

- global retail stops/order book;
- complete institutional order flow;
- Badar's private mental state;
- exact historical Exness microstructure before the available broker-history boundary.

## Scientific implication

The current project is **not ready to answer**:

> "Can an intelligent system outperform Badar?"

because the input environment is not yet information-comparable to Badar's observed environment.

The existing experiments answer narrower questions:

> Can price-only / price-dominant systems with the tested representations and targets find robust executable edge?

So far, the answer has been no.

That does **not** justify more arbitrary model or threshold searching.

It justifies building a richer information layer first.

## Required next milestone — Information Parity Layer V1

No new profitability model should be trained until a separately preregistered Information Parity Layer is specified.

The minimum V1 information package should contain:

1. **Gold market state**
   - raw causal XAUUSD M1 BID/ASK sequence;
   - M1 volume;
   - multi-timeframe causal bars/tensors;
   - spread;
   - session state;
   - higher-timeframe structural/liquidity map.

2. **Cross-market state**
   - DXY or a defensible USD-index proxy with intraday timestamps;
   - US 10-year yield or closest reproducible intraday rate proxy;
   - optionally silver only if source evidence / later ablation justifies it.

3. **Macro-event state**
   - scheduled event type;
   - exact scheduled/publication timestamp;
   - time-to/time-since event;
   - actual/forecast/previous where historically reproducible without hindsight;
   - surprise normalization;
   - post-event regime flag.

4. **Participation/microstructure state**
   - M1 relative volume / volume regime;
   - spread regime;
   - targeted tick-data feasibility for microstructure around entries/events;
   - no fabricated volume profile from insufficient data.

5. **Decision-state context**
   - current/previous session behavior;
   - recent thesis/invalidation state represented causally;
   - open-position and risk state kept separate from market-state prediction.

## Information sufficiency test

Do not assume that adding every available dataset improves trading.

After the information layer is built, the first intelligent-system experiment should include **ablation**:

- gold-only;
- +volume;
- +macro calendar;
- +DXY;
- +yield;
- combinations.

The goal is to determine which information channels produce incremental predictive/decision value.

A channel that does not improve held-out decision/economic evidence should be removed even if Badar uses it.

This allows the system to eventually use **more useful information than a human**, without blindly copying every human habit.

## Recommended architecture direction after parity

After information parity, the model should not be another rigid setup classifier.

A sensible intelligent architecture is:

`multi-source causal observation -> state encoder -> opportunity / direction / attainable excursion / downside-risk heads -> policy layer -> BUY / SELL / NO TRADE -> execution/risk state machine`

The state encoder should be allowed to consume sequences/tensors rather than only hand-engineered scalar rules.

The economic policy must remain separately validated from predictive fit.

## Stop condition against a research rat race

Do not proceed indefinitely through model variants.

Use a finite sequence:

1. build information parity;
2. verify timestamp integrity and coverage;
3. run a Badar-decision recognition benchmark and information-channel ablation;
4. only if the representation can recognize expert-like decision states better than a price-only baseline, freeze one economic policy experiment;
5. if the richer information does not materially improve expert-state recognition or economic opportunity quality, stop this formulation instead of tuning endlessly.

## Data governance

At this milestone:
- 2016-2021 remains TRAIN for historical development;
- 2022 remains unopened for the new information-parity design unless a later preregistration explicitly permits it;
- 2023-2024 remain unopened for the new design;
- 2025 remains sealed final OOS.

Adding a new historical external data source does not by itself authorize opening a sealed XAUUSD evaluation period.

No broker/order mutation is authorized.
