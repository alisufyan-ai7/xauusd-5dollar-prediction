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


---

## D-029 — Advance to Dukascopy BID/ASK Execution Economics V2

Decision:
Run a newly preregistered side-aware execution milestone before any FINAL_OOS opening.

Evidence and rationale:
- Execution Economics V1 did not pass the combined C20 advancement gate.
- Exness MT5 historical tick availability on the current demo server begins only in sampled 2026 history, so it cannot reconstruct 2023-2024.
- Dukascopy historical tick data provides timestamped BID and ASK together.
- A one-day XAUUSD BID/ASK smoke download for 2024-06-05 passed validation with the pinned dukascopy-node@1.50.0 path.

V2 rules:
- predictive model remains frozen;
- operational score cutoffs do not condition on future coverage_complete;
- top 10/5/2.5/1% policies only;
- BUY_ONLY, SELL_ONLY, COMBINED are preregistered;
- executable BUY uses ASK entry / BID exit;
- executable SELL uses BID entry / ASK exit;
- barriers are measured from executable entry;
- raw tick files are acquired only for required DEVELOPMENT_TEST UTC dates;
- additional friction stress is F0/F05/F10/F20;
- 2025 remains sealed.

Source specification:
research/EXP-001_EXECUTION_ECONOMICS_V2.md


---

## D-030 — Stop EXP-001 before FINAL_OOS; redesign executable target

Decision:
Do not open 2025 and do not promote any current policy.

Reason:
Execution Economics V2 modeled historical Dukascopy BID/ASK directly and found all preregistered policy/mode combinations negative overall, including at F0 before extra commission/slippage stress.

Top-1% COMBINED at F0:
- mean -0.3662 price units/trade;
- PF 0.8183;
- 2023 -0.1038;
- 2024 -0.4331;
- bootstrap 95% CI [-0.5563, -0.1817].

Top-1% SELL_ONLY at F0 was strongest but still negative overall:
- mean -0.1828;
- PF 0.9066;
- bootstrap 95% CI [-0.3921, +0.0068].

Conclusion:
The current predictive target is not sufficiently aligned with executable BID/ASK economics.

Next:
start a new experiment version whose labels/objective are defined directly from executable ASK/BID entry and exit mechanics before retraining.

2025 remains sealed.


---

## D-031 — Start EXP-002 with executable-side labels

Decision:
Stop modifying the EXP-001 target and start a new experiment version on a clean descendant branch.

Branch:
research/exp002-executable-target-v1

Reason:
EXP-001 demonstrated predictive ranking signal but failed side-aware historical execution economics. The failure showed that the BID-referenced target was misaligned with executable BUY/SELL mechanics.

EXP-002 freezes a new target before empirical results:
- decision after the current M1 close;
- entry at next M1 executable open;
- BUY enters ASK and evaluates target/adverse on BID;
- SELL enters BID and evaluates target/adverse on ASK;
- 60-minute horizon;
- +5 target / -3 adverse measured from executable entry;
- unresolved exits retain executable expiry P&L;
- paired Dukascopy M1 BID+ASK is primary data;
- tick data is reserved only for same-minute ordering ambiguity;
- spread-aware causal features are added;
- fixed EXP-001 GBT hyperparameters are reused without model search;
- 2025 remains sealed.

Initial non-sealed EXP-002 run:
36320442383


---

## D-032 — Advance EXP-002 to sequential execution economics

Decision:
Advance EXP-002 from initial predictive validation to sequential execution-economics testing without changing the model, target, features, or score bands.

Evidence:
Corrected run 36321788362 completed successfully.

DEVELOPMENT_TEST discrimination:
- BUY ROC-AUC 0.7392, PR-AUC 0.2315;
- SELL ROC-AUC 0.7482, PR-AUC 0.2454.

Fixed VALIDATION-derived top-1% realized success:
- BUY 29.05%;
- SELL 33.07%.

The executable-side target therefore retains meaningful chronological ranking signal.

Next:
run sequential BUY_ONLY / SELL_ONLY / COMBINED economics using the frozen executable entry, barrier, expiry, one-position-at-a-time, and friction semantics.

2025 remains sealed.


---

## D-033 — EXP-002 V1 fails sequential economics

Decision:
Do not open FINAL_OOS 2025 and do not promote any EXP-002 V1 policy.

Evidence:
Run 36324128764 completed successfully.

No preregistered top 10/5/2.5/1% BUY_ONLY, SELL_ONLY, or COMBINED policy passed F10.

Least-negative policy:
SELL_ONLY top 1% at F10:
- mean net -0.3252 price units/trade;
- PF 0.8360;
- 2023 -0.0895;
- 2024 -0.3967;
- bootstrap 95% CI [-0.5159, -0.1290].

Even at F0, SELL_ONLY top 1% remained negative overall.

Conclusion:
predictive ranking quality alone is insufficient; the current score-to-trade policy does not create positive sequential expectancy.

Next:
diagnose non-sealed 2016-2024 failure modes before any new experiment design.

2025 remains sealed.


---

## D-034 — Diagnose EXP-002 economic failure before designing EXP-003

Decision:
Do not design or train an economic-value model yet.

First run a frozen descriptive diagnosis of why EXP-002 preserves classifier ranking but loses money sequentially.

Diagnostic scope:
- outcome decomposition;
- unresolved expiry P&L;
- score deciles and top-10% tail slices;
- year/quarter drift;
- session and volatility regime decomposition;
- spread decomposition;
- holding-time behavior;
- raw-signal clustering and sequential suppression;
- explicit expected-value identity.

No new thresholds, direction promotion, or model tuning are allowed from this milestone.

Workflow:
36328166429

2025 remains sealed.


---

## D-035 — Start EXP-003 economic-value model

Decision:
Start a new clean descendant experiment on branch:

research/exp003-economic-value-v1

EXP-003 changes the prediction objective, not the feature set.

The frozen architecture models, separately for BUY and SELL:
- P(SUCCESS);
- P(FAILURE);
- P(UNRESOLVED);
- expected executable expiry P&L conditional on UNRESOLVED.

It then computes:

EV_GROSS =
5*P(SUCCESS)
-3*P(FAILURE)
+P(UNRESOLVED)*E[UNRESOLVED expiry P&L]

Primary decision score:
EV_F10 = EV_GROSS - 0.10.

Reason:
EXP-002 diagnosis showed that high SUCCESS probability did not sufficiently penalize adverse-barrier FAILURE probability, while UNRESOLVED expiry P&L was not the primary economic drag.

Frozen abstention thresholds:
- T0: EV_F10 > 0.00
- T25: EV_F10 >= 0.25
- T50: EV_F10 >= 0.50
- T75: EV_F10 >= 0.75

Operational evaluation remains one global position at a time so clustered minute observations are not treated as independent opportunities.

No new features or hyperparameter search are permitted in EXP-003 V1.

2025 remains sealed.


---

## D-036 — EXP-003 V1 fails sequential threshold economics

Decision:
Do not nominate any EXP-003 V1 policy for pre-OOS candidate freeze.

Evidence:
Run 36337595939 completed successfully.

No preregistered T0/T25/T50/T75 policy in BUY_ONLY, SELL_ONLY, or COMBINED passed the frozen advancement gates.

Representative T0:
- BUY_ONLY mean NET_F10 -0.4151, PF 0.7583;
- SELL_ONLY -0.4040, PF 0.7703;
- COMBINED -0.4142, PF 0.7616.

Higher EV thresholds did not rescue economics and often worsened expectancy or reduced trade counts below the preregistered minimum.

Conclusion:
explicit EV scoring over the unchanged EXP-002 feature set is still misaligned with realized executable P&L.

Next:
diagnose EV calibration/failure mechanisms before considering a new preregistered experiment.

2025 remains sealed.


---

## D-037 — Diagnose EXP-003 EV miscalibration before EXP-004

Decision:
Do not design EXP-004 yet.

First complete a frozen component-level diagnosis of why EXP-003 predicted EV_F10 is more optimistic than realized executable NET_F10.

Diagnostic scope:
- predicted versus realized SUCCESS / FAILURE / UNRESOLVED probabilities;
- unresolved-expiry-P&L regression error;
- counterfactual EV decomposition;
- class-probability calibration drift in 2022 / 2023 / 2024;
- EV error distribution and error by realized outcome;
- sequential opportunity-level calibration;
- frozen-feature distribution shift;
- positive-EV tail support relative to TRAIN.

TRAIN feature-distribution reference uses the same deterministic every-5th eligible TRAIN-row sampling rule frozen before results.

No recalibration, threshold tuning, feature selection, or new model fitting is permitted.

Workflow:
36348182305

2025 remains sealed.


---

## D-038 — EXP-003 EV failure is tail miscalibration plus distribution shift

Decision:
Seal the EXP-003 diagnosis before designing EXP-004.

Evidence:
Run 36348182305 completed successfully.

Dominant mechanisms:
1. positive-EV tails overpredict SUCCESS and underpredict FAILURE;
2. calibration error worsens as EV threshold rises;
3. replacing predicted class probabilities with realized class frequencies flips modeled EV strongly negative;
4. replacing only unresolved-expiry P&L does not remove the optimism;
5. 2024 shows substantial volatility/spread/attainability feature-distribution shift;
6. positive-EV rows frequently lie outside TRAIN 1%-99% feature support;
7. sequential opportunity filtering does not resolve the calibration gap.

Conclusion:
EXP-004, if started, must explicitly address probability calibration under temporal distribution shift and out-of-support uncertainty. It must not be a threshold retune of EXP-003.

2025 remains sealed.


---

## D-039 — Start EXP-004 shift-aware calibrated EV

Decision:
Start EXP-004 on branch:

research/exp004-shift-aware-calibrated-ev-v1

EXP-004 keeps:
- executable labels;
- feature vector;
- base learner;
- unresolved-expiry regressor;
- EV thresholds;
- sequential execution semantics.

It changes only:
1. class-probability calibration using strictly expanding-window out-of-time TRAIN predictions;
2. explicit TRAIN-support abstention.

Frozen calibration:
- OOT folds predict 2017, 2018, 2019, 2020, 2021 using only earlier years;
- multinomial LogisticRegression on log base probabilities;
- C=1.0, lbfgs, max_iter=1000.

Frozen support gate:
- outside_count <= 2;
- total normalized exceedance <= 1.0;
- TRAIN support reference from every-5th eligible TRAIN rows.

Experimental arms:
- A RAW_EV benchmark;
- B calibrated EV;
- C calibrated EV + support gate.

Only B/C may advance.

2025 remains sealed.


---

## D-040 — EXP-004 calibration/support gating does not rescue economics

Decision:
Do not freeze any EXP-004 candidate and do not access FINAL_OOS 2025.

Evidence:
Run 36394304605 completed successfully.

No ARM B (calibrated EV) or ARM C (calibrated EV + support gate) policy passed the frozen advancement rules.

Key result:
- calibration improved aggregate multiclass fit;
- SELL aggregate EV calibration gap was nearly eliminated;
- nevertheless T0 sequential economics remained materially negative;
- higher calibrated-EV thresholds became extremely sparse;
- support gating rejected ~16.9% of DEVELOPMENT_TEST rows but did not make T0 economics positive.

Conclusion:
the EXP-003 feature representation / base learner / target combination remains insufficient even after strictly chronological calibration and explicit support-aware abstention.

Next:
design a materially different experiment rather than retuning EXP-004 thresholds, support gates, or calibrator.

2025 remains sealed.


---

## D-041 — Start EXP-005 downside-first direct economic model

Decision:
Start EXP-005 on branch:

research/exp005-downside-first-competing-risk-v1

EXP-005 materially changes the prediction objective while retaining the frozen executable semantics and feature representation.

Models:
1. direct executable gross-P&L regressor;
2. binary EARLY_FAILURE classifier for adverse-barrier failure within <=5 minutes.

Frozen downside gates are derived only from VALIDATION 2022 predicted EARLY_FAILURE-risk quantiles:
- Q50;
- Q25;
- Q10.

Experimental arms:
- DIRECT_ONLY;
- DIRECT_EF_Q50;
- DIRECT_EF_Q25;
- DIRECT_EF_Q10.

Direct economic thresholds remain T0/T25/T50/T75.

Reason:
EXP-004 showed that probability recalibration and support gating alone did not rescue economics. Prior diagnostics showed rapid <=5-minute outcomes were strongly negative, so EXP-005 tests direct economic prediction plus explicit rapid-downside avoidance.

2025 remains sealed.


---

## D-042 — EXP-005 early-failure signal is useful but insufficient

Decision:
Do not freeze any EXP-005 candidate and do not access FINAL_OOS 2025.

Evidence:
Corrected run 36445233132 completed successfully.

Findings:
- direct executable-P&L regression has near-zero correlation with realized gross P&L;
- the <=5-minute EARLY_FAILURE classifier has useful discrimination (DEV ROC-AUC ~0.81-0.84);
- downside gating sharply reduces or eliminates observed early failures;
- however, admissible low-risk opportunities become too sparse;
- DIRECT_ONLY remains economically negative, especially in 2024;
- no arm satisfies trade-count, two-year positivity, bootstrap, and concentration gates.

Conclusion:
rapid downside risk is predictable, but the current frozen 48-feature representation does not provide enough positive-trade-quality information to support robust economics.

Next:
a materially richer market-state representation is required in a new preregistered experiment.

2025 remains sealed.


---

## D-043 — Start EXP-006 causal path-state representation

Decision:
Start EXP-006 on branch:

research/exp006-causal-path-state-v1

Purpose:
isolate whether the current market-state representation is the limiting factor.

Design:
- REP_A_BASE48: exact EXP-005 feature set, benchmark only;
- REP_B_PATH84: BASE48 plus 36 frozen causal price-path features;
- same direct executable-P&L regressor;
- same <=5-minute EARLY_FAILURE classifier;
- same validation-derived Q50/Q25/Q10 risk gates;
- same T0/T25/T50/T75 economic thresholds;
- same sequential execution and advancement gates.

The 36 added features measure, for 5/15/30/60/120/240-minute windows:
- path efficiency;
- sign-change rate;
- jump concentration;
- time since local high;
- time since local low;
- synthetic-bar body/range ratio.

No external events/news are added in EXP-006 so representation effects remain attributable.

2025 remains sealed.


---

## D-044 — EXP-006 PATH84 does not improve the edge

Decision:
Do not freeze any EXP-006 candidate and do not access FINAL_OOS 2025.

Evidence:
Run 36467825948 completed successfully.

Findings:
- PATH84 did not materially improve direct-P&L correlation;
- PATH84 did not materially improve EARLY_FAILURE ROC-AUC / PR-AUC;
- PATH84 T0 sequential economics were worse than BASE48;
- downside-gated PATH84 policies remained sparse and unstable;
- no PATH84 policy passed.

Conclusion:
adding more hand-crafted causal path-state features to the same tree-model family is not justified by evidence.

Next:
change model family, target formulation, or timestamp-safe external information in a new preregistered experiment.

2025 remains sealed.


---

## D-045 — Start EXP-007 causal sequence model

Decision:
Start EXP-007 on branch:

research/exp007-causal-sequence-v1

Purpose:
test whether ordered M1 path information contains executable trade-quality signal that the completed tree-based feature representations did not capture.

Frozen design:
- trailing 60 synchronized M1 bars;
- six causal BID/ASK-derived sequence channels;
- exact BASE48 static context;
- small fixed temporal CNN;
- separate direct executable-P&L and <=5-minute EARLY_FAILURE networks;
- every-20th eligible TRAIN sampling;
- fixed Adam optimization for 8 epochs;
- validation-derived Q50/Q25/Q10 downside gates;
- unchanged T0/T25/T50/T75 thresholds;
- unchanged sequential execution and advancement gates.

No external event/news context is added in EXP-007.

2025 remains sealed.


---

## D-046 — EXP-007 sequence model fails executable-P&L economics

Decision:
Do not freeze any EXP-007 candidate and do not access FINAL_OOS 2025.

Evidence:
Run 36485293055 completed successfully.

Findings:
- BUY direct-P&L Pearson is negative and its high-score tail is catastrophically miscalibrated;
- SELL direct-P&L Pearson improves modestly to about +0.067 but still fails economic gates;
- sequence-model EARLY_FAILURE ranking remains strong (ROC-AUC about 0.88);
- sequential BUY economics collapse near -3 per trade in higher-score bands;
- downside-gated arms are too sparse and remain negative;
- no policy passes.

Conclusion:
ordered 60-minute M1 sequence learning does not solve the positive trade-quality prediction problem under the current targets and economics.

Next:
change the target/information problem rather than tune the EXP-007 architecture.

2025 remains sealed.


