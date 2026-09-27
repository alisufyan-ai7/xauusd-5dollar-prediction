# Decision Log

This file records material project decisions and the reasoning that led to them.

It is intended to preserve continuity across chats and prevent silent changes to the research design.

---

## D-001 — Clean-room project isolation

Decision:
Use only this project repository, this project's chat context, and fresh public research/data.

Reason:
Prevent contamination from unrelated XAU/USD projects, strategies, code, assumptions, and prior conclusions.

---

## D-002 — Probability framing instead of certainty

Decision:
Model the probability that +$5 occurs before -$3 within 60 minutes for BUY, and the symmetric condition for SELL.

Reason:
Markets cannot provide genuine certainty. A probabilistic framing is measurable and compatible with calibration and abstention.

---

## D-003 — NO TRADE is a first-class outcome

Decision:
The prediction system may abstain.

Reason:
Forcing a fixed number of daily trades would bias the system toward low-quality states. A disciplined expert trader waits when no sufficiently strong setup exists.

---

## D-004 — M1 decision semantics

Decision:
Use the close of the current M1 bar as the reference price and begin outcome scanning from the next M1 bar.

Reason:
Prevents use of the decision bar's future high/low information and creates deterministic timestamp semantics.

---

## D-005 — Ambiguous same-minute barrier touches

Decision:
If target and adverse barrier are both touched inside the same M1 bar and ordering cannot be proven, mark the outcome AMBIGUOUS.

Reason:
Do not invent intra-minute event ordering from OHLC data.

---

## D-006 — Free public Dukascopy M1 feed

Decision:
Use free public Dukascopy XAU/USD M1 BID history as the primary historical source.

Reason:
It provides long historical coverage suitable for the initial feasibility study without paid data.

---

## D-007 — Historical acquisition window

Decision:
Use calendar years 2016-2025 for historical research.

Reason:
Ten years provides varied volatility and macro regimes while remaining operationally manageable.

2026 remains outside historical development.

---

## D-008 — Chronological partitions

Decision:

- TRAIN: 2016-2021
- VALIDATION: 2022
- DEVELOPMENT_TEST: 2023-2024
- FINAL_OOS: 2025

Reason:
Preserve chronological realism and maintain a genuinely untouched final out-of-sample year.

---

## D-009 — 2025 FINAL_OOS seal

Decision:
Do not expose or use 2025 outcome distributions during feature/model/threshold development.

Reason:
Opening 2025 early would turn the final OOS into another development set.

---

## D-010 — Dataset hash lock

Decision:
Pin every admitted yearly raw chunk by SHA-256 and row count.

Reason:
A later independent acquisition returned a 2020 file missing 120 rows while still passing structural validation. A subsequent targeted retry reproduced the original 2020 file exactly. Structural validation alone is therefore insufficient for research reproducibility.

---

## D-011 — Expert-trader observation principle

Decision:
Design the system to observe market context in the style of a disciplined expert human XAU/USD trader, but convert those observations into objective timestamp-safe variables and verify them statistically.

Reason:
Human experts consider context that simple single-indicator systems miss: higher timeframe structure, location, volatility, momentum, session, event risk, multi-timeframe alignment, and confluence.

The machine should preserve that breadth of observation while avoiding human emotional and cognitive weaknesses.

See: research/EXPERT_TRADER_OBSERVATION_MODEL.md

---

## D-012 — Expert concepts are hypotheses, not truths

Decision:
No human trading concept is accepted merely because traders commonly use it.

Reason:
Every feature or setup concept must demonstrate value through chronological validation, calibration, robustness, and later untouched OOS evidence.

---

## D-013 — Durable project context belongs in GitHub

Decision:
Material brainstorming conclusions, architectural rationale, project state, and research decisions must be recorded in this repository rather than existing only in ChatGPT conversation history.

Reason:
Future chats must be able to continue the project without depending on account-level memory or inaccessible prior-chat reasoning.

Operational rule:
After material decisions, update the decision log, relevant specification, and continuity summary.


---

