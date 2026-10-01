# Information Parity V1 — Stage 1 Source Feasibility Preregistration

Status: **FROZEN BEFORE SOURCE ACQUISITION / INTEGRATION**

Decision context:
- D-064: pause new strategy/model experiments until information parity is built.
- D-065: freeze the five-stage Information Parity V1 roadmap before implementation.

Parent roadmap:
`research/INFORMATION_PARITY_V1_ROADMAP.md`

## 1. Purpose

Stage 1 does **not** test profitability and does **not** train a trading model.

Its purpose is to determine, before any full historical integration, which missing information channels can be reconstructed for the 2016-2021 TRAIN period in a way that is:

- timestamp-safe;
- reproducible;
- sufficiently granular for intraday XAUUSD decisions;
- legally/accessibly obtainable for this research project;
- explicit about revisions and missingness;
- free from obvious hindsight leakage.

The output is an admission decision for each information channel, not an economic result.

## 2. Data governance

Permitted XAUUSD research period:
- 2016-2021 TRAIN only.

Sealed XAUUSD periods:
- 2022 validation;
- 2023-2024 development test;
- 2025 final OOS.

Stage 1 must not access sealed XAUUSD evaluation periods.

External-source metadata may describe general historical coverage beyond 2021, but Stage 1 must not build or analyze 2022-2025 XAUUSD-aligned external feature datasets.

No broker/order mutation is authorized.

No raw provider dataset will be committed to Git.

## 3. Source-layer motivation

The admitted Badar source layer documents decision use of information beyond XAUUSD price alone, including:

- DXY / USD direction;
- US yield context;
- scheduled macro events;
- post-release context;
- multi-timeframe XAUUSD structure and liquidity;
- volume / participation;
- session state.

This Stage 1 audit tests whether those information channels can be supplied causally to an intelligent system.

It does **not** assume that any channel is predictive merely because Badar uses it.

## 4. Channels under audit

Stage 1 must produce a decision for each of the following.

### C1 — DXY / broad USD intraday context

Preferred object:
- ICE U.S. Dollar Index / DXY itself, if a reproducible historical intraday source is available.

Fallback:
- a defensible broad-USD proxy may be admitted with limitation only if:
  - its composition and meaning are documented;
  - it exists causally at the required timestamps;
  - it is not constructed using future daily values;
  - the proxy distinction is explicit.

### C2 — US Treasury / rate intraday context

Preferred:
- intraday US 10-year Treasury yield.

Acceptable with limitation:
- a clearly documented intraday market proxy for 10Y rate direction, such as a Treasury futures-derived measure, only if exact semantics are documented.

Daily-only yield series cannot be treated as intraday state and may at most be admitted as a slow-regime variable.

### C3 — Scheduled macro-event calendar

Required event families for feasibility assessment:

- CPI;
- Nonfarm Payrolls / Employment Situation;
- FOMC rate decisions / statements;
- Initial Jobless Claims;
- GDP;
- ISM manufacturing/services where available;
- JOLTS.

Additional event families may be documented but cannot be added to the Stage 2 minimum layer without a later preregistration amendment made before empirical model results.

### C4 — Macro release values and surprise state

For each supported event family, investigate availability of:

- scheduled/publication timestamp;
- actual value;
- forecast/consensus;
- previously published value;
- revision semantics;
- unit / seasonal-adjustment metadata.

Consensus/forecast data are not mandatory for event-calendar admission.

If consensus history is not reproducible point-in-time, the event calendar may still be admitted while surprise features are excluded.

### C5 — XAUUSD M1 volume semantics

The primary Dukascopy M1 schema already contains `volume`.

Stage 1 must establish, from provider/tool documentation or other authoritative evidence where possible:

- what that volume field represents;
- whether BID and ASK side downloads carry equivalent/different volume semantics;
- whether the field is consistent enough for causal relative-volume features;
- missing/zero-value behavior.

No claim of centralized exchange volume is allowed unless the provider explicitly supports that interpretation.

### C6 — XAUUSD tick microstructure feasibility

The project already has a Dukascopy tick downloader/validator supporting:

- timestamp;
- ASK;
- BID;
- optional askVolume;
- optional bidVolume.

Stage 1 must determine whether targeted historical tick data are practical for:

- spread dynamics;
- quote-update intensity;
- short-horizon microstructure;
- volume-at-quote only if the fields have defensible semantics.

This stage does **not** authorize a full 2016-2021 tick-history download.

## 5. Candidate-source evaluation matrix

Every candidate source considered must be recorded with:

1. provider / source name;
2. exact series / instrument;
3. source URL or API/document identifier;
4. access method;
5. historical coverage;
6. nominal frequency;
7. actual timestamp granularity;
8. timezone / timestamp basis;
9. whether timestamps represent:
   - market observation time;
   - scheduled event time;
   - publication time;
   - database update time;
10. revision policy;
11. point-in-time reproducibility;
12. known missingness;
13. cost / authentication requirement;
14. terms/licensing or redistribution constraint relevant to this project;
15. whether raw data can remain external/ignored while compact manifests are committed;
16. alignment risk with XAUUSD timestamps;
17. verdict.

## 6. Admission verdicts

Each channel must receive exactly one final verdict:

### ADMITTED

Use when the channel has:
- reliable 2016-2021 TRAIN coverage;
- timestamp semantics appropriate for causal use;
- reproducible acquisition;
- acceptable missingness;
- no unresolved hindsight/revision problem material to the intended feature.