---

## D-047 — Start EXP-008 competing-hazard target formulation

Decision:
Start EXP-008 on branch:

research/exp008-competing-hazard-v1

Purpose:
replace unreliable direct-P&L prediction with a calibrated competing-hazard representation of target-first versus adverse-first timing.

Frozen classes:
- SUCCESS within 0-5 / 6-15 / 16-30 / 31-60 minutes;
- FAILURE within 0-5 / 6-15 / 16-30 / 31-60 minutes;
- UNRESOLVED at 60 minutes.

Inputs:
- exact BASE48 only.

Probability calibration:
- strictly out-of-time TRAIN folds 2017-2021;
- multinomial logistic mapping of nine-class base probabilities.

Economic score:
- +5 * aggregate calibrated SUCCESS probability;
- -3 * aggregate calibrated FAILURE probability;
- unresolved probability times frozen unresolved-expiry P&L prediction;
- minus F10 friction.

Optional frozen early-failure gates:
- validation Q50 / Q25 / Q10 of calibrated F_00_05 probability.

No time-bin economic bonus/penalty is allowed.

2025 remains sealed.


---

## D-048 — EXP-008 hazard formulation improves calibration but not economics

Decision:
Do not freeze any EXP-008 candidate and do not access FINAL_OOS 2025.

Evidence:
Run 36616276558 completed successfully.

Findings:
- nine-class competing-hazard calibration is broadly reasonable;
- SELL aggregate EV calibration gap is small;
- T0 sequential economics remain negative across BUY/SELL/COMBINED;
- early-failure gating reduces sample size but does not create robust positive economics;
- a T25 SELL pocket is positive but contains only 10 trades and fails bootstrap, sample-size, and concentration gates;
- no policy passes.

Conclusion:
target/adverse timing improves probability representation but does not solve price-only trade-quality prediction.

Next:
test a separately preregistered timestamp-safe exogenous information source rather than continue reformulating the same price-only state.

2025 remains sealed.


---

## D-049 — Root-cause reset to event-driven dynamic trade management

Decision:
Stop extending the EXP-001→EXP-008 minute-by-minute fixed-barrier lineage.

Start root reset on branch:

research/root-reset-event-driven-v1

Core corrections:
- event-driven CUSUM continuation candidates instead of every-minute scoring;
- direct $5 attainability target via executable MFE_60;
- regime/structure-adaptive initial stop;
- retain downside-risk veto;
- treat +$3 as a management trigger, not automatically the final target;
- compare HOLD_TO_5, BE_AT_3, and TAKE_3;
- keep 2025 sealed.

Dynamic stop:
max(
  trailing 15-minute structure invalidation + 0.25 * ATR15_PROXY,
  1.5 * ATR15_PROXY
)

Reject candidate if initial stop exceeds $5/1.5 = $3.333333....

Opportunity threshold:
choose once on VALIDATION 2022 from {0.50,0.60,0.70,0.80};
requires >=100 executed validation trades and positive mean NET_F10 under HOLD_TO_5.

If no validation threshold qualifies, do not access DEVELOPMENT_TEST.

2025 remains sealed.


---

## D-050 — Reset V1 stops at validation; diagnose gate intersection

Decision:
Close Root-Cause Reset V1 at VALIDATION.

Run 36629144070 succeeded technically but selected no opportunity threshold.

No DEVELOPMENT_TEST access occurred.

Important finding:
- event-driven OPPORTUNITY_5 ranking is meaningful (BUY ROC-AUC 0.773, SELL 0.759);
- zero trades qualified because the frozen combined gate was too restrictive;
- absolute opportunity thresholds started at 0.50 despite ~12.8% base rate;
- about half of events fail the $3.333 stop-admissibility cap;
- redesigned EARLY_DAMAGE is only ~0.6% prevalent and its Q50 cutoff is extremely small.

Next:
perform validation-only gate-overlap diagnosis before specifying V2.

Do not access 2023-2024 or 2025 during that diagnosis.


---

## D-051 — Dynamic stop cap conflicts with $5 opportunity ranking

Decision:
Do not proceed to DEVELOPMENT_TEST with Reset V1.

Validation-only diagnosis run 36687708188 shows:
- OPPORTUNITY_5 ranking is strongly monotonic and useful;
- the frozen stop-admissibility rule is anti-correlated with opportunity quality;
- high-score events are high-volatility events with both larger MFE and larger MAE;
- the $3.333 stop cap removes almost all top-decile opportunities;
- early-damage veto is secondary and weak for SELL.

Therefore the fixed minimum-$5 / 1.5R geometry is itself a root-cause error.

Next:
design Reset V2 around joint favorable/adverse excursion prediction and regime-adaptive reward/risk.

Do not access 2023-2024 or 2025 yet.


---

## D-052 — Start Root-Reset V2 joint excursion geometry

Decision:
Start Root-Reset V2 on branch:

research/root-reset-v2-joint-excursion

Reason:
Reset V1 validation diagnosis showed that fixed stop admissibility was anti-correlated with $5 opportunity quality.

V2 changes the geometry, not the event sampler:
- predict MFE60 q50/q70/q80;
- predict MAE60 q50/q70/q80;
- require MFE q70 >= $5;
- derive target and stop jointly from predicted excursion quantiles;
- require TARGET/STOP >= 1.20;
- compare G50/G70/G80 with HOLD and PROTECT_AT_3 management;
- validate once on 2022;
- access 2023-2024 only if a policy qualifies;
- keep 2025 sealed.

2025 remains sealed.


---

## D-053 — Raw excursion quantiles are not executable geometry

Decision:
Close Root-Reset V2 at VALIDATION.

Run 36696884026 completed successfully.

No policy qualified, so 2023-2024 were not accessed.

Key findings:
- MFE/MAE quantile models have meaningful moderate ranking signal;
- G50-H is mildly positive but has only 17 trades;
- G70/G80 targets and stops are too wide relative to realized executable paths;
- raw upper quantiles should not be used literally as target/stop distances;
- +$3 breakeven protection helps some wide geometries but hurts G50.

Next:
perform validation-only excursion calibration diagnosis before defining any V3 policy.

2025 remains sealed.


---

## D-054 — Continuation entry quality is the remaining bottleneck

Decision:
Do not define a V3 by merely shrinking excursion predictions or loosening reward/risk gates.

Validation-only calibration run 36700831693 shows:
- MFE q70 requires ~0.54-0.61 shrinkage to match median attainable reward;
- MFE q80 requires ~0.39-0.45 shrinkage;
- MAE q50 is already well calibrated as central adverse excursion;
- structural invalidation is not a better risk anchor;
- calibrated median reward/risk remains below 1 across the continuation-event population.

Conclusion:
the remaining root cause is setup/entry quality, not primarily target or stop calibration.

Next admissible research must change the setup family and/or add genuinely new timestamp-safe information before candidate generation.

Do not access 2023-2024 or 2025.


---

## D-055 — Screen distinct structural setup families before new modeling

Decision:
Start Root-Reset V3 as a TRAIN-only setup-family screening milestone.

Branch:
research/root-reset-v3-setup-screening

Families:
- A_BREAKOUT_RETEST
- B_SWEEP_RECLAIM
- C_IMPULSE_PULLBACK

Scope:
- synchronized XAUUSD BID/ASK M1;
- 2016-2021 only;
- no ML model;
- no stop/target optimization;
- no 2022-2025 access.

Selection:
a family must first pass frozen minimum count, yearly stability, positive path-edge, and MFE/MAE criteria.
If multiple pass, use the frozen minimum-year-edge ranking.

Purpose:
determine whether a mechanically defined entry family materially improves path quality before any further model work.

2022-2025 remain untouched.


---

## D-056 — Exhaust price-only setup invention; require new causal information

Decision:
Do not promote any Root-Reset V3 structural setup family.

TRAIN-only run 36711334369 shows:
- breakout-retest: 0/6 positive YEAR_PATH_EDGE years;
- sweep-reclaim: 0/6;
- impulse-pullback: 0/6;
- all overall median MFE/MAE ratios are far below 1.10.

Conclusion:
the current price-only setup search is exhausted.

Next admissible work:
establish a timestamp-safe exogenous context layer before candidate generation, beginning with scheduled macro-event and session/liquidity data, with cross-market context only if reproducible and causally aligned.

Do not access 2022-2025 yet.


---

## D-057 — Admit Badar trading repository as research source

Owner decision:
Explicitly admit private repository:

alisufyan-ai7/unpack-human-trading-strategies-claude

as a research source for this project.

Boundary:
- source-layer material outside derived/ may be used as evidence of what Badar said/showed, with its documented uncertainty;
- derived/ may be used only as Claude interpretation/engineering hypothesis and must never be attributed to Badar;
- no other private repository/chat/project/account memory is admitted by this decision.

This admission allows future preregistered research to formalize a Badar-Core setup hypothesis.

It does not authorize trading, post-hoc tuning, or opening sealed periods.

See research/ADMITTED_SOURCE_BADAR_TRADING_REPO.md.


---

## D-058 — Start source-grounded Badar-Core TRAIN experiment

Decision:
Start Root-Reset V4 on branch:

research/root-reset-v4-badar-core

Source basis:
the owner-admitted repository
alisufyan-ai7/unpack-human-trading-strategies-claude

Only its source layer is used to define the experiment.
Claude-derived rulebook/defaults are excluded.

V4 tests one narrow deterministic translation:
- H1-led HTF directional context;
- frozen Asian/London session liquidity;
- active H1 FVG location;
- M15 liquidity sweep + close back inside;
- M5 two-close MSS;
- displacement FVG;
- midpoint retracement limit entry;
- nearest opposing session liquidity target >= $5;
- structural and micro stop hypotheses measured separately.

Scope:
TRAIN 2016-2021 only.

No 2022-2025 access.
No ML.
No post-hoc parameter tuning.

See research/ROOT_RESET_V4_BADAR_CORE_PREREGISTRATION.md.


---

## D-059 — V4 translation too restrictive before entry

Run 36768684222 completed successfully.

V4 produced:
- 1,508 NY dates;
- 627 M15 liquidity sweeps;
- 364 sweeps at active H1 FVG;
- 135 M15 close-back confirmations;
- 24 M5 two-close MSS;
- 16 MSS + displacement FVG;
- 3 candidates with structural target >= $5;
- 3 midpoint limit orders;
- 0 fills.

Decision:
Do not interpret V4 as an economic failure of Badar's method.
The deterministic translation became too restrictive before entry.

Next:
perform a TRAIN-only translation diagnosis comparing source-observed execution alternatives
(one-close/M3/M1 confirmation, direct-close versus retracement entry, and broader structural liquidity targets)
without touching 2022-2025.

Do not loosen V4 post hoc.


---

## D-060 — Run TRAIN-only V4 translation diagnosis

Decision:
After V4 produced zero fills because its deterministic translation became too restrictive before entry, run a separate TRAIN-only translation diagnosis.

Frozen diagnosis:
research/ROOT_RESET_V4_TRANSLATION_DIAGNOSIS.md

Implementation:
scripts/diagnose_root_reset_v4_translation.py

Scope:
- 2016-2021 only;
- reuse V4 unchanged through M15 sweep + close-back confirmation;
- diagnose one-close M5, one-close M3, one-close M1, direct-close entry versus FVG-midpoint fill, and broader structural target availability;
- no P&L-based policy selection;
- no 2022-2025 access.

Purpose:
measure where V4 diverged from source-observed Badar execution before defining any V5.

The next chat/session must read GitHub continuity and decision files instead of relying on prior chat memory.


---

## D-061 — V4 translation diagnosis confirms pre-entry source-fidelity bottlenecks

Accepted TRAIN-only diagnosis run:

36779728544

The accepted run used a same-snapshot reproducibility guard:
- reacquire/synchronize 2016-2021 only;
- run frozen V4 reference and the diagnosis sequentially on the same files;
- assert identical M15 close-back population;
- retain compact raw/synchronized SHA-256 identities.

The frozen V4 reference reproduced the original funnel exactly, including:
- 627 M15 sweeps;
- 364 active-H1-FVG overlaps;
- 135 M15 close-back confirmations;
- 24 two-close M5 MSS;
- 16 MSS + displacement FVG;
- 3 session targets >= $5;
- 0 fills.

Diagnosis findings from the same 135 confirmations:
- one-close M5: 33 confirmations, recovering 9 cases missed by V4 C2;
- one-close M3: 47;
- one-close M1: 83;
- M3 and/or M1 recover 63 cases where V4 C2 is absent;
- for V4 C2, direct-close entry exists in 24 cases, while only 9 midpoint fills occur among 16 FVG cases;
- 15/24 C2 direct entries exist when the midpoint entry does not fill;
- 8/24 C2 direct entries have all session targets < $5 but at least one broader previous-day/H1/H4 structural target >= $5.

Decision:
Do not select a profitability policy or mechanically choose the diagnostic alternative with the largest population.

The largest absolute translation loss after frozen M15 close-back is the two-close M5 MSS gate (135 -> 24), while mandatory displacement-FVG/midpoint entry and session-only >=$5 targeting compound the restriction later.

Interpret V4 zero fills as a translation-coverage failure before economic evaluation, not an economic rejection of Badar's source method.

Next:
define one V5 translation from the admitted Badar source layer using evidence strength and observed execution practice rather than diagnostic outcome counts, preregister it before any TRAIN economic run, and keep 2022-2025 sealed.

See research/ROOT_RESET_V4_TRANSLATION_DIAGNOSIS_FINDINGS.md.


---

## D-062 — Freeze Root-Reset V5 Badar A+ source-fidelity translation

Decision:
Start Root-Reset V5 on branch:

research/root-reset-v5-badar-source-fidelity

Frozen preregistration:
research/ROOT_RESET_V5_BADAR_SOURCE_FIDELITY_PREREGISTRATION.md

Reason:
D-061 showed that V4 failed before economic evaluation because its mechanical translation added restrictive choices that were not uniquely required by the admitted Badar source layer.

V5 is resolved from source evidence rather than from whichever V4 diagnostic branch produced the most candidates.

Key frozen changes after the unchanged V4 M15 close-back stage:
- use source-valid one-close MSS on M5/M3;
- allow M3 as the documented fallback execution timeframe;
- still require a clean displacement FVG;
- enter at the FVG proximal/start edge rather than its midpoint;
- use only the taught structural stop beyond the sweep;
- use a final HTF liquidity target from previous-day/H1/H4 structure;
- require target distance >= $5 and structural target/stop RR >= 3;
- do not use M1/direct-close merely because those variants had greater diagnostic coverage;
- retain V4-style low-frequency candidate spacing and TRAIN-only advancement gates.

Source basis:
- notes/videos/dOdvKLaBPaA.md
- notes/videos/6en-a8-p48w.md
- notes/videos/CzyCyduZqOk.md
- notes/videos/TYY0aNKVnZ8.md
- PLAYBOOK.md S01
- LIVE_TRADING_OBSERVATIONS.md only as supporting observed-practice evidence, without overriding the taught A+ sequence.

Scope:
- 2016-2021 TRAIN only;
- no ML;
- no post-hoc threshold search;
- 2022-2025 remain sealed.

Next:
implement the frozen V5 specification, add a manual historical workflow mode, run it once on 2016-2021, inspect the funnel/economics, and record the result before any further formulation change.


---

## D-063 — Stop V5 at TRAIN; audit upstream source-location coverage before V6

Accepted run:
36783834169

Result:
- V5 completed successfully on 2016-2021 TRAIN only;
- 137 M15 close-back confirmations;
- 39 source-valid M5/M3 MSS + displacement-FVG triggers;
- 21 triggers with structural target distance >= $5;
- 9 with target/structural-stop RR >= 3;
- 9 proximal-edge orders;
- 6 fills;
- entry-population gate failed;
- structural-stop gate failed;
- no 2022 validation authorized.

Critical design finding:
V5 reused the >=180 filled-trade advancement gate, but its unchanged V4 upstream sampler produced only 137 M15 close-back confirmations in total. Therefore the count gate was mathematically unreachable even under perfect downstream conversion.

Decision:
Do not lower the count gate post hoc and do not tune downstream entry/target parameters to manufacture more trades.

The next scientific step is a TRAIN-only source-location coverage audit focused on whether V4/V5's mandatory session-liquidity sweep + active H1 FVG conjunction is materially narrower than Badar's admitted source-layer location map.

The audit may compare source-supported location/liquidity families descriptively, including session liquidity, PDH/PDL, confirmed H4 swing liquidity, and active H1/H4 FVGs. OB/breaker logic may be included only if a deterministic definition can be frozen from source evidence without arbitrary tuning.

No profitability-policy selection.
No 2022-2025 access.