## D-014 — Separate deterministic CI from historical reacquisition

Decision:
Automatic push/pull-request CI runs only deterministic repository tests. Public-data downloads, full-history reacquisition, dataset-lock reproduction checks, and long diagnostics are moved to a manually dispatched historical-data-integrity workflow.

Reason:
The public Dukascopy feed can return transient or changed historical snapshots that fail the pinned dataset lock even when repository code is correct. Re-running expensive network-dependent acquisition on every documentation or code commit created misleading red workflow runs and consumed unnecessary Actions capacity.

Operational rule:
- `.github/workflows/foundation-checks.yml` is automatic and deterministic.
- `.github/workflows/historical-data-integrity.yml` is manual and network/data dependent.
- A historical reacquisition mismatch is treated as a data-integrity event, not a code-regression failure.


---

## D-015 — Canonicalize current reproducible public snapshot

Decision:
If a previously locked Dukascopy yearly snapshot is no longer obtainable, and the current public snapshot is reproduced consistently across repeated independent downloads (including chunked reconstruction where practical), promote that current snapshot to the canonical dataset lock rather than blocking research indefinitely.

Applied:
2017 was changed from the unavailable prior snapshot (352,788 rows; SHA-256 8d6a8a2969536cf205ece4f1013003249ba794655deccdbe4bb5167d9f24347b) to the repeatedly reproduced current snapshot (342,895 rows; SHA-256 2efbfb87324fec2810f47833d2f9659a9c26da9037b5f639718058882dc40378).

Reason:
The research objective is a reproducible and stable source of truth, not preservation of an inaccessible historical byte snapshot at the cost of halting the project.

Rule:
A lock change must be explicit, documented, and based on repeated stable reproduction. Never silently mutate a pinned year.


---

## D-016 — Promote current 2020 snapshot

Decision:
Promote the repeatedly reproduced current Dukascopy 2020 M1 BID snapshot to canonical.

New canonical 2020:
- rows: 354,115
- SHA-256: 5616aafca39a2d3689911288c08fd5da8b2f3c3ea4a2bbdb8ca0cfbf690e9289

Superseded 2020:
- rows: 355,495
- SHA-256: 63892a47fec471a8bb4bbdd25ace162764fc56a1d6da02d458a535478fe6c6d3

Reason:
The previous 2020 snapshot is no longer consistently reproducible from the public feed, while the current snapshot reproduced identically across repeated independent full-year acquisitions. This follows D-015.


---

## D-017 — Fresh full snapshot is run source of truth

Decision:
For full-history research runs, acquire the entire 2016-2025 Dukascopy snapshot once and treat that exact acquired set of files and its manifest as the source of truth for that run.

The workflow still compares the fresh manifest to the prior lock and records every changed year, but differences do not block the run and do not trigger per-year retry loops.

Reason:
The public historical feed has shown that older yearly byte snapshots can change over time, and even repeated requests for the same year can differ. Discovering mismatches one year at a time created unnecessary friction without improving the research objective.

Operational rule:
- acquire the full snapshot once;
- validate each file structurally;
- record one consolidated manifest;
- audit all years against the prior lock in one report;
- continue labeling/features/baselines using the exact files from that same acquisition;
- preserve the fresh manifest with the results so the run remains reproducible as a recorded snapshot.


---

## D-018 — Prioritize volatility, session, and multi-timeframe structure

Decision:
The next expert-feature milestone prioritizes:
1. richer volatility/attainability features;
2. multi-timeframe trend and structure;
3. price location;
4. impulse/pullback/candle-sequence behavior;
5. session-transition context.

Reason:
The first non-sealed baseline run showed stable structure across TRAIN, VALIDATION, and DEVELOPMENT_TEST:
- high-volatility states had many-fold higher $5-target success rates than low-volatility states;
- Europe and US sessions materially outperformed Asia/LATE for target attainability;
- flat 60-minute momentum was consistently weaker than directional momentum;
- BUY performed best in UP states and SELL best in DOWN states, while opposite-direction states remained non-trivial.

