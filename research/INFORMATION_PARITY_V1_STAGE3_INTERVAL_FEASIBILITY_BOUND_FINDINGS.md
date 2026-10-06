# Information Parity V1 — Stage 3 Interval-Row Feasibility Bound and Final Evidence-Adequacy Finding

Status: **FINAL D-091 EVIDENCE STATUS = INSUFFICIENT; RECOGNITION HYPOTHESIS NOT TESTED**

Parents:
- `research/INFORMATION_PARITY_V1_STAGE3_PROTOCOL_PREREGISTRATION.md`
- `research/INFORMATION_PARITY_V1_STAGE3_EVIDENCE_ADEQUACY_CLARIFICATION.md`
- D-089 through D-096

Pinned Badar source:
- repository `alisufyan-ai7/unpack-human-trading-strategies-claude`
- commit `2df3d588c4b6d82761df2ee0c6f6639e82ce3414`
- `dataset/live_trades.csv` blob `ea620cb44937f276be2e65ae7da25ae9503be655`

No `derived/` content was used.
No market-price lookup was used.

## Why a feasibility bound is enough

D-096 established that all 40 current exact-M1 candidates had been adjudicated and only four are primary eligible.

The remaining 79 source-table rows were interval-only/unresolved.

To avoid blind frame-by-frame review, the frozen next step was to ask whether those 79 rows could *possibly* rescue D-091 under the existing rules.

A remaining row can help only if it could plausibly satisfy both:
1. Badar-owned live/real execution;
2. one unique source-resolved M1 entry minute.

If even an optimistic upper bound cannot meet one of the frozen evidence floors, exhaustive adjudication cannot change the conclusion.

## Deliberately generous upper-bound construction

Artifact:
`research/reference/information-parity-v1/stage3-interval-feasibility-bound-v1.csv`

The upper bound deliberately over-includes rather than under-includes.

A whole unresolved stream is retained whenever its source layer exposes any meaningful execution context such as:
- explicit Exness real / Real Pro account;
- Exness account history;
- Exness terminal used during the stream;
- explicit MetaTrader/XNS broker context;
- or, as an extra conservative allowance, a source note identifying Badar's broker chart even without proof that the unresolved row was actually filled live.

For retained streams, unresolved XAUUSD rows are counted in the bound even when:
- the individual row has not been tied to the real account;
- timestamp evidence still requires frame/transcript adjudication;
- ownership of a specific position is not yet proved.

This makes the bound intentionally optimistic.

The scan also found one additional stream, `EVm0u9Csglk`, whose full source note says Badar uses/takes the Exness terminal; both unresolved XAUUSD rows from that stream were therefore added to the generous bound.

Generic educational statements such as:
- preferring live accounts;
- future plans to trade a live account;
- lot-size advice for a hypothetical live account;
- comparing TradingView candles with Exness;

are not current execution evidence and are not treated as a plausible live fill context.

The explicit July 28 paper/TradingView stream remains outside the live bound.

## Generous unresolved rescue set

Upper-bound unresolved candidates:
- rows: **38**
- distinct dates: **17**
- LONG: **17**
- SHORT: **21**

These are not declared eligible rows. They are the maximum deliberately generous set worth considering as possible rescuers.

## Current confirmed primary set

From Batches 01-04:
- primary rows: **4**
- LONG: **3**
- SHORT: **1**
- distinct primary dates: **3**

Confirmed primary rows:
- `NIDMLJuBPwk#1`
- `B83jlxwuo10#1`
- `B83jlxwuo10#5`
- `qTSedn6hEp8#2`

## Absolute optimistic maximum

Assume, contrary to current evidence, that **every one** of the 38 upper-bound unresolved rows later proves:
- Badar-owned;
- live/real;
- exact-M1;
- otherwise primary eligible.

Then the absolute maximum becomes:

- total primary positives: **42**
- LONG: **20**
- SHORT: **22**
- distinct eligible source dates: **17**

The maximum eligible-date list is:

- 2026-07-06
- 2026-07-07
- 2026-07-10
- 2026-07-31
- 2026-08-04
- 2026-08-06
- 2026-08-07
- 2026-08-28
- 2026-08-31
- 2026-09-02
- 2026-09-04
- 2026-09-14
- 2026-09-16
- 2026-09-17
- 2026-09-21
- 2026-09-24
- 2026-10-02

D-091 requires:
- >=40 positives;
- >=20 dates;
- >=15 LONG;
- >=15 SHORT.

The count and direction floors could be reached only under this unrealistically optimistic assumption.

The **date floor cannot**.

Maximum possible distinct dates:
**17 < 20**

This is decisive.

Even perfect promotion of every deliberately over-included rescue row cannot make the pinned 119-row teacher source satisfy the frozen evidence-adequacy gate.

## Final D-091 result

Evidence adequacy:

`INSUFFICIENT`

Recognition hypothesis:

`NOT TESTED / INCONCLUSIVE`

Do not run the frozen Stage 3 FULL-vs-GOLD benchmark on this teacher corpus.

This is not a recognition FAIL because the benchmark never reaches the evidence-adequacy prerequisite.

## Scientific meaning

The finding is about the available teacher evidence only.

It does **not** establish:
- that Information Parity V1 lacks useful predictive information;
- that Badar's decision process is unlearnable;
- that gold cannot be modelled;
- that a profitable XAUUSD system cannot be built.

It means only:

> the pinned Badar source corpus does not contain enough source-verifiable, exact-M1, live/real Badar-owned teacher decisions across enough independent dates to support the frozen Stage 3 recognition benchmark.

## Chronology consequence

D-088 remains in force.

Opening or repurposing 2026 market data would **not** repair this teacher-evidence problem, because the inadequacy is already established before any market join.

Therefore there is no scientific reason to consume reserved 2026 XAUUSD merely to attempt this frozen benchmark.

2022-2025 remain sealed.
2026 remains unaccessed for Stage 3 market reconstruction.

## What would be required to continue Stage 3

The current frozen benchmark can proceed only after a new preregistered source/design decision, for example:

1. add genuinely new source-layer Badar live-trade evidence sufficient to raise the independent-date count, while preserving the same primary-teacher criteria; or
2. define a **different** teacher construct, such as Badar-authored decision intent regardless of live broker execution, and preregister it as a new experiment rather than retroactively weakening D-089; or
3. admit a different timestamp-resolvable expert teacher source.

Any of these is a new research design decision.

Do not change 40 / 20 / 15 / 15 after observing this shortfall merely to force the benchmark to run.