See research/ROOT_RESET_V5_BADAR_SOURCE_FIDELITY_FINDINGS.md.


---

## D-064 — Pause new strategy/model experiments until information parity is built

Decision:
Do not continue the V6 rule-translation loop or start another price-dominant model yet.

Reason:
An information audit against the admitted Badar source layer shows that the current project is not information-complete even relative to Badar's observed decision environment.

The project currently has strong XAUUSD historical BID/ASK price/spread data and many price-derived features, but is missing or not using several channels Badar demonstrably consults:
- raw M1 volume exists but is not represented in the main intelligence feature layer;
- DXY intraday context is absent;
- US-yield context is absent;
- timestamp-safe macro-event schedules and release surprises are absent;
- richer liquidity/location-map state is fragmented rather than unified;
- scenario/confidence state and trade/account state are not represented;
- exact historical Exness microstructure before 2026 is unavailable from the probed server.

Decision boundary:
Prior negative experiments show that the tested price-only/price-dominant representations did not produce robust executable edge. They do not establish that a richer intelligent system cannot match or outperform a skilled discretionary trader.

Next milestone:
Design and preregister an Information Parity Layer V1 before training any new profitability model.

Minimum information package:
1. XAUUSD causal BID/ASK sequence + volume + multi-timeframe structure + spread/session/liquidity state;
2. intraday DXY/USD context;
3. intraday US-yield/rate context;
4. timestamp-safe macro-event schedule and, where reproducible, actual/forecast/surprise;
5. participation/microstructure state;
6. separate trade/account/risk state.

After parity:
run a finite Badar-decision recognition and information-channel ablation benchmark before freezing one economic experiment.

Do not endlessly add models or thresholds.
Do not access 2022-2025 under this decision.

See research/INTELLIGENT_SYSTEM_INFORMATION_AUDIT.md.


---

## D-065 — Freeze five-stage Information Parity V1 roadmap before implementation

Decision:
The exact five-stage plan is now frozen before any new external-data acquisition, information-layer implementation, or profitability modeling begins.

Roadmap:
research/INFORMATION_PARITY_V1_ROADMAP.md

Stages:
1. information-source feasibility audit;
2. build Information Parity Layer V1;
3. Badar decision-recognition benchmark;
4. information-channel ablation;
5. one intelligent economic experiment.

Anti-rat-race rule:
- do not skip stages;
- do not iterate model families indefinitely;
- do not loosen economic gates post hoc;
- if richer information does not improve expert-state recognition, stop and diagnose information rather than tune models;
- if the one frozen economic experiment fails, a new experiment requires a new scientific hypothesis.

Immediate next action:
create a dedicated Information Parity V1 branch and preregister Stage 1 before acquiring/integrating new external historical data.

2022-2025 remain sealed.


---

## D-066 — Start Information Parity V1 Stage 1 on dedicated branch

Branch:
research/information-parity-v1

Frozen preregistration:
research/INFORMATION_PARITY_V1_STAGE1_SOURCE_FEASIBILITY_PREREGISTRATION.md

Decision:
Begin Stage 1 of the five-stage Information Parity V1 roadmap.

Stage 1 is a source-feasibility audit only. It must classify the following channels before full integration:
- DXY / broad USD intraday context;
- US Treasury / rate intraday context;
- scheduled macro-event calendar;
- macro release actual/forecast/previous/surprise feasibility;
- Dukascopy XAUUSD M1 volume semantics;
- targeted XAUUSD tick-microstructure feasibility.

Source admission is based on timestamp integrity, point-in-time causality, reproducibility, semantics, historical coverage, missingness, access/licensing practicality and alignment risk — not on trading P&L.

No profitability model, backtest, threshold search or source selection by future XAUUSD outcome is permitted in Stage 1.

Only tiny targeted samples may be used when necessary to verify schema/timestamp/coverage. No full multi-source TRAIN integration occurs until Stage 2 is separately specified.

2022-2025 XAUUSD evaluation periods remain sealed.


---

## D-067 — Complete Information Parity V1 Stage 1 and freeze Stage 2 source set

Accepted final source-feasibility probe:
- workflow run: 36986414645
- status: SUCCESS
- artifact: information-parity-stage1-probes
- artifact id: 11217188926
- artifact digest: sha256:27ff2ed0f4d03a6392a479208ad9d2a80bd467d45fe5a2b2d46113aa3d7f8821
- sealed XAUUSD periods accessed: none

Final Stage 1 channel verdicts:
- C1 DXY / broad USD intraday: ADMITTED WITH LIMITATION using SYNTHETIC_DXY_DUKASCOPY_BID;
- C2 US Treasury / rate intraday: DEFERRED;
- C3 scheduled macro-event calendar: ADMITTED WITH LIMITATION using composite first-party U.S. release archives/schedules;
- C4 macro actual/forecast/previous/surprise: DEFERRED;
- C5 XAUUSD M1 volume: ADMITTED WITH LIMITATION as Dukascopy provider participation/volume proxy;
- C6 XAUUSD tick microstructure: ADMITTED WITH LIMITATION for targeted use.

Important evidence:
- synthetic DXY had 1,417 / 1,419 / 1,404 synchronized M1 rows on the fixed 2016/2019/2021 anchor days;
- where direct Dukascopy DXY exists, synthetic-vs-direct level correlation was 0.99845 in 2019 and 0.99978 in 2021, with first-difference correlation 0.94616 and 0.91796;
- US T-Bond CFD had no 2016 anchor data and material later gaps;
- the frozen IEF fallback probe returned zero rows on all three anchor days, ending Stage 1 rate-source hunting;
- XAUUSD M1 provider volume is nonzero and side-specific in all fixed samples;
- targeted XAUUSD tick windows succeeded with 9,190 rows in 2016 and 27,097 rows in 2021, including BID/ASK and askVolume/bidVolume.

Decision:
Stage 1 is complete. Stage 2 design is authorized because the frozen minimum conditions are satisfied: XAUUSD historical state exists, M1 provider volume is characterized for limited use, at least one cross-market channel (synthetic DXY) is admitted, and a scheduled macro-event calendar is admitted.

Frozen Stage 2 source set:
- XAUUSD synchronized M1 BID/ASK OHLC;
- spread;
- Dukascopy XAUUSD M1 provider volume;
- raw XAUUSD causal sequences / multi-timeframe transforms;
- source-supported structural/session/liquidity state;
- SYNTHETIC_DXY_DUKASCOPY_BID;
- composite first-party scheduled U.S. macro-event calendar;
- optional targeted Dukascopy tick microstructure where explicitly justified;
- separate trade/account/risk state.

Explicit V1 exclusions:
- intraday US 10Y/rate channel;
- historical macro consensus/surprise;
- full global order flow;
- official ICE DXY prints as a complete TRAIN source;
- full six-year tick ingestion by default.

Next:
Do not train a model yet. Preregister Stage 2 Information Parity Layer V1 schema and timestamp-alignment contract before full 2016-2021 TRAIN acquisition/integration.

See research/INFORMATION_PARITY_V1_STAGE1_SOURCE_FEASIBILITY_FINDINGS.md.


---

## D-068 — Start Information Parity V1 Stage 2 with frozen schema/alignment contract

Branch:
research/information-parity-v1-stage2

Frozen preregistration:
research/INFORMATION_PARITY_V1_STAGE2_SCHEMA_PREREGISTRATION.md

Decision:
Begin Stage 2 design/build only after Stage 1 source verdicts were frozen in D-067.

Core timestamp contract:
- Dukascopy M1 timestamp is bar start;
- decision time = M1 bar start + 60 seconds;
- only information with availability time <= decision time may enter a decision row;
- no partial higher-timeframe candle may be used.

Frozen V1 information sources:
- synchronized XAUUSD M1 BID/ASK OHLC;
- spread;
- Dukascopy M1 provider volume;
- causal M3/M5/M15/M30/H1/H4/D1/W1 bars;
- deterministic causal swing/FVG/session/location state;
- SYNTHETIC_DXY_DUKASCOPY_BID;
- scheduled first-party U.S. macro-event calendar only;
- targeted tick microstructure only when explicitly justified;
- separate neutral trade/risk-state interface.

Explicit exclusions remain:
- intraday US 10Y/rate channel;
- macro actual/forecast/consensus/surprise;
- global order flow;
- full six-year tick ingestion by default.

Important design choices:
- reuse established EXP-002 BID/ASK synchronization;
- reuse conservative completed-bar semantics from existing project code;
- synthetic DXY is aligned by availability time with max 5-minute backward staleness;
- macro schedule may expose future scheduled event time, but never future event outcome;
- no pre-2016 warm-up acquisition;
- no outcome/P&L labels in Stage 2;
- accepted Stage 2 build must use one same-snapshot acquisition/build/integrity run with hashes.

Next implementation step:
build the Stage 2 acquisition/normalization pipeline and integrity checks on 2016-2021 TRAIN only, then run one accepted same-snapshot integrity build before Stage 3.

2022-2025 remain sealed.


---

## D-069 — Freeze Stage 2 public macro-calendar implementation and defer ISM historical dates

Decision:
Implement the Stage 2 scheduled macro calendar from reproducible first-party public sources for:
- CPI;
- Employment Situation / NFP;
- JOLTS;
- FOMC statements/rate decisions;
- Initial Jobless Claims;
- national GDP releases.

Exact implementation is frozen in:
research/INFORMATION_PARITY_V1_STAGE2_MACRO_ADDENDUM.md

Source families:
- BLS yearly historical schedules for CPI/NFP/JOLTS;
- Federal Reserve historical FOMC pages and statement pages;
- BEA national GDP archive/release pages;
- DOL/ETA weekly claims publication rule and holiday exception.

ISM implementation finding:
The public first-party site documents the normal first/third-business-day schedule, but also documents ISM-specific holiday exceptions, while historical PMI material is not reliably available publicly. Therefore V1 will not fabricate 2016-2021 ISM dates from a generic business-day calendar.

ISM Manufacturing/Services schedule state is deferred from Stage 2 V1 unless an exact reproducible first-party historical-date source is found before the first live macro acquisition.

Macro readiness for a year requires the six included core families to pass source-acquisition and count sanity checks. No actual/forecast/previous/revision/surprise values are ingested.

This decision was made from source reproducibility/causality constraints before Stage 2 model work and without XAUUSD outcome/P&L inspection.

2022-2025 XAUUSD remain sealed.


---

## D-070 — Use versioned normalized first-party schedule snapshots when agency sites block CI transport

Trigger:
The second bounded Stage 2 smoke run (37011477397) again failed only at macro-calendar completeness. BLS returned HTTP 403 from GitHub Actions for both official 2016 schedule URLs, while the same official BLS historical schedule is publicly readable outside the runner. FOMC and Claims succeeded. BEA returned pages but the archive query/parser did not surface national GDP releases.

Decision:
Do not keep changing user agents or repeatedly retrying the same blocked agency endpoint.

For schedule-only metadata, Stage 2 may use a small, versioned, normalized reference snapshot committed to the research repository when:
- every row is transcribed/normalized from an official first-party historical schedule page;
- the exact official source URL is stored on every row;
- local time and UTC conversion are deterministic with America/New_York;
- no release actual/forecast/previous/surprise value is included;
- the snapshot is reviewed against the official source before use;
- the snapshot is derived reference metadata, not a raw provider dump.

This transport fallback does not change the admitted information source: BLS remains the source for CPI/NFP/JOLTS schedule timestamps. It only removes runtime dependence on a BLS endpoint that blocks GitHub Actions.

Implementation order:
1. freeze and commit a verified BLS 2016 normalized schedule snapshot for the already-preregistered smoke year;
2. make the macro builder prefer live first-party fetch but fall back to the verified snapshot when BLS transport fails;
3. fix BEA GDP discovery by paging the official national-GDP archive with created_1=All and filtering releases by their first-party release timestamp;
4. rerun the same bounded 2016 smoke;
5. only after smoke acceptance, build/verify equivalent BLS snapshots for 2017-2021 before the full TRAIN run.

No third-party economic calendar is admitted by this decision.
No model/P&L data are used.
2022-2025 XAUUSD remain sealed.


---

## D-071 — Accept Stage 2 end-to-end smoke and advance to full-TRAIN preparation

Accepted smoke:
- run 37192128583 — SUCCESS
- head 273b93cc882ac954fcd6bc21b28155ef4ab5aa0f
- artifact information-parity-stage2-smoke
- artifact id 11299477067
- artifact digest sha256:cc46e7a2d7e3875533440e11c73846de5ed92e27b6182aff62a4a7f743d34d82

Result:
The fixed 2016-02-01 through 2016-02-06 market smoke completed acquisition, synchronization, synthetic DXY, macro normalization, Stage 2 layer build, and integrity validation end-to-end.

Key coverage:
- XAUUSD M1 decision rows: 6,840;
- synthetic DXY rows: 7,008;
- DXY availability on decision rows: 100%;
- feature-ready market share: 82.53%;
- normalized 2016 macro events: 108;
- macro schedule available: 100%.

Macro counts:
- Claims 52;
- CPI 12;
- FOMC 8;
- GDP 12;
- JOLTS 12;
- NFP 12.

Integrity validator: PASS.
2022-2025 XAUUSD accessed: none.

Expected smoke warnings:
D1 and W1 are empty because the smoke market window is one week and the frozen completion rules require more history. Their empty canonical files now preserve schema/header and validate correctly.

Decision:
Stage 2 smoke is accepted. Do not rerun it unless a later implementation change materially touches the end-to-end path.

Next:
- verify/commit 2017-2021 BLS normalized schedule snapshots under D-070;
- obtain green foundation CI for the new empty-table regression;
- implement the single 2016-2021 same-snapshot full TRAIN workflow;
- then run it once.

No model training is authorized yet.
See research/INFORMATION_PARITY_V1_STAGE2_SMOKE_FINDINGS.md.


---

## D-072 — Require offline deterministic Stage 2 preflight before any new CI/provider run

Decision:
The accepted Stage 2 smoke proved the end-to-end research pipeline can pass, but the sequence of preceding failures showed an engineering-process weakness: GitHub Actions was being used as the first integration-test environment.

That process is now stopped.

A dedicated isolated branch has been created:
research/information-parity-v1-stage2-preflight

It is intentionally not the head of PR #15 and is not included in automatic foundation-check push branches, so ordinary development commits there do not trigger CI.

Required offline gate:
- frozen runtime documented in research/INFORMATION_PARITY_V1_STAGE2_ENVIRONMENT.md;
- exact Python package lock in requirements/information-parity-stage2.lock.txt;
- offline runner: scripts/run_information_parity_stage2_preflight.sh;
- deterministic suite: tests/test_information_parity_stage2_preflight.py.

The suite exercises, without network/provider data:
- BID/ASK one-sided reconstruction and both-sides-missing behavior;
- M3/M5/M15/M30/H1/H4/D1/W1 aggregation;
- empty D1/W1 schema serialization;
- synthetic DXY exact-common-timestamp construction and <=5m backward staleness;
- US/UK DST session-boundary transitions;
- swing confirmation causality;
- FVG creation/invalidation causality;
- simultaneous macro-event multi-label state;
- neutral trade/risk state;
- positive integrity validation;
- a negative leakage test that must reject an injected future_return field.

Frozen accepted-smoke environment:
- CPython 3.12.14;
- Node v22.23.3;
- npm 10.9.9;
- dukascopy-node 1.50.0;
- exact Python package versions from accepted smoke run 37192128583.

CI policy:
CI is confirmation, not exploratory debugging.
Do not trigger a new Stage 2 CI/provider run simply because code changed.
First pass the offline deterministic preflight under the frozen environment. Then run one intentional pinned-environment CI confirmation only when the implementation is ready for integration.

If that intentional CI fails, add a deterministic regression before retrying whenever the failure is reproducible offline.

No new scientific source/model decision is made here.
No profitability work is authorized.
2022-2025 XAUUSD remain sealed.


---

## D-073 — First Stage 2 preflight failure was harness syntax; require compile-first rerun

Run 37196172995 failed before the deterministic suite executed.

Exact cause:
`scripts/check_information_parity_stage2_repo_contract.py` contained an unterminated string literal caused by newline escaping in the generated checker source.

The exact pinned environment itself initialized successfully:
- Node 22.23.3;
- npm 10.9.9;
- CPython 3.12.14;
- frozen Python dependency lock.

Decision:
Do not treat run 37196172995 as a Stage 2 information-layer failure.
Fix the checker, move the entire Python compile gate before checker/test execution, and perform off-CI syntax/shell validation before one more intentional deterministic-preflight confirmation.

