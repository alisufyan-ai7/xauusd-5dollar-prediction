# Information Parity V1 — Finite Research Roadmap

Status: **FROZEN ROADMAP BEFORE IMPLEMENTATION**

## Purpose

This roadmap operationalizes D-064.

The project must not return to an open-ended cycle of:
- adding another trading rule;
- changing another threshold;
- trying another model family;
- or loosening filters until a profitable backtest appears.

The next research program is finite and has exactly five stages.

No stage may be skipped merely because an intermediate result looks promising.

No new profitability model may be trained before Stages 1 and 2 are complete.

No 2022-2025 XAUUSD evaluation period may be opened under this roadmap unless a later separately preregistered validation explicitly authorizes it.

## Stage 1 — Information-source feasibility audit

### Goal

Determine which missing information channels can be reconstructed historically in a timestamp-safe, reproducible way for the 2016-2021 TRAIN period.

### Required channels to investigate

1. DXY / USD index intraday context.
2. US Treasury-yield intraday context, with 10Y preferred if suitable.
3. Scheduled macro-event calendar:
   - CPI;
   - NFP / payrolls;
   - FOMC / rate decisions;
   - unemployment claims;
   - GDP;
   - ISM;
   - JOLTS;
   - other events only if source evidence and reproducibility justify inclusion.
4. Event release values:
   - actual;
   - forecast/consensus;
   - previous;
   - revision handling;
   - timestamp semantics.
5. Existing Dukascopy XAUUSD M1 volume semantics and usability.
6. Targeted feasibility of Dukascopy tick volume / microstructure around relevant windows.

### For every candidate source, record

- provider/source;
- instrument/series;
- frequency;
- timezone/timestamp basis;
- historical coverage;
- point-in-time semantics;
- publication/revision behavior;
- API/access method;
- reproducibility;
- missing-data behavior;
- licensing/access constraints;
- whether the data can be used without hindsight leakage.

### Exit condition

Stage 1 ends with each channel classified as:

- ADMITTED;
- ADMITTED WITH LIMITATION;
- DEFERRED;
- REJECTED.

A channel must not enter Stage 2 unless admitted.

## Stage 2 — Build Information Parity Layer V1

### Goal

Create one causal market-observation state available at each decision timestamp.

### Required information groups

#### A. XAUUSD market state

- synchronized M1 BID/ASK OHLC;
- spread;
- M1 volume;
- raw recent M1 sequences;
- causal M3/M5/M15/M30/H1/H4/D1 representations;
- volatility/range state;
- session state;
- previous-day state;
- source-supported liquidity/location state where deterministic.

#### B. Cross-market state

For admitted sources only:

- DXY / USD-index state;
- US-yield/rate state;
- causal changes/trends/divergence with XAUUSD.

#### C. Macro-event state

For admitted sources only:

- next scheduled high-impact event;
- minutes to event;
- minutes since event;
- event class;
- actual/forecast/previous where historically point-in-time safe;
- surprise magnitude;
- post-event regime state.

#### D. Participation / microstructure state

- relative M1 volume;
- volume regime;
- spread regime;
- tick-derived microstructure only if Stage 1 establishes feasibility.

#### E. Decision/risk state

Kept separate from market prediction:

- whether a position is open;
- current direction;
- entry/stop/target state;
- attempts on the same thesis;
- realized session P&L;
- prior win/loss;
- risk already deployed.

### Representation principle

Preserve raw causal sequences/tensors in addition to engineered context.

Do not reduce the information layer to a single rigid rule chain.

### Integrity requirements

Before Stage 3:

- timestamp alignment tests;
- no future-row access;
- reproducible acquisition;
- compact data identities / hashes;
- documented missingness;
- schema/version lock.

### Exit condition

Information Parity Layer V1 is frozen and reproducible on TRAIN.

No profitability claim is made in Stage 2.

## Stage 3 — Badar decision-recognition benchmark

### Goal

Test whether the richer information state contains enough information to recognize expert-like decision moments.

### Source supervision

Use the admitted Badar live-trade dataset and source-layer observations.

Do not treat Claude-derived interpretations as Badar labels.

### Benchmark construction