Therefore the next feature work should refine those demonstrated contextual dimensions rather than add arbitrary indicators.

Evidence:
research/EXP-001_BASELINE_FINDINGS.md
research/EXP-001_EXPERT_FEATURE_MILESTONE_V2.md


---

## D-019 — Checkpoint expensive V2 features before analysis

Decision:
Split the long full-history workflow into two jobs:
1. acquisition / labeling / partitioning / V2 feature generation;
2. downstream baseline and model analysis from an uploaded checkpoint artifact.

Reason:
Run 36264651058 successfully generated every 2016-2024 V2 feature file, then the runner received a shutdown signal before the baseline stage completed. Recomputing all features after an unrelated late runner interruption is unnecessary and wasteful.

Operational rule:
- upload V2 features, partitioned labels, manifest, audit, and partition summary as a durable workflow artifact immediately after feature generation;
- downstream analysis downloads that checkpoint;
- later baseline/model failures must not require reacquiring or rebuilding V2 features.


---

## D-020 — First predictive model is logistic V1

Decision:
Run a deliberately simple logistic-regression milestone before gradient-boosted trees or neural models.

Frozen specification:
research/EXP-001_LOGISTIC_V1.md

Reason:
The research question is whether V2 expert-context features contain stable chronological predictive information. Logistic regression provides a transparent first test of discrimination, calibration, and probability monotonicity without introducing complex model capacity.

Operational rule:
- TRAIN only for fitting and preprocessing statistics;
- VALIDATION and DEVELOPMENT_TEST evaluated separately;
- FINAL_OOS 2025 remains inaccessible;
- BUY and SELL models are separate;
- weak or negative results are admissible and must not trigger silent feature or hyperparameter changes.


---

## D-021 — Advance to gradient-boosted trees after logistic V1

Decision:
Proceed to the preregistered next model class, gradient-boosted trees, without changing the V2 feature set or opening 2025.

Reason:
Logistic V1 demonstrated real chronological signal:
- BUY ROC-AUC remained 0.6359 on VALIDATION and 0.6194 on DEVELOPMENT_TEST;
- SELL discrimination was weaker, but higher-score tails still showed monotonic realized-success improvement;
- both directions exhibited substantial calibration drift across later regimes.

This supports testing nonlinear feature interactions while preserving the same labels, partitions, and sealed FINAL_OOS.

No live threshold is selected from Logistic V1.


---

## D-022 — Advance to calibration and abstention research

Decision:
Advance from GBT V1 to a dedicated calibration and abstention milestone while keeping the GBT feature/model configuration fixed and 2025 sealed.

Reason:
GBT V1 materially improved chronological discrimination over Logistic V1:
- BUY ROC-AUC: 0.7452 VALIDATION / 0.7378 DEVELOPMENT_TEST;
- SELL ROC-AUC: 0.7407 VALIDATION / 0.7452 DEVELOPMENT_TEST.

However, raw GBT probabilities are compressed and did not reach the descriptive 0.60 cutoff. Therefore the next question is not model complexity but whether the scores can be calibrated and converted into robust abstention bands without overfitting.

No live threshold is selected from GBT V1.


---

## D-023 — Freeze candidate abstention policies for robustness testing

Decision:
Stop model tuning after Calibration/Abstention V1 and move to robustness testing of fixed GBT score-band policies.

Reason:
Validation-derived BUY score bands transferred unusually well into DEVELOPMENT_TEST:
- top 10%: 30.96% -> 30.84%;
- top 5%: 33.42% -> 33.40%;
- top 2.5%: 34.54% -> 34.37%;
- top 1%: 36.38% -> 35.81%.

SELL also transferred usefully, although the validation extreme tail was not perfectly monotonic.

Platt calibration provided only small BUY improvements and slightly worsened SELL out-of-time calibration. Therefore the robust object for the next milestone is the fixed raw-score ranking / abstention policy, not further probability-map tuning.

2025 remains sealed.


---

## D-024 — Move to pre-OOS candidate-policy freeze