Off-CI checks completed before rerun authorization:
- corrected repository-contract checker compiles;
- deterministic preflight test compiles;
- preflight shell runner passes bash syntax validation.

The next CI, if triggered, is justified only to execute the full deterministic suite under the exact pinned runtime. It must not acquire provider market data.

See research/INFORMATION_PARITY_V1_STAGE2_PREFLIGHT_RUN1_FINDINGS.md.


---

## D-074 — Preflight exposed real D1 grouping bug; partially invalidate prior smoke and block provider runs

Run 37227754869 passed repository-contract, frozen-environment and foundation checks, then failed inside the deterministic end-to-end suite on daily-bar coverage.

Root cause:
`build_d1` changed the working frame to a DatetimeIndex and then assigned a RangeIndex-backed timestamp Series to `source_day`. Pandas label alignment therefore produced NaT source-day values and prevented D1 grouping.

Consequences:
- D1 construction was broken;
- W1 was empty downstream;
- previous-day state could not be populated;
- the earlier smoke run 37192128583 did not validate D1/W1/previous-day state.

Correction:
The Stage 2 smoke findings are amended. Run 37192128583 remains accepted evidence for M1-H4, DXY, macro, synchronization, structural/session, decision-index and neutral trade-state paths, but not for D1/W1 or previous-day state.

Fix:
Derive source_day directly from the DatetimeIndex, avoiding Series label alignment.

New regressions:
- 48 H1 bars => exactly 2 D1 bars with source_count 24/24;
- four-week deterministic fixture => exactly 28 D1 and 4 W1 bars.

Independent off-CI reproduction after the fix produced:
- H1 671;
- D1 28;
- W1 4;
with one 23-H1 day caused by the deliberately missing both-sides M1 minute.

Decision:
Do not trigger another CI or provider-data run yet.
Restore the preflight workflow to manual-only, remove the temporary trigger, review the remaining deterministic suite for similar index-alignment assumptions, and only then authorize one intentional preflight confirmation.

A corrected real-data smoke will be required after deterministic preflight acceptance because the fix materially changes the D1/W1 end-to-end path.

No model training is authorized.
2022-2025 XAUUSD remain sealed.

See research/INFORMATION_PARITY_V1_STAGE2_PREFLIGHT_RUN2_FINDINGS.md.


---

## D-075 — Local deterministic Stage 2 logic gate passes; exact-runtime CI still deferred

A real local execution was performed after the D-074 D1 fix.

This was not static review and not GitHub Actions.

Local result:
- Python compile PASS;
- deterministic preflight PASS;
- exit code 0;
- 40,319 synchronized M1 rows;
- one BID reconstruction and one ASK reconstruction;
- D1 = 28;
- W1 = 4;
- one deliberate >5m DXY coverage hole produced one unavailable decision row;
- max DXY age on available rows = 5m;
- macro state available on all deterministic rows;
- integrity validator PASS;
- injected future_return field correctly rejected;
- sealed periods accessed: none.

Execution-log SHA-256:
a80a1e9b6e001d1a5b62a7fe9e9e3b8fe57330f1fbc0f92756e94f8543516014

Important limitation:
the local container is Python 3.13.5 / pandas 2.2.3 / Node 22.16.0, not the frozen exact CI environment. Some larger source files had to be semantically materialized from connector content rather than byte-identical repository checkout because the local container cannot network-clone GitHub.

Decision:
Treat this as a successful local logic gate only. Do not trigger provider-data CI. Do not yet claim exact-branch/exact-runtime preflight acceptance.

Next:
reconcile exact source identity / finish static pandas-alignment review, then authorize one manual exact-runtime deterministic-preflight CI only if still warranted. Poll that intentional CI for up to four minutes.

See research/INFORMATION_PARITY_V1_STAGE2_LOCAL_PREFLIGHT_EVIDENCE.md.


---

## D-076 — Off-CI static review passes after four integrity corrections; authorize one exact-runtime preflight CI

After D-074/D-075, the exact branch source was reviewed off-CI for pandas alignment, higher-timeframe hierarchy, as-of semantics, macro grouping and raw timestamp integrity.

Four implementation gaps were found and corrected before another CI:
1. simultaneous macro events were counted as one timestamp instead of multiple admitted events;
2. required swing/session/previous-day distances were missing from the physical structural table;
3. the validator did not independently recompute D1/W1 hierarchy or previous-day as-of state;
4. raw XAUUSD/DXY loaders could silently overwrite duplicate timestamps and accepted off-grid M1 timestamps.

The corrected local deterministic suite then passed under the available local runtime.

Local review log SHA-256:
296261657094045e01afc4941fee413e2a8477fe0f95f1496a6cdb00b335fd0a

Decision:
One exact-runtime deterministic-preflight CI is now justified to confirm exact repository bytes under the frozen environment. This is a confirmation gate, not exploratory debugging.

No provider-data smoke/full run is authorized by this decision.
If the exact-runtime preflight passes, the next provider-data action is a corrected bounded smoke because D-074 materially changed D1/W1/previous-day behavior.

See:
- research/INFORMATION_PARITY_V1_STAGE2_PREFLIGHT_STATIC_REVIEW_ADDENDUM.md
- research/INFORMATION_PARITY_V1_STAGE2_LOCAL_REVIEW_V2.md


---

## D-077 — Exact-runtime deterministic Stage 2 preflight accepted

Accepted run:
- workflow: information-parity-stage2-preflight
- run: 37231660721
- head: 1a008ac8ff70335ee7ef8793a81d55c6909db8bb
- conclusion: SUCCESS

The run completed under the frozen environment:
- CPython 3.12.14;
- numpy 2.5.3;
- pandas 3.0.6;
- requests 2.34.2;
- beautifulsoup4 4.15.0;
- Node 22.23.3 / npm 10.9.9 as enforced by the preflight shell gate.

Passing gates:
- repository contract PASS;
- environment lock PASS;
- foundation tests PASS;
- deterministic offline preflight PASS;
- overall preflight PASS.

The exact-runtime confirmation includes the D-074/D-076 corrections:
- D1/W1 hierarchy;
- simultaneous macro-event multiplicity;
- structural/session/previous-day distances;
- duplicate/off-grid raw M1 guards;
- negative leakage rejection.

Decision:
The deterministic Stage 2 implementation is accepted for an updated bounded real-data smoke.

Because D-074 materially changed D1/W1/previous-day behavior after the earlier smoke, the previous smoke is not sufficient for those paths. One corrected 2016 bounded smoke is now authorized before any full 2016-2021 TRAIN build.

The deterministic preflight workflow has been restored to manual-only and its temporary trigger removed.

No full TRAIN run or model training is authorized yet.
2022-2025 XAUUSD remain sealed.


---

## D-078 — Corrected bounded real-data Stage 2 smoke accepted; authorize full TRAIN implementation work

Accepted run:
- workflow: information-parity-stage2
- run: 37231837219
- head: e2aaaaa829a76be6cd10e35f9dac85e3b7c6b343
- conclusion: SUCCESS
- artifact digest: sha256:05d7955f11834eb668d191b2cbf5dcf64ff0b4bbedec646c2e42fd2079cfe59e

Key corrected evidence:
- M1 6,840;
- H1 114;
- D1 5;
- W1 1;
- D1<-H1 hierarchy PASS;
- W1<-D1 hierarchy PASS;
- previous-day as-of PASS;
- structural distances PASS;
- DXY backward as-of PASS;
- macro state/timezone integrity PASS;
- sealed-period guard PASS;
- warnings: none.

This resolves the D-074 defect on real provider data.

Decision:
The Stage 2 implementation is accepted for full 2016-2021 TRAIN information-layer build preparation.

Do not jump directly to an expensive full CI run until the full-train orchestration itself has been implemented and reviewed off-CI. Once that orchestration passes static/local checks, one full TRAIN CI execution is scientifically justified.

No model training is authorized yet.
2022-2025 XAUUSD remain sealed.

See research/INFORMATION_PARITY_V1_STAGE2_CORRECTED_SMOKE_FINDINGS.md.


---

## D-079 — Full Stage 2 TRAIN must preserve causal state across calendar-year boundaries

During off-CI implementation review after D-078, the existing annual builder/orchestration pattern was found unsuitable for the accepted full TRAIN run if invoked independently for each year.

Independent yearly builds would incorrectly cold-start at every January 1 and lose causally available prior-TRAIN state, including rolling volume/spread context, swing/FVG state, D1/W1/previous-day context and DXY rolling history.

The frozen Stage 2 warm-up policy authorizes a cold start only at the beginning of 2016; it does not justify annual resets.

Decision:
- treat 2016-2021 as one continuous causal history;
- compute state continuously;
- use annual files only as post-computation physical partitions;
- build synthetic DXY continuously across all six years;
- add explicit year-boundary continuity checks.

This is an implementation-correctness clarification made before the full TRAIN build. It uses no future XAUUSD outcome or P&L information.

See research/INFORMATION_PARITY_V1_STAGE2_FULL_TRAIN_CONTINUITY_ADDENDUM.md.

No full CI run is authorized until the continuous full-TRAIN orchestration passes off-CI review.
2022-2025 XAUUSD remain sealed.


---

## D-080 — 2016-2021 BLS fallback snapshots complete and static full-input gate passes

The repository now contains normalized official-BLS schedule snapshots for every permitted TRAIN year 2016-2021.

Each annual snapshot contains exactly:
- CPI: 12 rows;
- Employment Situation / NFP: 12 rows;
- JOLTS: 12 rows.

Off-CI static verification against the exact GitHub branch files passed for all six years:
- exact frozen CSV schema;
- BLS agency/source provenance;
- America/New_York timezone declaration;
- local/UTC instant equivalence;
- unique event IDs;
- unique family/timestamp identities;
- deterministic SHA-256 event-ID reconstruction;
- minimum family-count requirement.

2017-2021 provenance and normalized SHA-256 identities are documented in:
research/INFORMATION_PARITY_V1_BLS_2017_2021_SNAPSHOT_PROVENANCE.md

Decision:
The BLS transport-fallback prerequisite no longer blocks full TRAIN preparation.

This does not authorize the full provider-data CI by itself. The continuous full-TRAIN orchestration still must pass its deterministic integration/static gate first.

No economic outcomes were used. 2022-2025 XAUUSD remain sealed.


---

## D-081 — Continuous Stage 2 full-TRAIN deterministic integration gate passes off-CI

After D-079/D-080, the continuous 2016-2021 Stage 2 orchestration was reconstructed from the exact branch files and executed off-CI using deterministic synthetic fixtures only.

Command-equivalent integration target:
`tests/test_information_parity_stage2_full_train_preflight.py`

Observed terminal result:
`INFORMATION_PARITY_STAGE2_FULL_TRAIN_PREFLIGHT_PASS`

The passing integration exercised:
- six annual TRAIN partitions feeding one continuous causal history;
- continuous synthetic DXY construction;
- M1 rolling state without artificial calendar-year resets;
- M3/M5/M15/M30/H1/H4 aggregation;
- D1-from-H1 and W1-from-D1 hierarchy validation;
- structural swing/FVG causality and distance checks;
- previous-day backward as-of state;
- macro schedule/state alignment;
- neutral trade/risk-state template;
- 2017-2021 year-boundary continuity checks;
- normalized manifest construction;
- final compact full-TRAIN summary gate;
- sealed-period assertions.

No provider market acquisition occurred in this off-CI run. No 2022-2025 XAUUSD data were accessed. No economic/P&L labels were used.

Runtime caveat:
The available local execution runtime was not the frozen CI runtime. Therefore this result accepts the orchestration logic/integration gate only; it does NOT substitute for exact-runtime confirmation under Python 3.12.14 / Node 22.23.3 and the frozen Stage 2 lock.

Decision:
The next step is one exact-runtime deterministic preflight CI confirmation. Do not launch the expensive full provider-data `full-train` job until that exact-runtime deterministic gate passes.


---

## D-082 — Exact-runtime continuous Stage 2 deterministic preflight accepted

GitHub Actions run:
- workflow: `information-parity-stage2-preflight`
- run ID: `37434443674`
- event: temporary branch/path-restricted push trigger
- head: `052e76d97edcdce07205be20c012cb557ea6d964`
- status: completed
- conclusion: success
- started: 2026-10-06T08:11:19Z
- completed: approximately 2026-10-06T08:12:22Z

Exact configured runtimes observed in the job log:
- Node: `v22.23.3`
- CPython: `3.12.14`
- frozen Stage 2 Python lock installed successfully.

Deterministic terminal gates all passed:
- `INFORMATION_PARITY_STAGE2_REPO_CONTRACT_PASS`
- `INFORMATION_PARITY_STAGE2_ENVIRONMENT_PASS`
- `INFORMATION_PARITY_STAGE2_FOUNDATION_PASS`
- `INFORMATION_PARITY_STAGE2_OFFLINE_PREFLIGHT_PASS`
- `INFORMATION_PARITY_STAGE2_FULL_TRAIN_PREFLIGHT_PASS`
- `INFORMATION_PARITY_STAGE2_PREFLIGHT_ALL_PASS`

GitHub emitted a platform warning that some pinned actions internally target deprecated Node 20 and are being forced by the hosted runner to Node 24. This did not alter the configured project Node 22.23.3 runtime used by the deterministic suite and did not fail any gate. Pinned action revisions remain unchanged.

The temporary push trigger was removed immediately after acceptance and the preflight workflow was restored to manual dispatch only.

Decision:
The deterministic/offline prerequisite for the Stage 2 full TRAIN build is accepted. The next authorized research action is the one-shot same-snapshot 2016-2021 provider-data `full-train` build. 2022-2025 remain sealed.


---

## D-083 — Full-TRAIN run 1 failed at macro normalization; freeze narrow recovery gate

Run 37434856203 is **not** an accepted Stage 2 full-TRAIN build.

What passed before the failure:
- frozen runtime and repository prerequisites;
- same-job 2016-2021 market acquisition;
- all annual XAUUSD synchronizations;
- continuous 2016-2021 synthetic DXY construction.

Failure:
- macro normalization was incomplete:
  - 2018 GDP = 9 (<11);
  - 2020 GDP = 10 (<11);
  - 2021 GDP = 10 (<11);
  - 2021 FOMC = 0 (<8).
- the legacy Federal Reserve 2021 historical-year URL returns 404;
- the BEA parser excludes legitimate national-GDP colon/parenthetical title variants and one punctuation form in embargo timestamps.

Artifact:
- id 11400771061
- digest sha256:4f8cff0e95191d7992be27ee4e2bc058fdc003e69e33da6f412c2df108d753a4

Decision:
1. keep the admitted macro source families unchanged;
2. correct only first-party Federal Reserve indexing and BEA syntax parsing as frozen in `research/INFORMATION_PARITY_V1_STAGE2_MACRO_RECOVERY_ADDENDUM.md`;
3. add deterministic regressions before CI;
4. require exact-runtime deterministic confirmation after the code change;
5. require one macro-only 2016-2021 network confirmation before another expensive full TRAIN run;
6. reorder the final full-TRAIN job so macro readiness is checked before market acquisition.

The market/DXY outputs from run 37434856203 are diagnostic partial evidence only and cannot be reused as the final same-snapshot artifact because the accepted Stage 2 build must finish all gates in one run.

No source substitution, economic-outcome inspection or model tuning is authorized.
2022-2025 XAUUSD remain sealed.


---

## D-084 — Macro recovery changed-surface off-CI gate passed; exact-runtime preflight authorized

Evidence:
`research/INFORMATION_PARITY_V1_STAGE2_MACRO_RECOVERY_LOCAL_REVIEW.md`

After D-083:
- the Federal Reserve 2021 index fallback and BEA title/time parser corrections were implemented;
- deterministic regressions were added for the exact observed failure modes;
- the full-TRAIN workflow was reordered so macro readiness precedes expensive market acquisition;
- a manual macro-only network-confirmation mode was added;
- repository-contract checks now enforce those properties.

Off-CI changed-surface regression result:
`TARGETED_MACRO_RECOVERY_OFF_CI_PASS 8 []`

The available local runtime differs from the frozen Stage 2 runtime, so this is a logic/static gate only.

Decision:
one complete exact-runtime deterministic preflight is now justified on the current branch. It is not a provider-data experiment and must be the only CI run triggered at this gate.

If it passes, the next authorized run is one 2016-2021 **macro-only** network confirmation. Full TRAIN remains blocked until that macro-only confirmation passes.

2022-2025 XAUUSD remain sealed. No model training.


---

## D-085 — Exact-runtime Stage 2 macro-recovery deterministic preflight accepted

Accepted run:
- workflow: `information-parity-stage2-preflight`
- run: **37472945799**
- head: `7e74193cba68591883621c70c4645b4ad85a425d`
- conclusion: **SUCCESS**