### ADMITTED WITH LIMITATION

Use when the channel is useful but has a material limitation, for example:
- coarser than preferred frequency;
- proxy rather than exact DXY/yield;
- event schedule available but consensus unavailable;
- incomplete subperiod coverage.

The limitation must be encoded in Stage 2 and cannot be silently ignored.

### DEFERRED

Use when a channel appears potentially useful but Stage 1 cannot establish sufficient reliable historical access without disproportionate cost/engineering.

Deferred channels are excluded from Information Parity V1.

### REJECTED

Use when:
- timestamps are not causally reconstructible;
- historical values are revision-contaminated with no point-in-time version;
- coverage is materially inadequate;
- access/terms make reproducible use unsuitable;
- semantics are too ambiguous.

## 7. Minimum temporal requirements

These are feasibility criteria, not a promise that the fastest source will be chosen.

### DXY / USD context

Preferred:
- <= 5-minute observations.

Admissible with limitation:
- >5m and <=30m if timestamp-safe and coverage is otherwise strong.

Daily-only:
- cannot be admitted as intraday DXY state;
- may only be considered as a slow-regime variable.

### Yield / rate context

Preferred:
- <= 5-minute observations.

Admissible with limitation:
- >5m and <=30m.

Daily-only:
- slow-regime context only.

### Macro events

Required:
- event timestamp precise enough to prevent a pre-release row from receiving post-release information.

For post-release actual/forecast/surprise:
- values may become available only at or after the documented publication timestamp.

## 8. Revision / hindsight controls

A source must not receive a clean ADMITTED verdict for a value if the historical record available today silently replaces what was known at the original decision time.

Examples:

- revised macro values must not replace the originally released value for a feature intended to represent the release surprise;
- a daily yield close must not be propagated backward through that same day;
- later-corrected timestamps must be documented;
- end-of-day aggregates must not appear in intraday rows before the period ends.

If point-in-time vintage data are unavailable:
- use only the unrevised/first-release field if recoverable;
- otherwise exclude that feature or mark the channel ADMITTED WITH LIMITATION for schedule-only use.

## 9. Stage 1 acquisition boundary

Before this preregistration is committed:
- no new external historical source acquisition/integration is allowed.

After this preregistration is committed, Stage 1 may perform:

- web/API documentation research;
- metadata requests;
- schema inspection;
- tiny targeted samples needed to verify timestamps, fields, and coverage.

Stage 1 may **not**:
- build a complete multi-source 2016-2021 feature dataset;
- train a model;
- calculate trading P&L;
- optimize thresholds;
- access sealed XAUUSD periods.

### Targeted sample rule

If a candidate source requires empirical verification, use the smallest sample sufficient to test schema/timestamps/coverage.

Do not choose sample windows because of known XAUUSD outcomes.

For XAUUSD Dukascopy tick feasibility, any new sample must come from 2016-2021 only and be used only for data-quality/microstructure feasibility, not trade selection.

## 10. No profitability or feature selection in Stage 1

Forbidden in Stage 1:

- trading backtests;
- target-before-stop outcome analysis by source channel;
- training classifiers/regressors;
- selecting a source because it correlates better with future gold returns;
- P&L-based source choice;
- post-hoc source shopping based on economic outcomes.

Sources are admitted based on data integrity, causality, reproducibility, semantics, and practical coverage.

Predictive usefulness is tested later under the frozen Stage 4 ablation design.

## 11. Required Stage 1 outputs

Create:

1. `research/INFORMATION_PARITY_V1_STAGE1_SOURCE_FEASIBILITY_FINDINGS.md`
2. one compact source registry, preferably:
   `research/INFORMATION_PARITY_V1_SOURCE_REGISTRY.json`
3. compact acquisition/sample manifests if any targeted samples are used;
4. D-067 or later decision recording the final Stage 1 channel verdicts;
5. update `research/PROJECT_CONTINUITY.md`.

Raw external data must remain uncommitted.

## 12. Stage 1 completion criteria

Stage 1 is complete only when C1-C6 each have a documented verdict.

At minimum, Stage 2 may begin only if the project has:

- the existing XAUUSD BID/ASK M1 data;
- understood M1 volume semantics well enough to decide whether volume enters V1;
- at least one admitted or admitted-with-limitation cross-market channel from C1/C2;
- an admitted or admitted-with-limitation scheduled macro-event calendar.

If neither DXY/USD nor rate context can be admitted, Stage 2 may still proceed only after a new decision explicitly records that cross-market parity is unavailable and narrows the V1 claim.

## 13. Stop conditions

Stop source hunting for a channel when:

- two strong candidate sources fail for the same fundamental reason; and
- no clearly superior accessible candidate is identified from authoritative documentation.

Do not search indefinitely for the perfect provider.

If an exact source is unavailable, prefer:
- a documented limitation;
- a defensible proxy;
- or exclusion,

over opaque scraped data with uncertain timestamps.

## 14. Stage transition

Passing Stage 1 does not authorize profitability modeling.

After Stage 1 completion:
1. record findings/verdicts;
2. freeze the admitted source list;
3. separately specify the Stage 2 Information Parity Layer schema/alignment contract;
4. only then acquire/build the full TRAIN information layer.

2022-2025 remain sealed throughout Stage 1.
