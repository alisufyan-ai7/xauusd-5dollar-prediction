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