Frozen runtime confirmed:
- Node 22.23.3 / npm 10.9.9;
- CPython 3.12.14;
- exact Stage 2 Python lock, including pandas 3.0.6.

All terminal gates passed:
- repository contract;
- frozen environment;
- foundation suite;
- deterministic Stage 2 preflight;
- continuous full-TRAIN deterministic preflight;
- overall preflight.

This exact-runtime suite includes the D-083/D-084 Federal Reserve 2021 fallback and BEA parser regressions, plus the workflow contract that prevents the macro-only gate from acquiring XAUUSD/FX market data and requires the full-TRAIN macro gate to precede expensive market acquisition.

The temporary isolated trigger was removed and the deterministic preflight workflow is manual-only again.

Decision:
the next authorized run is exactly one 2016-2021 **macro-only network confirmation**. Full TRAIN remains blocked until that macro-only run passes every admitted family/year coverage gate.

2022-2025 XAUUSD remain sealed. No model training.


---

## D-086 — 2016-2021 macro-only network confirmation accepted; second full-TRAIN build authorized

Accepted run:
- workflow: `information-parity-stage2`
- run: **37473462028**
- head: `db6dd32394c342e2c9650553cc20b24294fed544`
- artifact ID: **11418296108**
- digest: `sha256:67f134b67cbc1f476829a0c0d4f6bab58efa61773bda09dd2252c88a739c8a5d`

The isolated macro-only job passed and the smoke/full-TRAIN jobs were skipped.

Coverage status is PASS with 652 normalized schedule rows. Every admitted family passes every TRAIN year with no recorded errors. The previously failing cells are now:
- 2018 GDP = 12;
- 2020 GDP = 12;
- 2021 GDP = 12;
- 2021 FOMC = 8.

Both the macro coverage and repository-input verification record no sealed XAUUSD-period access.

Decision:
the preregistered D-083 recovery gates are complete. Exactly one second full 2016-2021 same-snapshot provider build is now authorized on the accepted implementation. Macro readiness must execute before market acquisition, and full-TRAIN causal state must remain continuous across year boundaries.

No 2022-2025 XAUUSD access, model training, profitability tuning or broker mutation is authorized.


---

## D-087 — Accept continuous 2016-2021 Information Parity V1 Stage 2 full-TRAIN build

Accepted run:
- workflow: `information-parity-stage2`
- run: **37474263432**
- head: `51664a31ab7739e2a4bdba9df70eadf02249133a`
- conclusion: **SUCCESS**
- artifact ID: **11421634040**
- artifact digest: `sha256:41ebcaacaaaddafc6433e787ee9232eccf5128205b8648cecfd20f595d52985a`

Final evidence:
- full summary: PASS;
- continuous 2016-2021 causal state: true;
- integrity checks: 27/27 PASS;
- integrity warnings: none;
- macro coverage: PASS for every admitted family/year;
- sealed XAUUSD periods accessed: none.

Core accepted counts:
- XAUUSD M1 / decision rows: 2,124,206;
- synthetic DXY M1: 2,138,819;
- macro schedule: 652;
- D1: 1,459;
- W1: 292.

Accepted evidence identities include:
- raw market manifest SHA-256 `128496c869cc99aff7790a1b2f8ad3fd03505fbfa41202edd6a4d07bd6717919`;
- synchronized XAUUSD manifest SHA-256 `4041c62ddcd1717f466dd5cdc9ce0426053603c8ef0c692794ab249f7740ea11`;
- normalized full-TRAIN manifest SHA-256 `e9440bb0971c52456d1a79ddaa0144aa36fd758666421392bc4e7203132ea4c9`;
- final summary SHA-256 `34e577e7755b2e3ebd9d619329c84ea26a9eca3d134677fc736236ed5c622d1f`;
- integrity report SHA-256 `79867cb548feeec8b537cfbbc80678057c664867e86c8ddb9fdba771376c5bf4`.

The compact evidence hash list contains a non-authoritative self-hash line for its own file because it was hashed while being written. This is a bookkeeping quirk only; do not rerun provider acquisition for it. The GitHub artifact digest is the uploaded-artifact identity, and all non-self scientific evidence hashes remain usable.

Decision:
**Information Parity V1 Stage 2 is complete and accepted.**

This does not establish profitability, does not authorize model tuning against sealed years, and does not open 2022-2025 XAUUSD.

Next:
freeze the accepted Stage 2 identity in Stage 3 prerequisites and preregister the Badar decision-recognition dataset/evaluation protocol before any Stage 3 empirical fitting.

See:
`research/INFORMATION_PARITY_V1_STAGE2_FULL_TRAIN_ACCEPTED_FINDINGS.md`.


---

## D-088 — Stage 3 Badar teacher benchmark is blocked by the 2026 time-domain mismatch

After D-087, the admitted Badar source layer was audited before any Stage 3 market acquisition or fitting.

Pinned Badar source:
- repository: `alisufyan-ai7/unpack-human-trading-strategies-claude`
- commit: `2df3d588c4b6d82761df2ee0c6f6639e82ce3414`
- source table: `dataset/live_trades.csv`
- blob: `ea620cb44937f276be2e65ae7da25ae9503be655`

Source-layer audit:
- 119 trade rows;
- 43 streams;
- date range 2026-07-06 through 2026-10-02;
- every row is dated 2026;
- 118 XAUUSD-like rows;
- 1 non-XAUUSD row;
- 52 long / 67 short;
- 110 chart-time strings are approximate;
- source `confidence` is evidence/readability confidence, not Badar trade confidence;
- `setup_id` is a researcher-added organizational index, not a Badar-authored class label.

Conflict:
- accepted Information Parity V1 Stage 2 market state is 2016-2021 TRAIN;
- 2026 is currently reserved for later forward/shadow comparison;
- there are zero admitted Badar live-trade teacher rows in 2016-2021.

Decision:
Do **not** acquire or use 2026 XAUUSD for Stage 3 fitting under the present governance.

Stage 3 empirical fitting is blocked until a separately frozen chronology decision either:
1. preserves the 2026 reserve and provides a different timestamp-resolvable expert teacher source overlapping TRAIN; or
2. explicitly repurposes a bounded 2026 teacher window and defines what 2026 data remains reserved.

No shortcut may convert Claude-derived rules/labels into Badar supervision.

See:
`research/INFORMATION_PARITY_V1_STAGE3_TEACHER_TIME_DOMAIN_FEASIBILITY.md`.

2022-2025 XAUUSD remain sealed. 2026 also remains untouched for Stage 3 until the chronology gate is changed explicitly.


---

## D-089 — Freeze Stage 3 decision-recognition protocol while empirical execution remains blocked

Preregistration:
`research/INFORMATION_PARITY_V1_STAGE3_PROTOCOL_PREREGISTRATION.md`

Development branch:
`research/information-parity-v1-stage3-preregistration`

This decision freezes the non-market Stage 3 protocol before any 2026 XAUUSD access or model fitting.

Teacher provenance remains pinned to:
- Badar source repo commit `2df3d588c4b6d82761df2ee0c6f6639e82ce3414`;
- source-layer `dataset/live_trades.csv` blob `ea620cb44937f276be2e65ae7da25ae9503be655`;
- no `derived/` content may be attributed to Badar or used as teacher supervision.

Frozen primary teacher requirements:
- XAUUSD only;
- Badar authorship confirmed from source-layer evidence;
- live/real personal execution confirmed;
- unambiguous LONG/SHORT;
- one exact M1 entry minute;
- no outcome-dependent inclusion.

Paper/simulation, student/viewer, planning/signal-only, unclear-fill and unresolved-time rows are excluded from the primary teacher benchmark.

Frozen control/evaluation design:
- controls come only from source-observed stream minutes;
- uncertain trade intervals are quarantined from negatives;
- all same-date streams remain in one group;
- leave-one-source-date-out evaluation;
- no random row split;
- no random negative subsampling in the primary benchmark.

Frozen comparison:
- GOLD_PRICE_ONLY versus FULL_INFORMATION_PARITY_V1;
- identical candidate rows/folds/preprocessing/model architecture;
- fixed L2 logistic-regression recognition benchmark;
- no hyperparameter search.

Primary advancement rule:
- minimum 40 eligible positive minutes, 20 dates, 15 LONG and 15 SHORT;
- FULL must improve mean per-date entry-recognition ROC-AUC over GOLD by at least +0.03;
- paired date-bootstrap 95% CI lower bound for the delta must be >0;
- FULL Brier score may not be worse than GOLD by more than 0.01.

Direction recognition is mandatory secondary evidence but cannot rescue a failed opportunity-recognition gate.

Critically, D-088 remains in force:
**this protocol does not authorize 2026 XAUUSD acquisition or empirical Stage 3 fitting.**

Immediate next safe task:
construct the source-only teacher adjudication and stream observation-window metadata from the pinned Badar source layer, then determine whether the minimum teacher-evidence gate can be met without looking at market prices.

2022-2025 remain sealed. 2026 remains reserved until a separate chronology decision explicitly changes that status.


---

## D-090 — Freeze Stage 3 source timestamp audit V1; targeted frame adjudication is the next safe gate

Findings:
`research/INFORMATION_PARITY_V1_STAGE3_SOURCE_TIMESTAMP_AUDIT_FINDINGS.md`

Durable source-only artifacts:
- `research/reference/information-parity-v1/stage3-teacher-timestamp-audit-v1.csv`
  - blob `fdfe6f2be6fd7633daaf0be69d5b738cdda0e315`;
- `research/reference/information-parity-v1/stage3-stream-observation-windows-v1.csv`
  - blob `6c1ee6b6450e688bc267c309e410b95472c53e07`.

Using only the pinned Badar source commit and source metadata, the conservative V1 resolver currently proves:
- 35 exact-M1 candidate rows;
- 16 dates;
- 14 LONG;
- 21 SHORT.

This is below D-089's minimum 40 / 20 dates / 15 LONG / 15 SHORT gate **before** authorship or live-execution exclusions.

Decision:
this is an intermediate metadata result, not a final teacher-evidence failure.

Source frames/notes may promote approximate rows only when they independently resolve one unique M1 entry minute. No timestamp rule may be relaxed to manufacture the minimum count.

The 43 stream header windows are now pinned for audit but are not yet authorized as negative-control windows; minute-level XAUUSD visibility still requires source-only review.

Immediate next safe work:
perform a targeted source-frame/note timestamp review of unresolved rows, prioritizing missing dates and LONG rows. Do not query market prices.

D-088 remains controlling:
no 2026 XAUUSD acquisition or empirical Stage 3 fitting is authorized.

No CI is required for this source-evidence review.


---

## D-091 — Separate Stage 3 evidence adequacy, recognition hypothesis, and profitability claims

Clarification:
`research/INFORMATION_PARITY_V1_STAGE3_EVIDENCE_ADEQUACY_CLARIFICATION.md`

The Stage 3 protocol has been amended before any empirical execution.

The 40 positive / 20 date / 15 LONG / 15 SHORT floors are now formally an **evidence-adequacy gate**, not a profitability gate and not the recognition-hypothesis PASS/FAIL test.

Allowed evidence-adequacy outcomes:
- `ADEQUATE`: all four floors are met;
- `INSUFFICIENT`: one or more floors are missed.

If evidence is `INSUFFICIENT`:
- the frozen recognition hypothesis is `NOT TESTED / INCONCLUSIVE`;
- do not relax source-quality/timestamp standards merely to cross the floors;
- do not infer that Information Parity lacks economic value;
- do not infer that a profitable XAUUSD system is impossible.

Only after evidence is `ADEQUATE` and the separate chronology gate authorizes execution may the frozen FULL-vs-GOLD recognition hypothesis be tested.

If that recognition hypothesis produces a negative result, the conclusion is limited to the frozen teacher dataset, representation, candidate construction and diagnostic model. It still does not prove unprofitability.

Profitability requires a later separately frozen economic evaluation with BUY/SELL/NO-TRADE semantics, execution costs, economic outcomes, chronological validation and sealed OOS testing.

The existing 35 exact-M1 / 16-date / 14-LONG / 21-SHORT metadata result is therefore an intermediate evidence audit only.

D-088 remains unchanged:
no 2026 XAUUSD acquisition, market reconstruction or Stage 3 empirical fitting is authorized.


---

## D-092 — Stage 3 timestamp sub-audit reaches numeric floors; primary evidence adequacy remains unresolved

Findings:
`research/INFORMATION_PARITY_V1_STAGE3_SOURCE_TIMESTAMP_AUDIT_V2_FINDINGS.md`

V2 timestamp artifact:
`research/reference/information-parity-v1/stage3-teacher-timestamp-audit-v2.csv`

Blob:
`de7f9647a18aa018ca00dc727c141f02d74fd2f4`

Targeted pinned-source transcript/frame review promoted five rows to exact M1:
- `HOidQitTyAc#3` -> 18:01 UTC+4;
- `qTSedn6hEp8#2` -> 17:41 UTC+4;
- `NPUPkMWzKTE#1` -> 18:11 UTC+4;
- `m0l1wj9IZ2o#3` -> 17:33 UTC+4;
- `PYPzCJV-YXE#1` -> 18:15 UTC+5.

Timestamp-only totals are now:
- 40 exact-M1 candidates;
- 21 source dates;
- 16 LONG;
- 24 SHORT.

These clear the numerical D-091 floors **before** authorship/live-execution filtering.

Decision:
do not label Stage 3 evidence `ADEQUATE` yet.

D-091 adequacy applies to primary eligible positives after Badar authorship adjudication, live/real execution adjudication, frozen exclusions and same-minute same-direction collapse.

Current status:
`UNRESOLVED — PRIMARY ELIGIBILITY NOT YET ADJUDICATED`.

Several reviewed rows were deliberately not promoted where the exact entry minute remained ambiguous, including `9d7IHhIAi6M#1`, `6trb-6A2t6Q#1/#2` and `fkZjFHTg3GY#1`. The timestamp standard was not relaxed to cross the numeric floor.

Immediate next safe task:
perform source-only authorship/execution adjudication on the 40 exact-M1 V2 candidates and compute the first true D-091 `ADEQUATE` / `INSUFFICIENT` result.

D-088 remains controlling. No 2026 XAUUSD market reconstruction or model fitting is authorized.


---

## D-093 — Freeze Stage 3 primary-teacher adjudication Batch 01; TradingView-only evidence does not establish live/real execution

Findings:
`research/INFORMATION_PARITY_V1_STAGE3_PRIMARY_ADJUDICATION_BATCH01_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3-teacher-primary-adjudication-batch01.csv`

Scope:
first 10 chronological exact-M1 V2 candidates.

Result:
- 10 / 10 `BADAR_CONFIRMED` authorship;
- 8 `FILL_UNCLEAR`;
- 1 `PAPER_OR_SIMULATION`;
- 1 `PLAN_OR_SIGNAL_ONLY`;
- 0 `LIVE_OR_REAL_CONFIRMED`;
- 0 primary-eligible rows in this batch.

Decision:
apply Section 5 conservatively. A TradingView position/long-short tool or first-person trade call does not by itself establish the required live/real execution. Live/real status requires source-layer evidence of actual personal broker/live-account execution.

The July 28 stream explicitly states live-account trading starts the next day, supporting paper/simulation exclusion for `suuicaoUvDQ#1`. Its later limit `suuicaoUvDQ#3` does not confirm Badar's own fill and is plan/signal-only.

No outcome, RR, TP/SL result, later market path or profitability was used in eligibility decisions.

This partial batch does not determine D-091 evidence adequacy.

Immediate next safe work:
continue source-only execution/authorship adjudication with the next chronological exact-M1 batch starting at `HOidQitTyAc#3`.

D-088 remains controlling; no 2026 market reconstruction, model fitting or CI is authorized.


---

## D-094 — Stage 3 primary adjudication Batch 02 finds the first two live/real primary teacher rows

Findings:
`research/INFORMATION_PARITY_V1_STAGE3_PRIMARY_ADJUDICATION_BATCH02_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3-teacher-primary-adjudication-batch02.csv`

Scope:
next 10 chronological exact-M1 V2 candidates after Batch 01.

Result:
- 10 / 10 `BADAR_CONFIRMED`;
- 2 `LIVE_OR_REAL_CONFIRMED`;
- 8 `FILL_UNCLEAR`;
- 2 primary-eligible rows.

Confirmed primary rows:
1. `NIDMLJuBPwk#1` — LONG — 2026-08-07T12:34Z
   - Exness terminal / second account / mobile close source evidence.