Decision:
Stop exploratory model/policy research and move to a pre-OOS candidate-policy freeze and specification audit before any 2025 access.

Reason:
All four fixed abstention policies retained positive lift in both years and every populated DEVELOPMENT_TEST quarter, with UTC-day bootstrap lift 95% confidence intervals entirely above 1 for BUY and SELL.

Important coverage caveat:
The strongest score bands fired almost exclusively in HIGH-volatility conditions and had essentially no LOW/MID-volatility or LATE-session coverage. Therefore robustness is demonstrated for the conditions in which the model selects, not uniformly across all regimes.

Next step:
freeze one candidate policy, document exact execution semantics and all remaining correctness/audit issues, hash the frozen specification, and only then decide whether the FINAL_OOS gate is ready.

2025 remains sealed.


---

## D-025 — Keep FINAL_OOS closed pending corrected revalidation and economics

Decision:
Do not freeze a final operating policy or open 2025 yet.

Audit findings:
1. the original label engine could mark a horizon complete despite an internal M1 gap;
2. same-partition Dec-31 decisions could lose next-year forward context;
3. predictive success rate alone is not enough to establish trading profitability because UNRESOLVED expiry P&L and execution costs are not yet modeled.

Actions:
- label coverage now requires exact contiguous M1 timestamps;
- same-partition year-boundary forward context is implemented without crossing partition boundaries;
- corrected 2016-2024 revalidation is running with no 2025 input;
- execution-economics semantics must be frozen and tested before the final OOS gate.

FINAL_OOS 2025 remains sealed.


---

## D-026 — Execution economics uses a BID-path cost-stress proxy

Decision:
Run Execution Economics V1 before any FINAL_OOS opening using the corrected Dukascopy BID-only history and frozen all-in round-trip cost stress scenarios.

Reason:
The admitted historical dataset does not contain Exness historical ASK quotes, spread, commission, or slippage. Therefore broker-exact fills cannot be reconstructed honestly.

Frozen operational rules:
- one global XAUUSD position at a time;
- no pyramiding or reversal while a trade is open;
- simultaneous BUY+SELL qualification => NO TRADE;
- SUCCESS gross +5;
- FAILURE gross -3;
- AMBIGUOUS conservatively -3;
- UNRESOLVED closes at exact 60-minute expiry BID close;
- all-in round-trip cost scenarios: 0.00, 0.10, 0.20, 0.30, 0.50 XAUUSD price units per trade;
- validation cutoffs derived from all eligible feature-complete decision rows, regardless of future ambiguity.

This is an economic screening proxy, not a broker-exact backtest.

2025 remains sealed.


---

## D-027 — Exness MT5 is a 2026 broker-validation source, not the historical source

Decision:
Do not use this Exness demo server as the primary 2023-2024 historical BID/ASK source.

Evidence:
The read-only monthly boundary probe scanned 45 monthly windows from Sep 2026 through Jan 2023.
The earliest sampled month returning XAUUSD BID+ASK ticks was Jan 2026.
All sampled 2025, 2024, and 2023 windows returned zero ticks with no MT5 error.

Use instead:
- Dukascopy BID+ASK for historical side-aware execution reconstruction;
- Exness MT5 2026 ticks for broker-specific spread/shadow validation.

No trading mutation occurred.


---

## D-028 — Execution Economics V1 does not open FINAL_OOS

Decision:
Do not freeze a combined operating policy and do not open 2025 after Execution Economics V1.

Reason:
No combined candidate passed the preregistered C20 economic gate.

Top-1% combined at C20:
- mean net expectancy: -0.0235 price units/trade;
- profit factor: 0.988;
- 2023 mean: +0.1548;
- 2024 mean: -0.0684;
- day-block bootstrap 95% interval: [-0.1890, 0.1620].

SELL-only top 1% was positive at C20, but direction-specific promotion was not preregistered and therefore must not be selected post hoc.

Next step:
historical side-aware BID/ASK execution reconstruction using Dukascopy, then a newly preregistered execution-economics V2.

2025 remains sealed.