For each sufficiently timestamp-resolvable Badar trade:

- reconstruct the causal market state immediately before entry;
- record direction;
- preserve available confidence/risk/setup metadata;
- build matched non-trade timestamps from the same stream/day/session.

### Required leakage protection

Use grouped evaluation so the same stream/day cannot be split across training and evaluation.

No random row-level split.

### Primary questions

1. Can the model rank Badar's actual entry timestamps above matched non-trade timestamps?
2. Can it recover Badar's trade direction better than a price-only baseline?
3. Does the richer information improve calibration/decision ranking?

### Important limitation

This stage does not claim that Badar's every trade is optimal.

It tests information sufficiency and expert-state recognizability.

### Exit condition

Proceed only if the richer representation materially improves expert-decision recognition relative to a frozen gold-only baseline.

If it does not, stop and diagnose missing information instead of changing model families repeatedly.

## Stage 4 — Information-channel ablation

### Goal

Determine which information channels provide incremental value.

### Frozen comparison arms

At minimum:

1. GOLD_ONLY
2. GOLD_PLUS_VOLUME
3. GOLD_PLUS_MACRO
4. GOLD_PLUS_DXY
5. GOLD_PLUS_YIELD
6. GOLD_PLUS_DXY_PLUS_YIELD
7. FULL_INFORMATION_PARITY_V1

Additional arms require preregistration before results.

### Control rule

Use one fixed recognition architecture and training procedure across arms.

Do not tune architecture independently per channel.

### Report

For each arm:

- expert-entry ranking;
- direction accuracy/calibration;
- opportunity discrimination;
- robustness across held-out streams/days;
- incremental delta versus GOLD_ONLY.

### Decision rule

Information channels that do not add stable held-out value should not be kept merely because Badar uses them.

The machine is allowed to discard human-used inputs and retain machine-useful inputs.

### Exit condition

Freeze the smallest information set that retains the useful incremental signal.

## Stage 5 — One intelligent economic experiment

### Goal

Only after Stages 1-4 pass, freeze one economic trading experiment.

### Intended architecture class

A multi-source causal state model with separate heads or outputs for:

- opportunity;
- direction;
- attainable favorable excursion;
- downside/adverse risk;
- confidence/abstention.

Policy output:

- BUY;
- SELL;
- NO TRADE.

Execution/risk logic remains a separate state machine.

### Requirements

Before running:

- one frozen architecture;
- one frozen label/target definition;
- one frozen execution model;
- one frozen cost model;
- one frozen advancement rule;
- no post-hoc threshold search.

### Validation progression

Initial economic experiment:
- 2016-2021 TRAIN only.

Only if frozen TRAIN gates pass:
- write a separate preregistration for 2022 validation.

2023-2024 and 2025 remain sealed unless later separately authorized.

## Anti-rat-race stop rules

This program must stop rather than mutate indefinitely.

### Stop A — source failure

If key external channels cannot be obtained with trustworthy point-in-time history:
- document the limitation;
- exclude them;
- do not fabricate proxies without preregistration.

### Stop B — information failure

If Information Parity V1 does not materially improve Badar-decision recognition over gold-only:
- stop this formulation;
- diagnose missing observation channels;
- do not cycle through arbitrary model families.

### Stop C — economic failure

If the one frozen intelligent economic experiment fails its gates:
- do not loosen thresholds post hoc;
- do not cherry-pick a tiny profitable subset;
- do not open 2022.

A new experiment would require a new scientific hypothesis, not parameter searching.

## Governance

Primary repository:
`alisufyan-ai7/xauusd-5dollar-prediction`

Admitted Badar source:
`alisufyan-ai7/unpack-human-trading-strategies-claude`

Badar source provenance:
- outside `derived/` = source layer;
- inside `derived/` = Claude interpretation only.

Current data boundary:
- 2016-2021 = TRAIN and allowed;
- 2022 = sealed validation;
- 2023-2024 = sealed development test;
- 2025 = sealed final OOS.

No broker/order mutation is authorized.

## Immediate next action

Create a dedicated Information Parity V1 branch and preregister **Stage 1: information-source feasibility audit** before acquiring or integrating any new external historical data.