2. `B83jlxwuo10#1` — LONG — 2026-09-04T12:30Z
   - explicitly shown on an Exness real account with placed buy limit, visible account/risk values and news slippage.

Decision:
execution provenance is evaluated per trade. General evidence that Badar owns or has shown live accounts does not upgrade an otherwise TradingView-only row to live/real.

Cumulative after two batches:
- 20 exact-M1 candidates adjudicated;
- 2 primary eligible;
- 2 LONG;
- 0 SHORT.

Do not yet declare D-091 evidence `INSUFFICIENT`: 20 V2 exact-M1 candidates remain unadjudicated and interval-only rows have not been exhaustively source-frame-reviewed for additional exact-M1 promotions.

Immediate next safe work:
continue source-only primary adjudication with the next chronological batch.

No 2026 market-price lookup, model fitting or CI is authorized.


---

## D-095 — Stage 3 primary adjudication Batch 03 adds two live/real rows and excludes one Zain-owned trade

Findings:
`research/INFORMATION_PARITY_V1_STAGE3_PRIMARY_ADJUDICATION_BATCH03_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3-teacher-primary-adjudication-batch03.csv`

Scope:
third chronological batch of 10 exact-M1 V2 candidates.

Result:
- 9 `BADAR_CONFIRMED`;
- 1 `OTHER_PERSON`;
- 2 `LIVE_OR_REAL_CONFIRMED`;
- 8 `FILL_UNCLEAR`;
- 2 primary eligible.

New primary rows:
1. `B83jlxwuo10#5` — SHORT — 2026-09-04T12:57Z
   - same Exness-real stream plus contemporaneous personal dashboard/profit evidence during the trade.
2. `qTSedn6hEp8#2` — LONG — 2026-09-21T13:41Z
   - Exness real-account position shown at 0.10 lot with dollar SL/P&L.

Explicit non-Badar row:
- `OpMzvMNNrHM#2` — `OTHER_PERSON`; source says Zain's OANDA chart and `Zain brother has done the trade`.

Cumulative after Batches 01-03:
- 30 / 40 current exact-M1 candidates adjudicated;
- 4 primary eligible;
- 3 LONG;
- 1 SHORT.

Do not yet declare D-091 `INSUFFICIENT`. The final 10 current V2 exact-M1 rows remain unadjudicated, and interval-only rows have not yet been exhaustively source-reviewed for additional timestamp promotion.

Immediate next safe work:
adjudicate the final 10 current V2 exact-M1 candidates, then assess whether additional interval-only review is necessary before final evidence adequacy.

No 2026 market-price lookup, model fitting or CI is authorized.


---

## D-096 — Complete primary adjudication of the current 40-row exact-M1 pool; overall adequacy now depends on interval-row feasibility

Findings:
`research/INFORMATION_PARITY_V1_STAGE3_PRIMARY_ADJUDICATION_BATCH04_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3-teacher-primary-adjudication-batch04.csv`

Batch 04:
- 10 / 10 `BADAR_CONFIRMED`;
- 10 `FILL_UNCLEAR`;
- 0 new primary-eligible rows.

The complete current V2 exact-M1 pool is now adjudicated:

- 40 / 40 rows reviewed;
- 4 primary eligible;
- 3 LONG;
- 1 SHORT;
- 3 distinct primary dates.

The exact-M1 V2 pool alone is `INSUFFICIENT` against D-091's evidence-adequacy floors.

However, overall D-091 status remains pending because 79 source-table rows are still outside the exact-M1 set.

To reach `ADEQUATE`, the remaining source evidence would have to contribute at minimum:
- 36 additional primary positives;
- 17 additional eligible dates;
- 12 additional LONG;
- 14 additional SHORT.

Decision:
do not blindly adjudicate all 79 interval rows.

Immediate next safe work is a source-only **feasibility-bound scan**. A remaining row can matter only if source evidence plausibly supports both:
1. a live/real Badar-owned execution;
2. resolution to one unique M1 entry minute.

If the resulting maximum possible pool cannot meet any one of the frozen floors, finalize D-091 as `INSUFFICIENT / NOT TESTED`.

D-088 remains controlling. No 2026 market-price lookup, model fitting or CI is authorized.


---

## D-097 — Finalize Stage 3 teacher evidence as INSUFFICIENT; frozen recognition hypothesis is NOT TESTED

Findings:
`research/INFORMATION_PARITY_V1_STAGE3_INTERVAL_FEASIBILITY_BOUND_FINDINGS.md`

Feasibility artifact:
`research/reference/information-parity-v1/stage3-interval-feasibility-bound-v1.csv`

D-096 left 79 interval-only/unresolved teacher rows.

A deliberately generous source-only feasibility bound was applied:
- entire unresolved streams were retained where source evidence showed explicit real/live/terminal execution context;
- MetaTrader/broker-chart streams were also retained as a conservative allowance;
- row-level live proof was **not** required for inclusion in the upper bound;
- unresolved timing was assumed potentially resolvable unless the source itself made a unique M1 path unavailable.

The optimistic unresolved rescue set contains:
- 38 rows;
- 17 dates;
- 17 LONG;
- 21 SHORT.

Combining those with the four already confirmed primary rows gives an absolute optimistic maximum of:
- 42 positives;
- 20 LONG;
- 22 SHORT;
- only **17 distinct eligible dates**.

D-091 requires 20 dates.

Therefore even perfect promotion of every deliberately over-included rescue row cannot satisfy the frozen evidence-adequacy gate.

Final evidence status:
`INSUFFICIENT`

Stage 3 recognition hypothesis:
`NOT TESTED / INCONCLUSIVE`

This is not a profitability result and must not be interpreted as proof that a profitable XAUUSD system cannot be built.

Do not run the frozen FULL-vs-GOLD Stage 3 benchmark on the current pinned teacher corpus.

D-088 remains controlling. Opening 2026 market data would not solve this source-evidence inadequacy and is not authorized.

Any continuation requires a new preregistered teacher-source or teacher-definition decision; do not loosen D-089 post hoc merely to make the benchmark executable.


---

## D-098 — Full Badar source-corpus rescan changes the recommended teacher abstraction, not the D-097 result

Findings:
`research/BADAR_FULL_SOURCE_CORPUS_RESCAN_FINDINGS.md`

Badar source repository:
`alisufyan-ai7/unpack-human-trading-strategies-claude`

Current source pin for this rescan:
`19ae93aa5ee9f78766f58415fb03a8a91d86b65c`

Provenance:
everything under `derived/` was excluded.

Current corpus reviewed through source indexes/consolidations, trade table, individual current notes, Shorts compilations and representative raw frame evidence:
- 143 long videos;
- 114 Shorts;
- 45 live streams;
- 121 current live trade rows;
- 120 XAUUSD rows over 38 dates.

D-097 remains valid for its frozen exact-live-broker-entry benchmark:
`INSUFFICIENT / NOT TESTED`.

New finding:
that exact-live-broker definition is too narrow to serve as the sole supervision source for learning Badar's broader decision process.

The corpus supports a different abstraction:

**Badar is a hierarchical, stateful, risk-conditioned decision policy.**

Recurring stages:
1. build HTF/session/news context;
2. map liquidity and POIs;
3. wait for sweep/close/structure event;
4. choose entry mode;
5. choose risk tier;
6. manage dynamically.

High+medium source-confidence XAUUSD live decisions alone provide:
- 82 rows;
- 37 dates;
- 37 LONG;
- 45 SHORT;

but most source timing is interval/approximate rather than one exact minute.

Decision:
the next teacher experiment should be separately preregistered and should use:
- source trust tiers;
- interval-censored decision windows;
- separate intent / execution / outcome labels;
- explicit considered-but-rejected setups as hard negatives;
- management actions as part of the teacher policy;
- instructional/replay evidence as lower-trust auxiliary supervision.

Do not retroactively weaken D-089 or relabel D-097.

Do not access 2026 provider XAUUSD yet.

Immediate next safe research action:
draft a new Stage 3B preregistration for Badar decision-process supervision, while keeping D-088 chronology restrictions intact.

No CI is required for that design work.


---

## D-099 — Freeze Stage 3B Badar Decision-Process Supervision protocol

Preregistration:
`research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Stage 3B is a new experiment design motivated by D-098.

It does not revise D-097.

Badar Stage 3B V1 source pin:
- repository `alisufyan-ai7/unpack-human-trading-strategies-claude`;
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`;
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`.

The Badar repository advanced after D-098:
- a 46th live stream was added;
- the current trade table is 123 rows / 122 XAUUSD rows / 39 XAUUSD dates;
- the high+medium XAUUSD subset remains 82 rows across 37 dates, 37 LONG / 45 SHORT;
- full-resolution single-frame source evidence now covers all 46 streams (1,331 files).

Stage 3B changes the teacher target from exact confirmed broker fills to a source-provenance-aware decision process.

Primary source classes:
- P1 LIVE_REAL_EXECUTION;
- P2 LIVE_BADAR_COMMITMENT;
- P3 LIVE_BADAR_REJECTION.

Replay/backtest and instructional examples remain auxiliary semantic evidence only.

Primary timing:
- exact M1 or source interval up to 5 M1 minutes;
- no midpoint imputation;
- each event has total training weight 1 regardless of interval width.

Primary hard negatives:
only explicit Badar REJECT/WAIT events tied to a concrete current opportunity.

Primary tasks:
- Task A ACT vs explicit REJECT/WAIT;
- Task B LONG vs SHORT conditional on ACT.

Diagnostics:
- risk tier;
- entry mode;
- management-event extraction.

Primary source adequacy floors:
- Task A: >=40 ACT, >=40 REJECT/WAIT, >=20 paired dates;
- Task B: >=40 ACT, >=20 ACT dates, >=15 LONG, >=15 SHORT.

Primary comparison remains:
`GOLD_PRICE_ONLY` vs `FULL_INFORMATION_PARITY_V1`

with fixed L2 logistic regression, leave-one-source-date-out evaluation and event-level interval pooling.

Stage 3B PASS requires:
- source adequacy;
- Task A FULL-GOLD mean per-date ROC-AUC delta >= +0.03;
- paired date-bootstrap lower 95% bound >0;
- Task A Brier degradation <=0.01;
- Task B balanced-accuracy degradation no worse than -0.02 and Brier degradation <=0.01.

No outcome/profitability information may determine source inclusion.

D-088 remains closed:
this decision does not authorize 2026 market acquisition, joining, model fitting or provider-data CI.

Immediate next action:
construct the source-only `stage3b-source-events-v1.csv` and report the frozen Stage 3B source-evidence adequacy status before any market join.


---

## D-100 — Freeze Stage 3B source-event construction Batch 01

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH01_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch01.csv`

Pinned Badar source:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`;
- trade-table blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`.

Batch 01 represents 12 source trade rows as 11 action events after one same-plan collapse.

Primary ACT events:
- total 11;
- 8 LONG;
- 3 SHORT;
- 8 source dates.

Timing:
- 5 EXACT_M1;
- 4 INTERVAL_2M;
- 2 INTERVAL_3_TO_5M.

Provenance:
- 1 P1 live-real event;
- 10 P2 live Badar commitment events.

`m0l1wj9IZ2o#1/#2` are one split/add-on teacher event, not two independent opportunities.

Pre-stream Exness-history rows `E2Vu2bndWRc#1/#2` are deliberately not admitted because the source does not expose their contemporaneous decision process.

The source-table confidence field was used only to order this first review batch; it is not an eligibility criterion.

Stage 3B adequacy remains unresolved because construction is incomplete and P3 hard negatives have not yet been extracted.

Immediate next safe work:
continue source-only ACT construction through the remaining July rows, then begin explicit REJECT/WAIT extraction.

D-088 remains closed. No provider market data, model fitting or CI is authorized.


---

## D-101 — Complete July Stage 3B ACT review and freeze first paired hard-negative set

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH02_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch02.csv`

At the frozen Badar source pin, all 31 July XAUUSD trade-table rows are now reviewed.

Disposition:
- 29 rows represented by 28 independent ACT events;
- one same-plan add-on pair remains collapsed;
- 2 pre-stream Exness-history fills remain excluded because contemporaneous decision evidence is absent.

Batch 02 adds:
- 17 ACT events;
- 8 LONG / 9 SHORT;
- 12 explicit P3 REJECT/WAIT events.

Cumulative:
- 28 ACT;
- 16 LONG;
- 12 SHORT;
- 12 ACT dates;
- 12 REJECT/WAIT;
- 12 paired ACT+REJECT dates.

The July 28 TradingView/paper decisions remain eligible P2 decision commitments but explicitly carry PAPER_OR_SIMULATION broker status.

Legacy source-table confidence is not an eligibility rule; direct/corroborated Stage 3B source evidence controls.

Stage 3B source adequacy remains unresolved.

Immediate next safe work:
continue ACT + P3 source construction into August, with no provider market join.

D-088 remains closed. No model fitting or CI is authorized.


---

## D-102 — Freeze Stage 3B source-event Batch 03 for Aug 3-5

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH03_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch03.csv`

Scope:
all 17 pinned XAUUSD trade-table rows from 2026-08-03 through 2026-08-05.

Disposition:
- 16 eligible ACT events;
- 1 exclusion (`aEw6393GE1c#1`) because the trade was already active before the stream and the contemporaneous commitment moment is not observed.

Batch additions:
- 5 LONG;
- 11 SHORT;
- 3 explicit P3 hard negatives on 3 new dates.

Cumulative:
- 44 ACT;
- 21 LONG;
- 23 SHORT;
- 15 ACT dates;
- 15 REJECT/WAIT;
- 15 paired ACT+REJECT dates.

Task B now meets the frozen total-ACT and direction floors, but still misses the 20-date floor.

Task A remains below its reject-count and paired-date floors.

Immediate next safe work:
adjudicate Aug 6-7 source events plus paired P3 negatives.

D-088 remains closed. No provider market join, fitting or CI is authorized.


---

## D-103 — Freeze Stage 3B source-event Batch 04 for Aug 6-7

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH04_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch04.csv`

Scope:
all 8 pinned XAUUSD trade-table rows on 2026-08-06 and 2026-08-07.

Result:
- 8 eligible ACT events;
- 4 LONG / 4 SHORT;
- 8 E1 DIRECT;
- 1 P1 live-real event;
- 7 P2 live Badar commitment events;
- 2 paired P3 REJECT/WAIT events.

Cumulative:
- 52 ACT;
- 25 LONG;
- 27 SHORT;
- 17 ACT dates;
- 17 REJECT/WAIT;
- 17 paired ACT+REJECT dates.

Task B now needs only 3 more distinct ACT dates; its count and direction floors are already met.

Task A still needs 23 more explicit REJECT/WAIT events and 3 more paired dates.

Immediate next safe work:
adjudicate Aug 13 and Aug 17, and begin collecting multiple valid P3 events per date rather than only one paired negative.

D-088 remains closed. No provider market join, fitting or CI is authorized.


---

## D-104 — Freeze Stage 3B source-event Batch 05 for Aug 13 + 17

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH05_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch05.csv`

Scope:
all six pinned XAUUSD trade-table rows on Aug 13 and Aug 17 plus all distinct source-supported P3 decisions reviewed in this bounded chunk.

ACT disposition:
- 4 primary-eligible ACT;
- 2 London chart-box rows excluded because Badar personal commitment is not established at E1/E2 confidence.

New P3 events:
- 11 total;
- 6 on Aug 13;
- 5 on Aug 17.

Cumulative:
- 56 ACT;
- 27 LONG;
- 29 SHORT;
- 19 ACT dates;
- 28 REJECT/WAIT;
- 19 paired ACT+REJECT dates.

Task B now needs only 1 additional ACT date.

Task A needs:
- 12 additional explicit P3 events;
- 1 additional paired date.

Multiple P3 events on one date are retained only when they represent materially distinct later decision states; arbitrary no-trade minutes remain prohibited.

Immediate next safe work:
adjudicate Aug 28 + Aug 31, prioritizing at least one paired P3 on the next ACT date and continuing the explicit reject-event count.

D-088 remains closed. No provider market join, fitting or CI is authorized.


---

## D-105 — Freeze Stage 3B source-event Batch 06; minimum numerical adequacy floors are now reached

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH06_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch06.csv`

Scope:
all six pinned XAUUSD trade-table rows on Aug 28 and Aug 31 plus every distinct explicit P3 decision found in the bounded source review.

Batch:
- 6 ACT;
- 2 LONG / 4 SHORT;
- 4 P1 live-real;
- 2 P2 live Badar commitments;
- 13 explicit P3 REJECT/WAIT events.

Cumulative through August:
- 62 ACT;
- 29 LONG;
- 33 SHORT;
- 21 ACT dates;
- 41 REJECT/WAIT;
- 21 paired ACT+REJECT dates.

The minimum D-099 numerical source floors are now met for both Task A and Task B.

This does **not** authorize stopping construction at the threshold.

The pinned corpus still contains September/October source dates. Stage 3B V1 must continue chronologically and freeze the complete source-derived event table before any market join.

Therefore:
- minimum adequacy = numerically reached;
- final source adequacy certification = pending complete source construction + QA;
- D-088 remains closed.

Immediate next safe work:
Sep 2 + Sep 4 source-only ACT/P3 adjudication.

No provider market data, fitting or CI is authorized.


---

## D-106 — Freeze Stage 3B source-event Batch 07 for Sep 2 + Sep 4

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH07_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch07.csv`

Scope:
all eight pinned XAUUSD trade-table rows on Sep 2 and Sep 4 plus all distinct explicit P3 decisions retained in this bounded review.

Result:
- 8 source rows -> 7 independent ACT events;
- 4 LONG / 3 SHORT;
- 5 P1 / 2 P2;
- 12 new P3 events.

`B83jlxwuo10#2/#3` are collapsed as one short decision because the latter is the retained small piece of the same original entry.

Cumulative:
- 69 ACT;
- 33 LONG;
- 36 SHORT;
- 23 ACT dates;
- 53 REJECT/WAIT;
- 23 paired ACT+REJECT dates.

Both numerical D-099 adequacy gates remain met.

A required final-QA backfill is now explicit:
D-099 permits committed unfilled resting orders as ACT events, while the live-trade table can omit them.

Therefore after the chronological table-row review is complete, scan all pinned live streams for non-table ACT commitments before final merge/hash.

Immediate next safe work:
Sep 14 + Sep 15 source-only adjudication.

D-088 remains closed. No provider market join, fitting or CI is authorized.


---

## D-107 — Freeze Stage 3B source-event Batch 08 for Sep 14 + Sep 15

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH08_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch08.csv`

Scope:
all eight pinned XAUUSD trade-table rows on Sep 14 and Sep 15 plus all distinct explicit Badar P3 decisions retained in this bounded review.

Disposition:
- 8 source rows -> 6 independent Badar ACT events;
- 3 LONG / 3 SHORT;
- all 6 P2;
- 16 new P3 events.

`C18mm9p2oW4#1/#2` are one split sell decision.

`C18mm9p2oW4#4` is excluded because it is Zain's trade after Badar hands over the screen.

Low-confidence Sep 15 rows are retained where the pinned source itself provides E1/E2 Badar commitment evidence; legacy table confidence is not an eligibility rule.

Cumulative:
- 75 ACT;
- 36 LONG;
- 39 SHORT;
- 25 ACT dates;
- 69 REJECT/WAIT;
- 25 paired ACT+REJECT dates.

All D-099 numerical adequacy floors remain exceeded.

The mandatory final non-table ACT backfill is reinforced by Sep 14's explicitly committed but unfilled 4302 sell limit.

Immediate next safe work:
Sep 16 + Sep 17 source-only adjudication.

D-088 remains closed. No provider market join, fitting or CI is authorized.


---

## D-108 — Freeze Stage 3B source-event Batch 09 for Sep 16 + Sep 17

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH09_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch09.csv`

Scope:
all six pinned XAUUSD trade-table rows on Sep 16 and Sep 17 plus all distinct explicit Badar P3 decisions retained in this bounded review.

Disposition:
- 6 source rows -> 4 independent Badar ACT events;
- 3 LONG / 1 SHORT;
- 1 P1 / 3 P2;
- 12 new P3 events.

`y2Oun9g9abk#2` is excluded because the source is contradictory about whether Badar personally took the sell; later profit language does not resolve the ownership/action ambiguity.

`6trb-6A2t6Q#1/#2` collapse into one scaled P1 long because Badar explicitly combines the two positions by average rate and manages them as one plan.

Cumulative:
- 79 ACT;
- 39 LONG;
- 40 SHORT;
- 27 ACT dates;
- 81 REJECT/WAIT;
- 27 paired ACT+REJECT dates.

All D-099 numerical adequacy floors remain exceeded.

The mandatory non-table ACT backfill is again supported by Sep 17's explicitly placed-but-unfilled limit order.

Immediate next safe work:
Sep 18 + Sep 21 source-only adjudication.

D-088 remains closed. No provider market join, fitting or CI is authorized.


---

## D-109 — Freeze Stage 3B source-event Batch 10 for Sep 18 + Sep 21

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH10_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch10.csv`

Scope:
all four pinned XAUUSD trade-table rows on Sep 18 and Sep 21 plus all distinct explicit Badar P3 decisions retained in this bounded review.

Disposition:
- 4 source rows -> 3 primary Badar ACT events;
- 2 LONG / 1 SHORT;
- 2 P1 / 1 P2;
- 13 new P3 events.

`qTSedn6hEp8#3` is conservatively excluded because the source documents the trade plan/result but does not establish Badar's own current commitment strongly enough for E1/E2 personal ACT ownership.

Cumulative:
- 82 ACT;
- 41 LONG;
- 41 SHORT;
- 29 ACT dates;
- 94 REJECT/WAIT;
- 29 paired ACT+REJECT dates.

All D-099 numerical adequacy floors remain exceeded.

Immediate next safe work:
Sep 22 + Sep 23 source-only adjudication.

D-088 remains closed. No provider market join, fitting or CI is authorized.


---

## D-110 — Freeze Stage 3B source-event Batch 11 for Sep 22 + Sep 23

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH11_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch11.csv`

Sep 22 has no pinned XAUUSD trade-table row and no indexed source hit.

Sep 23:
- 3 source trade rows reviewed;
- 1 primary Badar ACT event;
- 2 rows excluded as OTHER_PERSON because they are Zain's trades on Zain's OANDA chart;
- 1 SHORT / P2 / E1;
- 7 new P3 events.

`OpMzvMNNrHM#3` is retained because the stream returns to Badar's own chart and he directly commits: `It is not completely closed inside. But let's do it.`

Cumulative:
- 83 ACT;
- 41 LONG;
- 42 SHORT;
- 30 ACT dates;
- 101 REJECT/WAIT;
- 30 paired ACT+REJECT dates.

All D-099 numerical adequacy floors remain exceeded.

Final QA must explicitly account for every source row, including other-person exclusions, rather than assuming every trade-table row maps to a Badar event.

Immediate next safe work:
Sep 24 + Sep 25 source-only adjudication.

D-088 remains closed. No provider market join, fitting or CI is authorized.


---

## D-111 — Freeze Stage 3B source-event Batch 12 for Sep 24 + Sep 25

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH12_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch12.csv`

Scope:
all four pinned XAUUSD trade-table rows on Sep 24 and Sep 25 plus all distinct explicit Badar P3 decisions retained in this bounded review.

Disposition:
- 4 source rows -> 2 primary Badar ACT events;
- both SHORT / P2 / E1;
- 13 new P3 events.

Excluded:
- `U5CphnzaXio#2` — optional/viewer re-sell; Badar explicitly says he did not place it;
- `1E65DgTFxe0#1` — pre-stream Badar trade, so the contemporaneous live commitment event is unavailable.

Cumulative:
- 85 ACT;
- 41 LONG;
- 44 SHORT;
- 32 ACT dates;
- 114 REJECT/WAIT;
- 32 paired ACT+REJECT dates.

All D-099 numerical adequacy floors remain exceeded.

Immediate next safe work:
Sep 28 + Sep 29 source-only adjudication.

D-088 remains closed. No provider market join, fitting or CI is authorized.


---

## D-112 — Freeze Stage 3B source-event Batch 13 for Sep 28 + Sep 29

Findings:
`research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH13_FINDINGS.md`

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch13.csv`

Scope:
all eight pinned XAUUSD trade-table rows on Sep 28 and Sep 29 plus all distinct explicit Badar P3 decisions retained in this bounded review.

Disposition:
- 8 source rows -> 8 primary Badar ACT events;
- 2 LONG / 6 SHORT;
- 8 P2;
- 7 E1 / 1 E2;
- 16 new P3 events.

Sep 29 #4 remains Badar-owned despite being displayed on Zain's laptop because Badar explicitly compares the displayed SL with `my SL` and manages the current decision. It remains P2 because no live-real Badar broker account is shown.

Cumulative:
- 93 ACT;
- 43 LONG;
- 50 SHORT;
- 34 ACT dates;
- 130 REJECT/WAIT;
- 34 paired ACT+REJECT dates.

All D-099 numerical adequacy floors remain exceeded.

Immediate next safe work:
Sep 30 + Oct 1 source-only adjudication.

The mandatory non-table ACT backfill and source-row coverage audit remain required before final source certification.

D-088 remains closed. No provider market join, fitting or CI is authorized.


---

## D-113 — Freeze Stage 3B source-event Batch 14 for Sep 30 + Oct 1

Findings: `research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH14_FINDINGS.md`
Artifact: `research/reference/information-parity-v1/stage3b-source-events-v1-batch14.csv`

Four pinned XAUUSD source trade rows resolved into two Badar-owned P2/E1 SHORT ACT decisions. Sep 30 #1 excluded: team/VIP trade, Badar explicitly did not take it. Sep 30 #2/#3 collapsed to one current sell thesis with a smaller follow-on entry. Oct 1 #1 is a separate M15-close short. Seven distinct explicit Badar P3 REJECT/WAIT decisions retained (Sep 30 three; Oct 1 four), avoiding generic teaching and repeated same-plan conditions.

Cumulative: 95 ACT / 43 LONG / 52 SHORT / 36 ACT dates / 137 P3 REJECT-WAIT / 36 paired dates. Numerical D-099 floors exceeded; final source QA outstanding.

Immediate next source-only work: Oct 2, Oct 6 and Oct 8, then non-table ACT backfill and complete source-row/temporal/timezone audit and final merged CSV/hash. D-088 closed, no market joins/fitting/CI.


---

## D-114 — Freeze Stage 3B source-event Batch 15 for Oct 2 + Oct 6 + Oct 8

Findings: `research/INFORMATION_PARITY_V1_STAGE3B_SOURCE_EVENTS_BATCH15_FINDINGS.md`.
Artifact: `research/reference/information-parity-v1/stage3b-source-events-v1-batch15.csv`.

Nine remaining pinned XAUUSD table rows reviewed; seven Badar ACT (four LONG, three SHORT). Oct 2 five decisions (four P2 longs and an independently verified P1 Exness real short), Oct 6 one P2 short, Oct 8 one P2/E2 short. Oct 6 #1 excluded as pre-stream/co-host-owned or unclear Badar commitment; Oct 8 #2 excluded as position-tool only. Seven distinct explicit P3 events added (Oct 2 four, Oct 6 two, Oct 8 one).

Provisional cumulative: **102 ACT / 47 LONG / 55 SHORT / 39 ACT dates / 144 P3 / 39 paired dates**. Numerical D-099 adequacy exceeded; backfill and comprehensive QA pending. Next: mandatory non-table ACT search and full original source-row disposition audit. D-088 closed; no provider join, fitting, CI.


---

## D-115 — Freeze mandatory Stage 3B non-table ACT backfill

Artifact: `research/reference/information-parity-v1/stage3b-source-events-v1-backfill.csv`.
Findings: `research/INFORMATION_PARITY_V1_STAGE3B_NON_TABLE_BACKFILL_FINDINGS.md`.

All 46 pinned stream notes screened for unfilled and missing-table commitments, with targeted transcript/source note checks. Five independent Badar P2 unfilled SHORT resting-limit commitments retained (Jul 7, Jul 23, Sep 2, Sep 14, Sep 17). Competing conditional, tutorial, ambiguous, unconfirmed or same-plan duplicate candidates excluded/documented. No broker P1 status assigned to unfilled orders.

Cumulative now 107 ACT / 47 LONG / 60 SHORT / 39 ACT dates / 144 P3 / 39 paired dates. Final QA and schema correction still required before source certification. D-088 closed; no market join/CI/fitting.


---

## D-116 — Freeze final Stage 3B source-only event table and row-by-row QA

Findings: `research/INFORMATION_PARITY_V1_STAGE3B_FINAL_SOURCE_QA_FINDINGS.md`.
Canonical event CSV: `research/reference/information-parity-v1/stage3b-source-events-v1.csv` (SHA-256 `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd`).
One-row-per-pinned-trade disposition CSV: `research/reference/information-parity-v1/stage3b-source-row-dispositions-v1.csv` (SHA-256 `bf9fed8d952b9a0195ef1bfa3b036ba1e5489daec1169c7075ac36968a722604`). Freeze manifest: `research/reference/information-parity-v1/stage3b-source-freeze-manifest-v1.json`.

**251 canonical events, 250 primary eligible: 107 ACT / 47 LONG / 60 SHORT / 39 ACT dates / 143 eligible P3 / 39 paired dates**. Source evidence passes all D-099 numeric floors. Original 123 trade-table rows all dispositioned: 107 source keys attached to 102 ACT after five same-plan collapses, 16 excluded (including one BTC), no unresolved row; plus five non-table ACT backfilled under D-115.

Canonical-only deterministic changes: fix six Batch01 rows with a surplus blank CSV field; retain but exclude `S3B-REJ-0141` as a primary session-stop negative because `S3B-ACT-0100` follows on the same stream minutes later. Prior frozen batches untouched. No provider XAUUSD, fitting, CI, broker or sealed-year access. This is **source adequacy**, not statistical recognition success; D-088 chronology stays CLOSED. D-097 remains INSUFFICIENT/NOT TESTED.


---

## D-117 — Review the D-088 chronology/reserve boundary without opening it

Review: `research/INFORMATION_PARITY_V1_STAGE3B_CHRONOLOGY_GATE_REVIEW.md`.

D-116 has certified source-only Stage 3B evidence adequacy but accepted information states exist only for 2016–2021 TRAIN while the pinned Badar teacher cohort is from reserved 2026. Three legitimate routes are documented: (A) maintain 2026 reserve and seek TRAIN-overlapping expert source; (B) an expressly owner-approved separately preregistered bounded 2026 teacher-window repurpose with disjoint shadow holdout and no hindsight; (C) stop this teacher-market join without false inference. **No new 2026 exception was selected or authorized. D-088 remains CLOSED** pending explicit owner decision; 2022–2025 sealed, no provider join/fitting/CI/Stage4-5/live execution. This is governance review, not a completed recognition benchmark.


---

## D-118 — Owner accepts Option B in principle; bounded 2026 protocol proposed, no data authorization

The owner expressly approves **design of a bounded 2026 Badar teacher–market protocol in principle**, and expressly forbids provider acquisition or fitting until a **second explicit final approval**.

Proposal: `research/INFORMATION_PARITY_V1_STAGE3B_2026_BOUNDED_PROTOCOL_PROPOSAL.md`.
Final-approval checklist: `research/INFORMATION_PARITY_V1_STAGE3B_2026_FINAL_APPROVAL_CHECKLIST.md`.

Proposed warm-up `2026-06-01T00:00:00Z` to `2026-07-06T00:00:00Z`; retrospective teacher period `2026-07-06T00:00:00Z` to `2026-10-09T00:00:00Z` (39 frozen source dates), disjoint zero-use embargo `2026-10-09T00:00:00Z` to `2026-12-01T00:00:00Z`, separate prospective shadow `2026-12-01T00:00:00Z` to `2027-01-01T00:00:00Z`. Proposed restricted source set: Dukascopy XAUUSD BID/ASK + six FX BID M1 for synthetic DXY + first-party macro schedule. Proposed one-run/350MiB raw/750MiB normalized ceilings; **no actual acquisition approved**. The complete exact feature allowlist, runtime and no-provider deterministic preflights are still prerequisites to requesting execution authorization.

D-088 **CLOSED**; Stage 3B model **NOT TESTED**, Stage 4/5 blocked, 2022–2025 sealed. Owner's in-principle approval may not be used as an execution token.


---

## D-119 — Freeze owner-independent Stage 3B bounded-2026 code/source preflight; retain execution blocks

Exact static feature allowlist: `research/reference/information-parity-v1/stage3b-2026-feature-allowlists-v1.json` SHA-256 `44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104` (92 GOLD, 63 extra FULL = 155 FULL). Frozen source-date LODO: `research/reference/information-parity-v1/stage3b-2026-teacher-folds-v1.json` SHA-256 `56a1c301cfebc78373793db10d7099aab9391b33e1470c869b714261ba677ec5` (39 folds, 250 eligible events, 343 candidate-minute expansions, weight mass 250). Provider-free deterministic module/tests in `scripts/stage3b_2026_preflight.py` and `tests/test_stage3b_2026_preflight.py`, byte identities recorded in `research/INFORMATION_PARITY_V1_STAGE3B_2026_PREFLIGHT_QA_FINDINGS.md`. 11/11 local Python 3.13.5 stdlib tests passed; exact Stage 3B solver runtime only **specified**, not installed/reproduced. No CI.

Public primary agency macro pages and official Dukascopy access documentation/terms reviewed. **Critical external gate:** Bank terms restrict automated access without prior express written consent, and the project's requested usage has not been independently licensed. **Scientific state gate:** accepted Stage2 FVG/last-confirmed-swing can persist unboundedly so proposed June1 warm-up cannot be certified equivalent from fixed windows alone. Macro future schedule as-of versions remain partly unverified. All remain explicit pending blockers; no provider rows or fitted models.

D-118 design-only approval remains in force; **D-088 CLOSED**, sealed 2022–2025 intact, no 2026 market acquisition, CI, fitting, Stage4/5 or broker. A separate execution approval **cannot** be requested as ready until rights, warm-up, macro and exact runtime blockers are resolved.


---

## D-120 — Record owner-confirmed provider permission; advance bounded 2026 no-provider preflight

Owner affirmatively states possession of written permission or licence for automated Dukascopy historical-data acquisition. This **closes the repeated licence-evidence owner-input question** on an owner-attestation basis; no licence contents or credentials added to GitHub. It does not grant D-118 final scientific execution approval or waive the data budget.

New `research/INFORMATION_PARITY_V1_STAGE3B_2026_D120_FINDINGS.md`, `research/reference/information-parity-v1/stage3b-2026-macro-asof-evidence-v1.json`, `scripts/stage3b_2026_addendum.py`, `tests/test_stage3b_2026_addendum.py`. Calendar review records FOMC's 2024 advance publication and BLS 2026 monthly modification dates, distinguishing reliable earlier schedule from post-release hindsight; unverified future schedules remain missing. Stage 2's indefinite FVG/swing carry requires a **disclosed June1 bounded cold-start** as an initialization addendum for owner final approval, *not* a scope expansion or false 2016–2021 full-history-equivalence claim.

Combined no-provider local standard-library tests **17/17 PASS**, compileall PASS; no CI, provider acquisition or fitting. Exact CPython3.12 environment and full event-calendar coverage remain implementation verification, not a new user permission request. **D-088 CLOSED** until the separately required final approval.


---

## D-121 — Commit source-only bounded 2026 acquisition manifest and final-approval guards

Owner-confirmed data access was recorded under D-120. D-121 adds **no provider or market data**. New immutable design manifest `research/reference/information-parity-v1/stage3b-2026-acquisition-preflight-v1.json` (source bounds, eight symbols, one-attempt 350 MiB raw / 750 MiB normalized limits, separate shadow/quarantine, `owner_final_execution_approval_commit=null`). The additional `scripts/stage3b_2026_execution_preflight.py` / `tests/test_stage3b_2026_execution_preflight.py` check manifest identities/approval and inspect package versions without training or network activity.

Combined local standard-library synthetic tests: **21/21 PASS**, CPython 3.13.5 (exact pinned 3.12.14 runtime and pandas/numpy versions **NOT** reproduced). Macro schedule unknowns fail closed to an explicitly unavailable year instead of hindsight. Proposed June1 bounded state initialization is a recognized limitation, **not** claimed full-history Stage2 equivalence. Technical disclosure in `research/INFORMATION_PARITY_V1_STAGE3B_2026_D121_FINDINGS.md`.

D-088 CLOSED; no CI/provider job, training, broker use, shadow data or sealed evaluation years. Final approval is still withheld by the owner and must be expressly requested only when exact-runtime/implementation checks are ready.


---

## D-122 — Harden D-121 execution approval check; synthetic suite 22/22 PASS

The D-121 code accepted any manually supplied 40-hex commit SHA when `status=FINAL_APPROVED` was set, despite no actual owner approval. Corrected `scripts/stage3b_2026_execution_preflight.py` to require membership in `AUTHORIZED_FINAL_DECISION_SHAS`, deliberately **empty** until a later reviewed owner-approved code change. The manifest alone can never enable provider execution; still no downloader/model in this module.

Updated `tests/test_stage3b_2026_execution_preflight.py` tests forged SHA rejection plus the empty allowlist. Combined synthetic local standard-library suite **22/22 PASS**, no CI or provider data. Findings: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D122_FINDINGS.md`.

The owner's existing Dukascopy licence affirmation stands, no further paperwork requested. D-088 **CLOSED**; final scientific owner approval withheld. Exact pinned Python 3.12.14 environment remains unverified in current offline runtime and future no-provider integration preflight remains technical work.


---

## D-123 — Make GitHub-enforced chat continuity/documentation discipline mandatory

Owner states that this is **Chat 04** and GitHub is the project source of truth. Before chat rollover, a ready new-chat prompt must exist so a successor chat can reconstruct all current progress from GitHub rather than conversation memory. Owner also requires project documentation to remain maintained after each execution.

Added:
- `research/PROJECT_DOCUMENTATION_PROTOCOL.md` — mandatory post-execution documentation/verification checklist and owner-escalation rules;
- `research/NEW_CHAT_PROMPT.md` — ready-to-copy **Chat 05** bootstrap prompt with branch, authoritative reading order, frozen identities, current scientific restrictions and immediate owner-independent work;
- refreshed `research/NEW_CHAT_HANDOFF.md` for **Chat 04 -> Chat 05**.

Operating rule: after each material execution, update decision/continuity/handoff/prompt as applicable, update README when high-level state changes, commit on the active branch, and verify branch HEAD before reporting completion. Never rely on chats as the only repository of project state. Already-recorded owner inputs must not be repeatedly requested.

This decision changes documentation/process only. D-088 remains CLOSED and D-122 scientific/data restrictions remain unchanged.


---

## D-124 — Owner grants final bounded 2026 Stage 3B acquisition/model authorization

Owner explicitly grants the final approval reserved by D-118–D-123: proceed with the frozen bounded 2026 provider acquisition and preregistered Stage 3B model fitting/evaluation **without any further approval request**. Detailed authorization: `research/INFORMATION_PARITY_V1_STAGE3B_2026_FINAL_AUTHORIZATION.md`.

Authorized only: `2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z`; XAUUSD BID/ASK plus six FX BID series for synthetic DXY; one capped provider attempt; D-120 bounded June1 cold start; D-121 macro fail-closed policy; D-116 teacher corpus; frozen L2 logistic Task A/Task B, 39-date LODO, bootstrap and advancement rule. A narrowly targeted exact-runtime/provider CI job is permitted when needed to execute this package.

Still prohibited: 2022–2025, Oct9–Nov30 2026, December shadow, 2027, new symbols/providers/features/models/hyperparameters, Stage4/5 automatic execution, macro outcome values, broker/order mutation.

**D-088 is partially superseded only for this exact D-124 bounded exception.** Next implementation must admit the exact D-124 commit SHA into the final-approval allowlist and machine-readable plan before any provider call. No further owner approval is needed for the authorized package.


---

## D-125 — Admit exact D-124 SHA and trigger one no-provider exact-runtime preflight

D-124 commit `c99ad84e4b7254d074b96df7a5f4c371ccbe01c2` is the sole approved final-decision SHA in the Stage 3B execution guard and machine-readable plan. The plan changes to FINAL_APPROVED for that exact scope. Added a CPython 3.12.14/full-lock environment checker and a path-isolated workflow triggered only by `.github/stage3b-2026-exact-preflight-trigger`. The triggered job downloads **no provider market data** and fits **no model**; it is justified because the current local Python 3.13.5 environment cannot certify the frozen runtime. Findings: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D125_FINDINGS.md`.


---

## D-126 — Exact Stage 3B runtime preflight PASS

GitHub Actions run **45896702785** / job **140172268991** on D-125 head `15b408dbffbf43e9eee0e124ff506ade119f7fc5` succeeded. Verified CPython3.12.14 and the complete frozen Stage3B package lock; **22/22** guard tests passed and D-124 authorization/source hashes were verified. No market data or fitting. Exact-runtime blocker is resolved; proceed to the single authorized bounded provider/build/benchmark implementation and one-attempt execution after static guard review.


---

## D-127 — Implement bounded provider/build/benchmark pipeline; rehearse end-to-end with fake market data first

Implemented the production D-124 pipeline before spending the single provider attempt:
- strict eight-series Jun1–Oct9 provider validator and raw-byte cap;
- bounded June1 cold-start layer builder reusing accepted Stage2 causal transforms;
- exact D-116 teacher join: 250 eligible events / expected 343 source candidate minutes;
- frozen GOLD/FULL L2 logistic, 39 source-date LODO, event/class weighting, event mean pooling, Task A/Task B metrics, 10,000 paired-date bootstrap and frozen advancement rule;
- one-attempt acquisition wrapper with raw provider deletion before artifact upload;
- production provider workflow guarded by a **separate trigger path that is not yet present**.

D-127 itself triggers only `.github/workflows/stage3b-2026-pipeline-preflight.yml`, which generates deterministic fake market state around the real frozen teacher times and runs the entire pipeline under the exact runtime. This rehearsal makes no provider market call. The one real D-124 attempt may be triggered only after this synthetic workflow passes and its result is recorded.

Findings: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D127_FINDINGS.md`.


---

## D-128 — D-127 synthetic pipeline PASS; real-attempt workflow gate repaired before provider access

Synthetic exact-runtime run **45897637362** (job **140175383322**) PASSED the whole fake-market rehearsal using the real frozen teacher/features/folds. The printed fake-market scientific classification is ignored.

GitHub production run record **45897634530** contained zero jobs and therefore did not execute provider/model code. It is classified as a workflow-validation/trigger-surface failure, **not** the single provider attempt. D-128 replaces the invalid/brittle surface with a fixed workspace and requires the exact D-124 execution commit marker, exact trigger-file contents and `GITHUB_RUN_ATTEMPT=1` before acquisition. The real trigger remains absent in this commit.

Findings: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D128_FINDINGS.md`.


---

## D-129 — Fix production workflow YAML and validate parser with a non-authorizing trigger

D-128 no-provider synthetic run **45897995539** succeeded. Production workflow records 45897634530 and 45897993636 had zero jobs: the YAML parser rejected an unindented heredoc block before any runner existed. They are not provider attempts.

D-129 fixes the YAML with an indentation-safe `printf` trigger comparison. A placeholder `.github/stage3b-2026-authorized-trigger` is committed with explicit validation-only content; the commit message contains no execution marker, so the provider job must be skipped even though the workflow path matches. This validates workflow parsing without market access.

Findings: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D129_FINDINGS.md`.


---

## D-130 — Trigger the one authorized real provider/build/Stage 3B benchmark run

D-129 production parse validation **45898223471** was skipped as intended and confirms the repaired workflow parses without executing provider code. D-130 replaces the validation-only trigger with the exact D-124 payload and commit marker `[STAGE3B_PROVIDER_EXECUTE_D124]`.

This is the **single** real provider attempt authorized by D-124. Rerun is forbidden; `GITHUB_RUN_ATTEMPT=1` is enforced before download. Scope is unchanged: Jun1–Oct9 exclusive, eight frozen M1 series, cold-start/fail-closed macro, frozen teacher/features/folds/model/gate, compact evidence only.

Findings/trigger record: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D130_FINDINGS.md`.


---

## D-131 — Correct D-130 pre-checkout guard failure; provider attempt remains unspent

D-130 run **45898387479** reached a runner but failed before repository checkout at `test -f .github/stage3b-2026-authorized-trigger`. Checkout, runtime setup, provider acquisition, dataset construction and model fitting were all skipped. This is an orchestration defect, not a provider attempt.

D-131 moves checkout ahead of the trigger guard, changes the future exact trigger payload to D-132, and adds a regression assertion that Checkout precedes the immutable-trigger guard. The D-131 commit updates only the synthetic preflight trigger for one no-provider revalidation. It does not change the production trigger file, so real acquisition cannot start from D-131.

Findings: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D131_FINDINGS.md`.


---

## D-132 — Spend the single D-124 provider acquisition attempt after all preflight gates pass

D-131 exact-runtime no-provider regression run **45898582347** succeeded. D-132 now replaces the prior trigger contents with the exact payload accepted by the hardened production workflow and includes `[STAGE3B_PROVIDER_EXECUTE_D124]` in the commit message.

D-132 is the single real acquisition attempt. No rerun is allowed. The run is restricted to the D-124 date/symbol/budget/cold-start/macro/model scope; outputs are compact evidence only after raw/derived payload removal.

Findings/trigger record: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D132_FINDINGS.md`.


---

## D-133 — Consume D-124 attempt on zero-byte provider transport failure; Stage 3B NOT TESTED

D-132 run **45898796339** / job **140179219355** reached the first XAUUSD BID provider request and received a zero-byte output. The local non-empty-file guard stopped execution. No subsequent provider series, normalized layer, candidate dataset or model fit occurred.

The single D-124 provider attempt is therefore **consumed**. Stage 3B is `NOT TESTED`, not negative. Compact artifact **15155230246** (digest `sha256:1ffaac4dc19f6b4edaf8075ef197a53cd0b182fabf57bf7d7dfe0ace92cf8e14`) contains only failure bookkeeping.

The frozen transport was dukascopy-node 1.50.0. Upstream issue #261 documents WAF-202 empty-result behavior in older JSON-API transport; #264 documents current WAF 202/403 failures; 1.51.1 later added export-widget headers/tighter 403 handling. This supports a transport-failure diagnosis but does not prove D132's exact HTTP code.

Execution is now fail-closed: machine plan status `ATTEMPT_CONSUMED_PROVIDER_TRANSPORT_FAILURE`, provider/model/CI flags false, authorization allowlist empty. A proposed transport-only recovery using pinned 1.51.1 preserves all scientific scope but requires one new explicit owner authorization for one new provider attempt.

Findings: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D133_PROVIDER_FAILURE_FINDINGS.md`.
Recovery proposal: `research/INFORMATION_PARITY_V1_STAGE3B_2026_PROVIDER_TRANSPORT_RECOVERY_PROPOSAL.md`.


---

## D-134 — Owner authorizes one pinned 1.51.1 transport-recovery attempt

The owner explicitly authorizes the D-133 recovery proposal: exactly one new provider-recovery attempt using `dukascopy-node 1.51.1`, while preserving the complete D-124 scientific scope and sealed-period/broker restrictions. The same-attempt XAUUSD BID sanity request is authorized as proposed.

Provider access remains disabled until implementation: the exact D-134 commit SHA must be admitted into the recovery guard/manifest, 1.51.1 must be pinned, WAF/HTTP diagnostics added, and no-provider exact-runtime regression must pass. After that, no further owner approval is required. Recovery failure may not be rerun.

Authorization record: `research/INFORMATION_PARITY_V1_STAGE3B_2026_TRANSPORT_RECOVERY_AUTHORIZATION.md`.


---

## D-135 — Implement pinned 1.51.1 recovery transport and run no-provider regression

D-134 SHA `8cdd4edf222b88ac1d7ce15e3d3ac8639a2be155` is admitted by a new recovery guard. Added separate 1.51.1 downloader, WAF/HTTP diagnostics/classification, ephemeral token-cache handling, Jun1→Jun2 XAUUSD BID sanity identity, and recovery acquisition wrapper. Scientific dates/symbols/teacher/features/folds/models/thresholds remain unchanged.

Machine plan status becomes `RECOVERY_AUTHORIZED_PREFLIGHT_PENDING`; provider/model/CI-provider flags stay false. D-135 triggers only the exact-runtime synthetic/no-market-provider preflight, including exact 1.51.1 CLI flag checks and matching Chromium installation. No Dukascopy market request occurs in this commit.

Findings: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D135_RECOVERY_IMPLEMENTATION_FINDINGS.md`.


---

## D-136 — Record D-135 PASS and trigger the one D-134 transport-recovery attempt

D-135 exact-runtime/no-market-provider run **45901246019** / job **140187267884** PASSED with Node22.23.3, npm10.9.9, Python3.12.14, matching 1.51.1 Chromium and 30/30 deterministic tests. Synthetic end-to-end teacher/model plumbing also passed.

D-136 changes recovery state to `RECOVERY_READY_ONE_ATTEMPT`, enables provider/model execution only for the D134 recovery scope, and adds the one-time `stage3b-2026-transport-recovery` workflow. The workflow is fail-closed on exact trigger, preflight identity and run_attempt=1. No rerun is authorized.

Findings: `research/INFORMATION_PARITY_V1_STAGE3B_2026_D136_RECOVERY_TRIGGER_FINDINGS.md`.
