# Project Continuity — XAU/USD $5 Directional Prediction

## Purpose

This file is the durable handoff context for future ChatGPT chats working on this project.

A new chat should read this file together with the linked decision/specification documents before making changes.

## Clean-room scope

Allowed project context:

1. this repository;
2. the current project chat in which a decision is being made;
3. fresh public research/data gathered specifically for this project;
4. Exness information supplied in-project or freshly verified from public sources.

Do not import conclusions, code, datasets, strategies, or assumptions from unrelated chats, account-level memory, or other GitHub repositories.

## Core research question

Can XAU/USD market states be identified where, from decision price P:

- BUY target P + $5 is reached before P - $3;
- SELL target P - $5 is reached before P + $3;
- within 60 minutes;
- using only information available at the decision timestamp?

The system may output BUY, SELL, or NO TRADE.

The goal is not to force trades. High-confidence states may be rare.

## Current research architecture

The intended system should observe markets in the style of a disciplined expert XAU/USD trader while remaining measurable, reproducible, and statistically testable.

Conceptual flow:

1. market observation;
2. context/regime interpretation;
3. setup recognition;
4. probability estimation;
5. confluence/quality assessment;
6. BUY / SELL / NO TRADE;
7. deterministic execution and risk management.

The system should imitate expert decision structure, not human weaknesses such as FOMO, revenge trading, arbitrary trade quotas, moving stops emotionally, or hindsight pattern fitting.

See: research/EXPERT_TRADER_OBSERVATION_MODEL.md

## Current experiment

EXP-001 is the initial feasibility experiment.

Frozen label semantics:

- decision price: close of current M1 bar;
- decision time: next minute boundary;
- forward scan starts at the next M1 bar;
- horizon: 60 calendar minutes;
- BUY success: +$5 before -$3;
- SELL success: -$5 before +$3;
- same-bar target/adverse touch: AMBIGUOUS;
- neither barrier: UNRESOLVED;
- no invented sub-minute ordering.

## Historical data

Primary source: free public Dukascopy XAU/USD M1 BID data.

Frozen historical research window:

- 2016-01-01 through 2025-12-31.

2026 is kept outside historical development for later forward/shadow comparison.

First admitted full-history run:

- GitHub Actions run: 36029810579
- total rows: 3,542,055
- yearly hashes pinned in research/EXP-001_DATASET_LOCK.json

A later download produced a transient 2020 mismatch of 120 rows. A targeted locked re-acquisition subsequently reproduced the admitted 2020 file exactly. All future research inputs must match the pinned dataset lock.

## Frozen chronological partitions

- TRAIN: 2016-2021
- VALIDATION: 2022
- DEVELOPMENT_TEST: 2023-2024
- FINAL_OOS: 2025
- 2026: reserved for later forward/shadow comparison

FINAL_OOS 2025 must not be used for feature selection, model selection, threshold tuning, or hyperparameter tuning.

## Current implementation status

Implemented:

- clean-room repository/context policy;
- EXP-001 preregistration;
- public M1 downloader;
- deterministic validation;
- deterministic +$5/-$3 labeling;
- ambiguity handling;
- data diagnostics;
- full 2016-2025 acquisition;
- SHA-256 dataset lock;
- chronological partitions;
- sealed 2025 FINAL_OOS reporting;
- initial timestamp-safe feature engine;
- initial baseline-analysis code;
- CI for deterministic checks and full-history workflows.

Current active branch:

research/exp001-foundation

At the time this continuity file was created, the latest feature/baseline CI was triggered from commit:

779b5f5bd42a16a56cdf7c873ef103e286f10528

## Immediate next work

1. inspect the feature/baseline CI;
2. confirm all yearly files matched the dataset lock;
3. inspect TRAIN / VALIDATION / DEVELOPMENT_TEST baseline evidence only;
4. keep 2025 FINAL_OOS sealed;
5. expand timestamp-safe expert-trader features only where the feature definition can be made objective and tested;
6. build simple models before complex models;
7. assess calibration and opportunity frequency;
8. freeze a candidate configuration before opening 2025.

## Continuity rule

Whenever a material project decision is made, update:

- research/DECISION_LOG.md
- this continuity file if the current-state summary changes
- the relevant technical specification

Do not rely on chat history as the sole record of a project decision.


## Automatic CI policy

Automatic push/PR CI is deterministic-only. Network-dependent public-data acquisition and historical integrity checks are manually dispatched from `.github/workflows/historical-data-integrity.yml`.

This separation prevents transient public-feed differences from making ordinary code/documentation commits appear broken.


## 2017 canonical snapshot update

The original 2017 Dukascopy snapshot became unavailable from the public feed. The current 2017 snapshot was reproduced consistently through repeated yearly downloads and independent monthly-chunk reconstruction.

The project therefore promoted the current snapshot to canonical:
- rows: 342,895
- SHA-256: 2efbfb87324fec2810f47833d2f9659a9c26da9037b5f639718058882dc40378

This supersedes the prior 2017 lock. The change is explicit and recorded in the dataset lock and decision log.


## 2020 canonical snapshot update

The project promoted the repeatedly reproduced current Dukascopy 2020 M1 BID snapshot to canonical:
- rows: 354,115
- SHA-256: 5616aafca39a2d3689911288c08fd5da8b2f3c3ea4a2bbdb8ca0cfbf690e9289

This supersedes the older 2020 lock of 355,495 rows / SHA-256 63892a47fec471a8bb4bbdd25ace162764fc56a1d6da02d458a535478fe6c6d3.


## Fresh-snapshot research policy

Full-history research no longer fails because a fresh Dukascopy year differs from an older byte-level lock.

Each full-history run now:
1. downloads the complete 2016-2025 snapshot once;
2. validates every file;
3. records a consolidated manifest;
4. audits all years against the previous canonical lock in one report;
5. continues research using the exact files from that acquisition.

The manifest for the run is the durable source-of-truth record for that run.


## Initial baseline milestone completed

Successful run: 36156744481

The first non-sealed baseline analysis completed over 2,860,357 eligible complete-feature rows.

Main findings:
- volatility is the dominant first-order determinant of $5 target attainability;
- Europe/US sessions are materially more favorable than Asia/LATE;
- directional momentum contains useful structure, while flat momentum is consistently weak;
- unresolved outcomes remain common, reinforcing NO TRADE as a core system behavior.

Next milestone:
Implement the frozen expert feature V2 specification in research/EXP-001_EXPERT_FEATURE_MILESTONE_V2.md, then evaluate simple models before any complex model.


## Expert feature V2 implementation

The timestamp-safe V2 price-context engine is implemented and deterministic CI is green.

It now includes richer volatility/attainability, M5/M15/H1/H4 directional context, rolling structure/location, candle conviction, impulse/pullback, session-transition, and trailing session-volatility features.

Before model fitting, the next required step is a full-history scale run on the fresh-snapshot pipeline to verify runtime and artifact generation across 2016-2024 without accessing FINAL_OOS for model selection.


## V2 workflow checkpointing

Run 36264651058 verified that V2 feature generation completes for every non-sealed year 2016-2024, but the GitHub runner shut down afterward during the baseline stage.

The historical workflow is now split:
- `full-history-prep`: acquisition, audit, labels, partitions, V2 features, then upload `exp001-v2-research-checkpoint`;
- `full-history-analysis`: downloads that checkpoint and performs non-sealed baseline/model analysis.

This prevents late runner interruptions from forcing expensive feature recomputation.


## Logistic V1 milestone

The first predictive model is preregistered in research/EXP-001_LOGISTIC_V1.md.

Implementation:
- script: scripts/logistic_exp001_v1.py
- memory-bounded chunked training/evaluation;
- TRAIN-only preprocessing and fitting;
- separate BUY and SELL models;
- VALIDATION and DEVELOPMENT_TEST evaluated chronologically;
- 2025 FINAL_OOS not accessed.

The workflow mode `v2-logistic-existing-checkpoint` reuses the preserved V2 checkpoint rather than rebuilding historical data or features.


## Logistic V1 results

Run 36268335102 completed successfully.

Key chronological evidence:
- BUY ROC-AUC: TRAIN 0.6826 / VALIDATION 0.6359 / DEVELOPMENT_TEST 0.6194.
- SELL ROC-AUC: TRAIN 0.5787 / VALIDATION 0.5816 / DEVELOPMENT_TEST 0.5549.
- High-score tails showed monotonic realized-success improvements for both BUY and SELL.
- Calibration drifted materially because later-period base rates increased.

Conclusion:
V2 features contain predictive information, especially for BUY, but the linear model is insufficient. Proceed to a frozen gradient-boosted-tree milestone while keeping 2025 sealed.

See research/EXP-001_LOGISTIC_V1_FINDINGS.md.


## GBT V1 results

Run 36307804733 completed successfully.

Chronological discrimination:
- BUY ROC-AUC: TRAIN 0.8439 / VALIDATION 0.7452 / DEVELOPMENT_TEST 0.7378.
- SELL ROC-AUC: TRAIN 0.8415 / VALIDATION 0.7407 / DEVELOPMENT_TEST 0.7452.

GBT V1 materially outperformed Logistic V1 for both directions.

Key feature-importance signal:
- 60m true-range mean was dominant;
- short-term and long-term realized volatility;
- minutes to session transition;
- compression/expansion and range-location features.

Raw GBT probabilities are compressed and never reached 0.60 in the evaluated partitions, so they are not yet suitable as direct confidence values.

Next milestone:
calibration and abstention/score-band research on VALIDATION and DEVELOPMENT_TEST only, with 2025 still sealed.

See research/EXP-001_GBT_V1_FINDINGS.md.


## Calibration and abstention V1 results

Run 36308557202 completed successfully.

BUY validation-derived raw-score bands transferred very strongly into DEVELOPMENT_TEST:
- top 10%: 30.96% -> 30.84%;
- top 5%: 33.42% -> 33.40%;
- top 2.5%: 34.54% -> 34.37%;
- top 1%: 36.38% -> 35.81%.

SELL bands also improved strongly with selectivity, but the VALIDATION extreme tail was not perfectly monotonic.

Platt calibration:
- modestly improved BUY Brier/log loss out-of-time;
- slightly worsened SELL out-of-time calibration.

Conclusion:
GBT ranking/selectivity is currently more reliable than interpreting the raw probability as literal confidence.

Next milestone:
freeze candidate abstention policies and test robustness across time blocks, volatility/session regimes, and overlapping-observation-aware uncertainty before any final OOS opening.

See research/EXP-001_CALIBRATION_ABSTENTION_V1_FINDINGS.md.


## Abstention robustness V1 results

Run 36310814632 completed successfully.

DEVELOPMENT_TEST overall:
- BUY top 10/5/2.5/1% success: 30.84% / 33.40% / 34.37% / 35.81%.
- SELL top 10/5/2.5/1% success: 32.77% / 34.58% / 35.72% / 36.97%.
- paired UTC-day bootstrap lift 95% CI lower bounds were >2.23 for every candidate policy.

All policies were above unconditional performance in both 2023 and 2024 and every populated quarter.

Coverage caveat:
The candidate policies fire almost entirely in the HIGH-volatility regime. LOW/MID-volatility and LATE-session robustness are not established because selected counts are zero or negligible there.

Next milestone:
pre-OOS candidate-policy freeze and specification audit before any 2025 access.

See research/EXP-001_ABSTENTION_ROBUSTNESS_V1_FINDINGS.md.


## Pre-OOS audit V1

The pre-OOS audit found two label-correctness issues before any FINAL_OOS opening:
- internal forward gaps could previously pass coverage if the final expected timestamp existed;
- same-partition year boundaries could lose valid next-year forward context.

Both mechanics are now repaired and deterministic tests were added.

A corrected non-sealed revalidation run rebuilds 2016-2024 only and reruns the frozen GBT/calibration/robustness stack. Run ID: 36311818762.

A separate economic blocker remains:
raw +$5/-$3 hit rates alone do not prove profitability because UNRESOLVED 60-minute expiry P&L and execution costs are not yet modeled.

Therefore:
- no final candidate is frozen yet;
- 2025 remains sealed;
- after corrected revalidation, freeze expiry/cost semantics and test non-sealed economics before any OOS opening.

See research/EXP-001_PRE_OOS_AUDIT_V1.md.


## Execution Economics V1

The next non-sealed milestone is preregistered in research/EXP-001_EXECUTION_ECONOMICS_V1.md.

It converts the corrected GBT score policies into sequential trade-level economics on DEVELOPMENT_TEST only.

Key rules:
- one global position at a time;
- simultaneous BUY/SELL signal => NO TRADE;
- SUCCESS +5 / FAILURE -3;
- AMBIGUOUS treated conservatively as -3;
- UNRESOLVED exits at exact 60-minute expiry close;
- all-in round-trip cost stress grid: 0.00 / 0.10 / 0.20 / 0.30 / 0.50 price units;
- top 10%, 5%, 2.5%, 1% policies only;
- 2025 remains sealed.

This is a BID-path economic proxy because historical Exness ASK/spread/slippage is not available in the admitted dataset.


## Execution Economics V1 findings

Run 36314782089 completed successfully.

No combined policy passed the frozen C20 advancement rule.

Top-1% combined:
- C0 mean +0.1765, PF 1.100, bootstrap 95% CI [0.0110, 0.3620];
- C10 mean +0.0765, PF 1.042, bootstrap CI crossed zero;
- C20 mean -0.0235, PF 0.988, 2024 negative, bootstrap CI crossed zero.

SELL-only top 1% was positive at C20, but no post-hoc direction-specific policy is being promoted.

Exness MT5 boundary probe:
- this demo server returned BID+ASK monthly samples from Jan-Sep 2026;
- sampled 2025-2023 months returned zero ticks;
- Exness is therefore reserved for 2026 broker-specific spread/shadow validation.

Next:
preregister and implement Dukascopy BID+ASK side-aware historical execution reconstruction before any FINAL_OOS opening.

See:
- research/EXP-001_EXECUTION_ECONOMICS_V1_FINDINGS.md
- research/EXNESS_MT5_TICK_BOUNDARY_FINDINGS.md

2025 remains sealed.


## Execution Economics V2 — side-aware historical reconstruction

Execution Economics V2 is preregistered and running.

Why:
- V1's BID-only proxy did not pass the combined C20 gate.
- Exness MT5 historical BID/ASK on the current demo server is useful from sampled Jan 2026 onward, not for 2023-2024 reconstruction.
- Dukascopy tick history exposes both BID and ASK.

Verified smoke:
- pinned dukascopy-node@1.50.0;
- XAUUSD tick day 2024-06-05 downloaded successfully;
- required schema timestamp / askPrice / bidPrice validated.

V2:
- keeps the corrected frozen GBT;
- derives operational cutoffs without future coverage conditioning;
- downloads only UTC tick days needed by top-10% candidate signals;
- evaluates BUY_ONLY / SELL_ONLY / COMBINED for top 10/5/2.5/1%;
- embeds historical Dukascopy spread through side-aware entry/exit quotes;
- applies extra F0/F05/F10/F20 friction stress;
- keeps FINAL_OOS 2025 sealed.

Current workflow run: 36316779171.

See research/EXP-001_EXECUTION_ECONOMICS_V2.md.


## Execution Economics V2 findings

Run 36316779171 completed successfully.

The side-aware historical execution screen failed.

Even at F0:
- top-1% COMBINED mean -0.3662, PF 0.8183, bootstrap 95% CI [-0.5563, -0.1817];
- top-1% BUY_ONLY mean -0.4961, PF 0.7602;
- top-1% SELL_ONLY mean -0.1828, PF 0.9066, bootstrap 95% CI [-0.3921, +0.0068].

All broader bands were also negative at F0 and worsened under F05/F10/F20.

Therefore:
- no current candidate advances;
- FINAL_OOS 2025 remains sealed;
- no Exness demo trading is justified from EXP-001;
- the next milestone must redesign labels/objective around executable BID/ASK economics and retrain under a new experiment version.

See research/EXP-001_EXECUTION_ECONOMICS_V2_FINDINGS.md.


## EXP-002 executable-side target

EXP-001 stopped before FINAL_OOS because side-aware BID/ASK execution economics were negative.

A new experiment is now active on:
research/exp002-executable-target-v1

Frozen specification:
research/EXP-002_PREREGISTRATION.md

Core change:
the target itself now uses executable-side mechanics.

BUY:
- entry next M1 ASK open;
- +5 / -3 evaluated using BID path.

SELL:
- entry next M1 BID open;
- +5 / -3 evaluated using ASK path.

The existing timestamp-safe market-context feature set is retained and augmented with causal spread features available by the decision close.

Initial workflow:
36320442383

Data:
paired Dukascopy BID/ASK M1 for 2016-2024 only.

2025 FINAL_OOS remains sealed.


## EXP-002 initial model findings

Run 36321788362 completed successfully.

DEVELOPMENT_TEST:
- BUY ROC-AUC 0.7392, PR-AUC 0.2315;
- SELL ROC-AUC 0.7482, PR-AUC 0.2454.

Fixed VALIDATION-derived top-1% success:
- BUY 29.05%;
- SELL 33.07%.

The executable-side target preserves substantial predictive ranking signal.

AMBIGUOUS rows are rare relative to complete-path rows, so later tick adjudication should be a small correction rather than the main source of the result.

Next milestone:
sequential EXP-002 execution economics on 2023-2024 using frozen score bands and executable-side P&L semantics.

2025 FINAL_OOS remains sealed.

See research/EXP-002_INITIAL_MODEL_FINDINGS.md.


## EXP-002 sequential economics findings

Run 36324128764 completed successfully.

No preregistered policy passed the F10 advancement gate.

Least-negative:
SELL_ONLY top 1% at F10:
- trades 1,348;
- mean net -0.3252;
- PF 0.8360;
- 2023 -0.0895;
- 2024 -0.3967;
- bootstrap 95% CI [-0.5159, -0.1290].

Even F0 remained negative overall.

Therefore:
- no EXP-002 V1 policy advances;
- 2025 remains sealed;
- no Exness demo trading is justified from this milestone;
- next work should diagnose why strong classifier ranking does not translate into positive sequential expectancy using only 2016-2024.

See research/EXP-002_EXECUTION_ECONOMICS_V1_FINDINGS.md.


## EXP-002 economic failure diagnosis

After EXP-002 sequential economics failed, the project moved to a diagnostic-only milestone before any EXP-003 design.

Frozen specification:
research/EXP-002_ECONOMIC_FAILURE_DIAGNOSIS_V1.md

Questions:
- are losses dominated by FAILURE or UNRESOLVED expiry P&L?
- does score improve economic value monotonically?
- is the failure concentrated by year/quarter, session, volatility, or spread?
- do high scores cluster into repeated observations of the same episode?
- how much sequential position filtering suppresses raw signals?
- which term of the empirical EV identity causes negative expectancy?

No new model or threshold will be selected from this diagnosis.

Current workflow:
36328166429

2025 FINAL_OOS remains sealed.


## EXP-003 economic-value model V1

Active branch:
research/exp003-economic-value-v1

Frozen specification:
research/EXP-003_PREREGISTRATION.md

Motivation:
EXP-002 preserved strong SUCCESS-probability ranking but failed sequential economics because high-score regions still contained too many -3 adverse-barrier failures. UNRESOLVED expiry P&L was not the primary drag, and raw qualifying observations were strongly clustered.

EXP-003 V1 therefore:
- keeps the frozen EXP-002 feature vector;
- trains separate BUY and SELL three-class models for SUCCESS / FAILURE / UNRESOLVED;
- trains separate unresolved-expiry-P&L regressors;
- computes explicit expected executable value;
- uses frozen EV_F10 abstention thresholds 0 / 0.25 / 0.50 / 0.75;
- evaluates one global position at a time;
- requires positive F10 economics in both 2023 and 2024 plus a positive UTC-day bootstrap lower bound before any policy can advance.

2025 FINAL_OOS remains sealed.

No EXP-003 model result has been produced yet.


## EXP-003 threshold economics findings

Run 36337595939 completed successfully.

No preregistered EXP-003 V1 policy passed.

T0 F10 means:
- BUY_ONLY -0.4151;
- SELL_ONLY -0.4040;
- COMBINED -0.4142.

T25 remained negative overall; T50/T75 also remained negative and many variants failed minimum trade-count gates.

Therefore:
- no pre-OOS candidate freeze;
- no 2025 access;
- no Exness demo/live advancement;
- next work is diagnosis of why predicted EV remains misaligned with realized executable P&L.

See research/EXP-003_THRESHOLD_ECONOMICS_V1_FINDINGS.md.


## EXP-003 EV miscalibration diagnosis

After EXP-003 threshold economics failed, the project moved to a frozen diagnostic milestone before any EXP-004 design.

Specification:
research/EXP-003_EV_MISCALIBRATION_DIAGNOSIS_V1.md

The diagnosis decomposes predicted EV error into:
- class-probability error;
- unresolved-expiry-P&L regression error;
- year/quarter calibration drift;
- error by realized outcome;
- sequential-trade calibration;
- feature-distribution shift and TRAIN-support extrapolation.

No new model or threshold is being selected.

Current workflow:
36348182305

2025 FINAL_OOS remains sealed.


## EXP-003 EV miscalibration diagnosis findings

Run 36348182305 completed successfully.

The dominant EXP-003 failure is now identified:

- positive-EV tails systematically overpredict SUCCESS and underpredict FAILURE;
- this tail miscalibration worsens at higher predicted EV;
- unresolved-P&L regression is not the primary source of the optimism;
- 2024 has strong volatility/spread/attainability distribution shift relative to TRAIN;
- positive-EV rows are frequently outside TRAIN feature support, especially BUY;
- the same EV optimism persists at sequential executed-trade level.

Therefore a future EXP-004 must address temporal calibration / distribution shift / out-of-support uncertainty rather than merely retuning EV thresholds.

See:
research/EXP-003_EV_MISCALIBRATION_DIAGNOSIS_V1_FINDINGS.md

2025 FINAL_OOS remains sealed.


## EXP-004 shift-aware calibrated EV V1

Active branch:
research/exp004-shift-aware-calibrated-ev-v1

Frozen specification:
research/EXP-004_PREREGISTRATION.md

Purpose:
test whether EXP-003's EV miscalibration can be corrected without changing market features or executable target.

Changes relative to EXP-003:
- expanding-window out-of-time TRAIN probability calibration;
- one frozen TRAIN-support abstention gate.

Arms:
- A raw EXP-003 EV benchmark;
- B calibrated EV;
- C calibrated EV plus support gate.

Only B/C may advance.

No EXP-004 result has been produced yet.

2025 FINAL_OOS remains sealed.


## EXP-004 findings

Run 36394304605 completed successfully.

No calibrated-EV or calibrated-EV-plus-support policy passed.

Calibration improved aggregate probability fit, especially SELL, but did not produce positive sequential economics.

ARM B T0 F10:
- BUY_ONLY -0.4237;
- SELL_ONLY -0.4339;
- COMBINED -0.4413.

ARM C T0 F10:
- BUY_ONLY -0.3922;
- SELL_ONLY -0.4379;
- COMBINED -0.4204.

The support gate rejected about 16.9% of DEVELOPMENT_TEST rows, but economics remained negative.

Higher calibrated-EV thresholds became extremely sparse and did not satisfy minimum trade-count, temporal-coverage, bootstrap, or concentration gates.

Therefore:
- no candidate freeze;
- no 2025 access;
- no Exness demo/live advancement;
- next experiment must materially change representation or target rather than retune calibration/support thresholds.

See research/EXP-004_FINDINGS.md.

2025 FINAL_OOS remains sealed.


## EXP-005 downside-first direct economic model V1

Active branch:
research/exp005-downside-first-competing-risk-v1

Frozen specification:
research/EXP-005_PREREGISTRATION.md

Purpose:
test a materially different target representation after EXP-004 failed.

EXP-005:
- predicts realized executable gross P&L directly;
- separately predicts adverse-barrier FAILURE within <=5 minutes;
- freezes VALIDATION-derived EARLY_FAILURE risk gates Q50/Q25/Q10;
- evaluates DIRECT_ONLY and three downside-gated arms;
- reuses the same frozen market feature vector and execution semantics.

No EXP-005 empirical result exists yet.

2025 FINAL_OOS remains sealed.


## EXP-005 findings

Corrected run 36445233132 completed successfully.

No EXP-005 policy passed.

Key result:
- direct gross-P&L regression had very weak predictive correlation;
- <=5-minute EARLY_FAILURE classification was materially stronger (DEV ROC-AUC about 0.81-0.84);
- risk gating could remove observed rapid-failure trades, but usable trade counts collapsed;
- ungated direct-score economics remained negative;
- 2024 remained a major failure point.

Therefore:
- no candidate freeze;
- no 2025 access;
- no Exness demo/live advancement;
- next experiment must materially improve the market-state representation rather than reuse the same frozen 48 features.

See research/EXP-005_FINDINGS.md.

2025 FINAL_OOS remains sealed.


## EXP-006 causal path-state representation V1

Active branch:
research/exp006-causal-path-state-v1

Frozen specification:
research/EXP-006_PREREGISTRATION.md

EXP-006 is a representation A/B test:
- BASE48 benchmark;
- PATH84 = BASE48 + 36 causal path-state features.

The model targets, hyperparameters, <=5-minute EARLY_FAILURE definition, validation risk gates, score thresholds, sequential execution rules, and advancement gates remain unchanged from EXP-005.

Only PATH84 policies may advance.

No EXP-006 empirical result exists yet.

2025 FINAL_OOS remains sealed.


## EXP-006 findings

Run 36467825948 completed successfully.

No PATH84 policy passed.

Representation deltas were essentially zero:
- BUY direct-P&L Pearson delta -0.0068;
- SELL +0.0044;
- EARLY_FAILURE ROC-AUC changes approximately zero.

PATH84 T0 F10:
- BUY_ONLY -0.5212;
- SELL_ONLY -0.5074;
- COMBINED -0.5161.

Thus richer hand-crafted causal price-path features did not solve the trade-quality problem and generally worsened economics.

Therefore:
- no candidate freeze;
- no 2025 access;
- no Exness demo/live advancement;
- next experiment must change a more fundamental dimension than additional tree-input path features.

See research/EXP-006_FINDINGS.md.

2025 FINAL_OOS remains sealed.


## EXP-007 causal sequence model V1

Active branch:
research/exp007-causal-sequence-v1

Frozen specification:
research/EXP-007_PREREGISTRATION.md

EXP-007 moves beyond hand-crafted tree inputs and tests a small causal temporal CNN over the trailing 60 synchronized M1 bars plus BASE48 static context.

Targets remain:
- direct executable gross P&L;
- <=5-minute EARLY_FAILURE.

Economic policies and advancement gates remain unchanged.

No EXP-007 empirical result exists yet.

2025 FINAL_OOS remains sealed.


## EXP-007 findings

Run 36485293055 completed successfully.

No sequence-model policy passed.

Key result:
- BUY direct-P&L Pearson -0.0269 and catastrophic positive-tail miscalibration;
- SELL direct-P&L Pearson +0.0667 but still economically negative;
- EARLY_FAILURE remains highly rankable (ROC-AUC ~0.88 for both directions);
- T0 BUY_ONLY mean NET_F10 -3.0200;
- T0 SELL_ONLY -0.2913;
- T0 COMBINED -2.3099;
- downside-gated arms are tiny and negative.

Therefore:
- no candidate freeze;
- no 2025 access;
- no Exness demo/live advancement;
- next experiment should change target formulation or add separately preregistered exogenous information rather than tune the current CNN.

See research/EXP-007_FINDINGS.md.

2025 FINAL_OOS remains sealed.


## EXP-008 competing-hazard target-before-adverse V1

Active branch:
research/exp008-competing-hazard-v1

Frozen specification:
research/EXP-008_PREREGISTRATION.md

EXP-008 changes the target formulation while returning to exact BASE48 inputs.

It models nine competing time-to-event classes:
- four SUCCESS timing bins;
- four FAILURE timing bins;
- U_60 unresolved.

It uses strictly out-of-time TRAIN probability calibration and derives executable EV from the calibrated competing-hazard probabilities.

Validation-derived early-failure gates Q50/Q25/Q10 are preregistered.

No EXP-008 empirical result exists yet.

2025 FINAL_OOS remains sealed.


## EXP-008 findings

Run 36616276558 completed successfully.

No policy passed.

Aggregate calibration improved:
- BUY T0 raw rows realized approximately -0.025 NET_F10 versus predicted +0.059 EV;
- SELL aggregate EV calibration gap was about +0.021.

But sequential T0 economics remained negative:
- BUY_ONLY -0.4043;
- SELL_ONLY -0.3412;
- COMBINED -0.3650.

A T25 SELL subset averaged +1.229 NET_F10 but had only 10 trades and failed bootstrap, sample-size, annual-count, and concentration requirements.

Therefore:
- no candidate freeze;
- no 2025 access;
- no Exness demo/live advancement;
- next experiment should add separately preregistered timestamp-safe exogenous context.

See research/EXP-008_FINDINGS.md.

2025 FINAL_OOS remains sealed.


## Root-cause reset — event-driven dynamic trade management V1

Active branch:
research/root-reset-event-driven-v1

Frozen design:
research/ROOT_CAUSE_RESET_V1.md

Purpose:
correct the trading formulation rather than continue tuning models.

Changes:
- score only event-driven continuation candidates;
- model probability that executable MFE_60 reaches at least $5;
- derive initial stop from structure + 15-minute volatility;
- reject trades whose dynamic stop makes minimum $5 reward/risk < 1.5;
- use a downside-risk veto;
- compare:
  - M0 HOLD_TO_5
  - M1 BE_AT_3
  - M2 TAKE_3

VALIDATION 2022 selects one opportunity threshold once.
DEVELOPMENT_TEST 2023-2024 is accessed only if validation qualification succeeds.

2025 FINAL_OOS remains sealed.


## Root-reset V1 result

Run 36629144070: SUCCESS.

Outcome:
- no opportunity threshold selected;
- zero qualifying validation trades at 0.50/0.60/0.70/0.80;
- DEVELOPMENT_TEST 2023-2024 was not accessed;
- FINAL_OOS 2025 was not accessed.

However, OPPORTUNITY_5 ranking showed meaningful validation signal:
- BUY ROC-AUC 0.7728 / PR-AUC 0.3421;
- SELL ROC-AUC 0.7592 / PR-AUC 0.3316.

The likely failure is the intersection of:
- overly high absolute opportunity-probability thresholds;
- dynamic-stop reward/risk admissibility;
- an extremely rare EARLY_DAMAGE veto.

Next step:
VALIDATION-ONLY gate-overlap diagnosis. Do not alter V1 post hoc.

See research/ROOT_CAUSE_RESET_V1_FINDINGS.md.


## Root-reset V1 gate-overlap result

Corrected diagnosis run 36687708188: SUCCESS.

No DEVELOPMENT_TEST or FINAL_OOS access occurred.

Core result:
- opportunity ranking is useful;
- stop admissibility is the dominant bottleneck;
- stop-admissible validation events have only ~5.2% $5-opportunity rate;
- stop-rejected events have ~20% $5-opportunity rate;
- top opportunity decile has ~40-42% $5 attainment but virtually zero stop admissibility.

Thus the fixed $3.333 maximum stop, derived from a fixed $5 / 1.5R geometry, selects quiet low-opportunity states and rejects the high-volatility states where $5 moves actually occur.

Next:
Root-Reset V2 should jointly model attainable favorable excursion and adverse excursion / structural invalidation, then derive dynamic reward/risk.

See research/ROOT_RESET_V1_GATE_OVERLAP_FINDINGS.md.

2023-2024 and 2025 remain untouched.


## Root-Reset V2 — joint excursion dynamic reward/risk

Active branch:
research/root-reset-v2-joint-excursion

Frozen specification:
research/ROOT_RESET_V2_PREREGISTRATION.md

Core change:
replace the fixed stop ceiling with jointly predicted favorable/adverse excursion quantiles.

Models:
- MFE60 q50/q70/q80;
- MAE60 q50/q70/q80.

Eligibility:
- MFE q70 >= $5;
- central adverse estimate not greater than central favorable estimate;
- dynamic TARGET/STOP >= 1.20.

Policies:
- G50-H / G50-B3
- G70-H / G70-B3
- G80-H / G80-B3

2022 validation selects at most one policy.
2023-2024 are accessed only if one qualifies.
2025 remains sealed.


## Root-Reset V2 result

Run 36696884026: SUCCESS.

Outcome:
- no validation policy qualified;
- DEVELOPMENT_TEST 2023-2024 was not accessed;
- FINAL_OOS 2025 was not accessed.

Excursion models showed moderate signal:
- MFE q70 Pearson ~0.39 BUY / ~0.41 SELL;
- MAE q70 Pearson ~0.40 BUY / ~0.46 SELL.

But raw quantile geometry was too optimistic:
- G70 mean target ~$7.4 vs realized median MFE ~$3.5;
- G80 mean target ~$7.9 vs realized median MFE ~$4.1.

G50-H was mildly positive (+0.124 NET_F10, PF 1.059) but only 17 trades and therefore inadmissible.

Next:
validation-only excursion calibration diagnosis; no 2023-2024 or 2025 access.

See research/ROOT_RESET_V2_FINDINGS.md.


## V2 excursion calibration result

Run 36700831693: SUCCESS.

No DEVELOPMENT_TEST or FINAL_OOS access occurred.

Key result:
- MFE q70 needs substantial shrinkage (~0.54-0.61);
- MFE q80 needs even more (~0.39-0.45);
- MAE q50 is reasonably calibrated and better than structural invalidation as a risk anchor;
- after calibration, median reward/risk is still below 1 for the continuation-event population.

Therefore:
- do not create V3 by shrinkage alone;
- continuation event entry quality is the remaining bottleneck;
- next work must change setup family and/or introduce new timestamp-safe information before candidate generation.

See research/ROOT_RESET_V2_EXCURSION_CALIBRATION_FINDINGS.md.

2023-2024 and 2025 remain untouched.


## Root-Reset V3 — structural setup family screening

Active branch:
research/root-reset-v3-setup-screening

Frozen specification:
research/ROOT_RESET_V3_SETUP_SCREENING.md

TRAIN-only screening of:
- breakout-retest continuation;
- sweep-reclaim reversal;
- impulse-pullback continuation.

Data:
2016-2021 only.

No validation, development-test, or FINAL_OOS access is allowed.

No model fitting occurs in this milestone.

The output selects at most one setup family for a future separately frozen 2022 validation experiment.

2022-2025 remain untouched.


## Root-Reset V3 screening result

Run 36711334369: SUCCESS.

No family selected.

TRAIN-only 2016-2021:
- A_BREAKOUT_RETEST: 0/6 positive yearly path-edge years;
- B_SWEEP_RECLAIM: 0/6;
- C_IMPULSE_PULLBACK: 0/6.

All families have median MFE60 below median MAE60 and fail the frozen stability requirements.

Therefore:
- no 2022 validation access;
- no more price-only pattern invention;
- next work must add genuinely new timestamp-safe causal context before entry generation.

See research/ROOT_RESET_V3_SETUP_SCREENING_FINDINGS.md.

2022-2025 remain untouched.


## Newly admitted research source — Badar repository

Owner explicitly admitted:

alisufyan-ai7/unpack-human-trading-strategies-claude

for use in this project.

Use its provenance boundary:
- outside derived/ = source layer documenting what Badar said/showed;
- derived/ = Claude interpretation only.

The repo may now support a separately preregistered Badar-Core setup experiment.

No other private source has been admitted by this decision.

See research/ADMITTED_SOURCE_BADAR_TRADING_REPO.md.


## Root-Reset V4 — Badar-Core

Active branch:
research/root-reset-v4-badar-core

Frozen preregistration:
research/ROOT_RESET_V4_BADAR_CORE_PREREGISTRATION.md

Implementation:
scripts/root_reset_v4_badar_core.py

Purpose:
test whether a source-grounded Badar-style multi-stage entry process materially improves the TRAIN entry population relative to the failed generic price-only setup families.

Key sequence:
HTF context -> session liquidity -> H1 FVG -> M15 sweep/reclaim -> M5 MSS -> displacement FVG -> retracement entry -> structural liquidity target.

Two stop hypotheses are measured without optimization:
- S-STRUCT
- S-MICRO

Data:
2016-2021 only.

2022-2025 remain untouched unless a future separately preregistered validation is justified by the frozen TRAIN gates.


## Root-Reset V4 result

Run 36768684222: SUCCESS.

Result:
- zero filled trades;
- no economic evaluation possible;
- no stop hypothesis passed;
- no 2022 validation authorized.

Primary funnel bottlenecks:
- 135 M15 confirmations -> 24 M5 two-close MSS;
- 24 -> 16 MSS + displacement FVG;
- 16 -> 3 structural targets >= $5;
- 3 limit orders -> 0 fills.

Interpretation:
the V4 deterministic translation is too restrictive before entry and should not be treated as proof against Badar's source method.

Next step:
TRAIN-only translation diagnosis before any V5.

2022-2025 remain untouched.

See research/ROOT_RESET_V4_BADAR_CORE_FINDINGS.md.


## Active work — V4 translation diagnosis

Current branch:
research/root-reset-v4-badar-core

V4 main result:
- historical run 36768684222 succeeded;
- zero filled trades;
- no economic conclusion about Badar's method;
- 2022-2025 untouched.

Active next step:
TRAIN-only translation diagnosis.

Frozen specification:
research/ROOT_RESET_V4_TRANSLATION_DIAGNOSIS.md

Implementation:
scripts/diagnose_root_reset_v4_translation.py

The diagnosis keeps V4 frozen through:
HTF context -> session liquidity -> H1 FVG -> M15 sweep -> M15 close-back.

It then measures:
- one-close M5 vs two-close M5 MSS;
- M3/M1 one-close confirmation recovery;
- direct-close entry vs midpoint-FVG fill;
- PDH/PDL and H1/H4 swing structural-target availability;
- the exact V4 gate responsible for excluding the most source-plausible cases.

No profitability policy is selected in this diagnosis.

Research-source boundary:
- primary project repo: alisufyan-ai7/xauusd-5dollar-prediction
- explicitly admitted Badar research repo: alisufyan-ai7/unpack-human-trading-strategies-claude
- in the Badar repo, everything outside derived/ is source evidence; derived/ is Claude interpretation only.

Clean-room boundary remains binding:
do not use account memory, other chats, other projects, or any other private GitHub repository.

2022, 2023-2024, and 2025 remain sealed/unopened for this stage.

New chats should reconstruct project state from this file, research/DECISION_LOG.md, the active preregistration/diagnosis files, and current GitHub Actions state.


## V4 translation diagnosis result

Accepted run:
36779728544 — SUCCESS.

The run is TRAIN-only (2016-2021) and includes a same-snapshot frozen-V4 reference guard plus compact data SHA-256 identity.

The frozen V4 reference reproduced the original funnel exactly:
- 1,508 NY dates;
- 627 M15 liquidity sweeps;
- 364 active-H1-FVG overlaps;
- 135 M15 close-back confirmations;
- 24 M5 two-close MSS;
- 16 MSS + displacement FVG;
- 3 session targets >= $5;
- 3 midpoint orders;
- 0 fills.

Translation diagnosis:
- C1 one-close M5 = 33;
- C2 V4 two-close M5 = 24;
- C3 one-close M3 = 47;
- C4 one-close M1 = 83;
- C1 recovers 9 cases C2 misses;
- M3 and/or M1 recover 63 cases C2 misses;
- C2 direct entries = 24;
- C2 displacement-FVG cases = 16;
- C2 midpoint fills within 30m = 9;
- C2 direct entries without midpoint fill = 15/24;
- C2 cases with session targets < $5 but broader previous-day/H1/H4 target >= $5 = 8/24.

Conclusion:
V4's zero fills were caused by cumulative translation restriction before economic evaluation. The largest absolute population loss is the two-close M5 confirmation gate, with FVG-midpoint entry and session-only target translation adding further restriction.

No profitability policy was selected.
No 2022-2025 data were accessed.

See:
research/ROOT_RESET_V4_TRANSLATION_DIAGNOSIS_FINDINGS.md

## Active next step — source-grounded V5 specification

Do not choose C1/C3/C4, direct entry, or a target family simply because it produced the largest diagnostic population.

Before another economic experiment:
1. use only the admitted Badar source layer outside derived/;
2. resolve the deterministic confirmation, entry, target and stop translation from source evidence;
3. preregister one V5 translation on TRAIN;
4. only then run a new 2016-2021 experiment.

2022, 2023-2024 and 2025 remain sealed.


## Root-Reset V5 — Badar A+ source-fidelity

Active branch:
research/root-reset-v5-badar-source-fidelity

Frozen preregistration:
research/ROOT_RESET_V5_BADAR_SOURCE_FIDELITY_PREREGISTRATION.md

Decision record:
D-062

Purpose:
translate the admitted Badar S01/A+ setup more faithfully after V4's pre-entry coverage failure, without selecting rules by diagnostic candidate count.

Frozen upstream through M15 close-back remains V4-identical.

Frozen V5 execution after M15 close-back:
- one-close MSS on M5/M3;
- first causal valid MSS + clean displacement FVG wins, with M5 tie priority;
- no M1 MSS;
- FVG remains mandatory;
- resting entry at FVG proximal/start edge, not midpoint;
- structural stop beyond the sweep only;
- final target from causally known previous-day/H1/H4 liquidity;
- require target distance >= $5 and target/stop RR >= 3;
- no direct-close entry, no OB alternative, no micro stop, no partials/BE/trailing.

Data:
2016-2021 synchronized BID/ASK M1 only.

2022 validation, 2023-2024 development test, and 2025 FINAL_OOS remain sealed.

Next implementation step:
create scripts/root_reset_v5_badar_source_fidelity.py and a manual historical-data-integrity workflow mode, then run TRAIN once under the frozen specification and record the funnel/economic result.


## Root-Reset V5 result

Accepted historical run:
36783834169 — SUCCESS.

Scope:
2016-2021 TRAIN only.

Key funnel:
- 1,546 NY dates;
- 656 M15 liquidity sweeps;
- 369 active-H1-FVG overlaps;
- 137 M15 close-back confirmations;
- 39 source-valid M5/M3 MSS + FVG triggers;
- 21 targets >= $5;
- 9 target/stop RR >= 3;
- 9 proximal-edge orders;
- 6 fills.

Advancement:
- entry population pass: FALSE;
- structural stop pass: FALSE;
- future 2022 validation preregistration: NOT AUTHORIZED.

Important formulation finding:
the frozen >=180 filled-trade gate could not be reached because the retained V4 upstream sampler itself generated only 137 M15 close-back confirmations over all six TRAIN years.

Therefore do not lower the gate or tune downstream rules post hoc.

See:
research/ROOT_RESET_V5_BADAR_SOURCE_FIDELITY_FINDINGS.md

## Active next step — TRAIN-only source-location coverage audit

Decision record:
D-063

Purpose:
measure whether the mandatory V4/V5 conjunction of session-liquidity sweep + active H1 FVG is substantially narrower than Badar's admitted source-layer concept of trading from a marked liquidity/location zone.

The audit is diagnostic only and should compare source-supported location families without selecting a profitability winner.

2022, 2023-2024 and 2025 remain sealed.


## Intelligent-system information audit

Decision record:
D-064

Audit:
research/INTELLIGENT_SYSTEM_INFORMATION_AUDIT.md

Result:
the project is not yet information-comparable to Badar's observed decision environment.

Available now:
- XAUUSD M1 BID/ASK OHLCV from Dukascopy;
- spread and executable-side semantics;
- multi-timeframe price-derived state;
- session/timing state;
- causal PDH/PDL, swing and FVG building blocks;
- 2026 Exness read-only tick data for later forward broker calibration.

Important unused information already present:
- Dukascopy M1 volume.

Important missing channels:
- DXY intraday;
- US-yield intraday;
- historical macro calendar and release surprise state;
- unified source-faithful liquidity/location representation;
- broader fundamental regime;
- explicit scenario/confidence state;
- trade/account/risk state.

Active next step:
preregister and build Information Parity Layer V1 before another profitability model or strategy experiment.

Then run information-channel ablations and a Badar decision-recognition benchmark. Only if richer information materially improves the representation should one new economic policy experiment be frozen.

2022-2025 remain unopened for this new milestone.


## Information Parity V1 finite roadmap frozen

Decision record:
D-065

Roadmap:
research/INFORMATION_PARITY_V1_ROADMAP.md

The exact next program is now frozen before implementation:
1. information-source feasibility audit;
2. build Information Parity Layer V1;
3. Badar decision-recognition benchmark;
4. information-channel ablation;
5. one intelligent economic experiment.

No new external-data acquisition or profitability modeling has started under this roadmap yet.

Immediate next step:
create the dedicated Information Parity V1 branch and preregister Stage 1.

2022-2025 remain sealed.


## Information Parity V1 — Stage 1 active

Active branch:
research/information-parity-v1

Decision record:
D-066

Frozen preregistration:
research/INFORMATION_PARITY_V1_STAGE1_SOURCE_FEASIBILITY_PREREGISTRATION.md

Current task:
audit source feasibility for DXY/USD, US yields/rates, macro-event schedules, macro release values/surprises, existing Dukascopy M1 volume semantics, and targeted tick microstructure.

Stage 1 selects sources only on data integrity/causality/reproducibility criteria. It does not train a model or inspect profitability.

2022-2025 XAUUSD evaluation periods remain sealed.


## Information Parity V1 — Stage 1 complete

Decision record:
D-067

Findings:
research/INFORMATION_PARITY_V1_STAGE1_SOURCE_FEASIBILITY_FINDINGS.md

Accepted final probe:
- run 36986414645 — SUCCESS
- artifact digest sha256:27ff2ed0f4d03a6392a479208ad9d2a80bd467d45fe5a2b2d46113aa3d7f8821
- 2022-2025 XAUUSD remained untouched.

Final source verdicts:
- C1 synthetic DXY: ADMITTED WITH LIMITATION;
- C2 rates/yields: DEFERRED;
- C3 scheduled macro calendar: ADMITTED WITH LIMITATION;
- C4 macro surprise/consensus: DEFERRED;
- C5 M1 provider volume: ADMITTED WITH LIMITATION;
- C6 targeted tick microstructure: ADMITTED WITH LIMITATION.

Stage 2 source set is now frozen around XAUUSD M1 BID/ASK + spread + provider volume + multi-timeframe/structural state + synthetic DXY + first-party scheduled macro calendar, with targeted tick microstructure optional and trade/risk state separate.

Active next step:
preregister the Stage 2 Information Parity Layer V1 schema and timestamp-alignment contract before full TRAIN acquisition/integration.

Do not train a profitability model yet.


## Information Parity V1 — Stage 2 active

Active branch:
research/information-parity-v1-stage2

Decision record:
D-068

Frozen preregistration:
research/INFORMATION_PARITY_V1_STAGE2_SCHEMA_PREREGISTRATION.md

Stage 2 purpose:
build a causal, reproducible 2016-2021 Information Parity Layer V1. No predictive model or profitability evaluation is authorized in this stage.

Key decision-time rule:
M1 timestamp is bar start; decision time is bar start + 60 seconds; every joined field must have availability time <= decision time.

Stage 2 source set:
- synchronized XAUUSD BID/ASK M1 OHLC;
- spread and provider-volume state;
- causal multi-timeframe/structural/session state;
- SYNTHETIC_DXY_DUKASCOPY_BID;
- first-party scheduled macro calendar;
- targeted tick data only if explicitly required;
- separate trade/risk-state schema.

Deferred/excluded:
US 10Y/rates, macro surprises/consensus, global order flow, default full-history ticks.

Active next step:
implement acquisition/normalization + leakage/integrity checks under the frozen Stage 2 contract and run one 2016-2021 same-snapshot build.

2022-2025 remain sealed.


## Stage 2 macro-calendar implementation frozen

Decision record:
D-069

Specification:
research/INFORMATION_PARITY_V1_STAGE2_MACRO_ADDENDUM.md

Implementation now targets first-party scheduled timestamps for:
CPI, NFP, JOLTS, FOMC, Initial Claims and national GDP.

ISM Manufacturing/Services historical dates are deferred from V1 rather than synthesized from a generic business-day rule because exact historical first-party holiday exceptions are not sufficiently reproducible from the public archive.

Scripts added:
- scripts/acquire_macro_schedule_stage2.py
- scripts/validate_information_parity_stage2.py

No macro outcomes/surprises are allowed.
No model training is allowed yet.
2022-2025 XAUUSD remain sealed.


## Stage 2 macro transport fallback

Decision record:
D-070

Second smoke run 37011477397 confirmed that BLS blocks GitHub Actions with HTTP 403 even though the official historical schedule is publicly available. The project will stop retrying that transport path.

Stage 2 now permits versioned normalized BLS schedule snapshots derived from official BLS historical pages, with source URL/provenance on every row. This is a transport/reproducibility fallback, not a new data source and not a raw provider-data commit.

The immediate smoke fix is limited to the already-frozen 2016 smoke year. Equivalent 2017-2021 snapshots must be verified before the full TRAIN build.

BEA GDP discovery will also switch to the official national-GDP archive with created_1=All and release-year filtering.

No economic outcomes or sealed XAUUSD periods are involved.


## Stage 2 smoke accepted

Decision record:
D-071

Findings:
research/INFORMATION_PARITY_V1_STAGE2_SMOKE_FINDINGS.md

Accepted run:
- 37192128583 — SUCCESS
- artifact digest sha256:cc46e7a2d7e3875533440e11c73846de5ed92e27b6182aff62a4a7f743d34d82

End-to-end integrity passed for the fixed 2016 smoke window. Macro coverage was complete for the admitted six core families, synthetic DXY was available on all smoke decision rows, and no sealed XAUUSD periods were accessed.

Active next step:
prepare/verify 2017-2021 normalized BLS schedule snapshots under D-070, then implement and run the single full 2016-2021 same-snapshot Stage 2 workflow after foundation CI is green.

No model training yet.


## Stage 2 engineering preflight gate active

Decision record:
D-072

Isolated development branch:
research/information-parity-v1-stage2-preflight

Preflight specification:
research/INFORMATION_PARITY_V1_STAGE2_PREFLIGHT.md

Frozen environment:
research/INFORMATION_PARITY_V1_STAGE2_ENVIRONMENT.md
requirements/information-parity-stage2.lock.txt

Offline command:
bash scripts/run_information_parity_stage2_preflight.sh

Policy change:
GitHub Actions is no longer the first integration-test environment for Stage 2. Ordinary preflight development stays on the isolated branch with no automatic CI. CI is triggered only once the deterministic offline suite is ready and passing.

The accepted real-data smoke remains run 37192128583.
The full 2016-2021 provider-data build is still blocked until this preflight gate and 2017-2021 BLS schedule verification are complete.

No model training yet. 2022-2025 remain sealed.


## Stage 2 preflight run 1 diagnosed

Run 37196172995 failed before deterministic tests because the static repository-contract checker itself had a Python newline-escaping syntax error.

This is documented in:
research/INFORMATION_PARITY_V1_STAGE2_PREFLIGHT_RUN1_FINDINGS.md

Decision record:
D-073

Corrective changes:
- checker newline handling fixed;
- Python compile gate moved before checker/test execution;
- corrected checker and preflight test syntax-compiled off-CI;
- shell runner passed bash syntax validation off-CI.

One more deterministic preflight CI is now justified solely to execute the complete suite under the exact frozen runtime. Provider market-data workflows remain blocked.


## Stage 2 preflight found real D1/W1 bug

Decision record:
D-074

Findings:
research/INFORMATION_PARITY_V1_STAGE2_PREFLIGHT_RUN2_FINDINGS.md

Run 37227754869 passed the frozen environment/repository/foundation gates but exposed a real pandas index-alignment bug in D1 grouping.

The bug is fixed and deterministic regressions now require exact D1/W1 output.

Important correction:
accepted smoke run 37192128583 remains valid for M1-H4/DXY/macro and other exercised paths, but its D1/W1/previous-day path is invalidated and must be rerun after preflight acceptance.

Current policy:
- no automatic preflight trigger exists;
- no new CI yet;
- no provider-data run yet;
- review remaining deterministic paths for similar alignment assumptions first.

2022-2025 remain sealed. No model training.


## Local Stage 2 deterministic logic gate passed

Decision record:
D-075

Evidence:
research/INFORMATION_PARITY_V1_STAGE2_LOCAL_PREFLIGHT_EVIDENCE.md

A real local deterministic execution passed after the D-074 D1 fix:
- D1 28;
- W1 4;
- integrity PASS;
- negative leakage injection rejected;
- no sealed-period access.

This is explicitly a local logic gate, not exact pinned-runtime acceptance. The local environment differs from the frozen CI environment and some large source files were semantically materialized rather than byte-identical due container network restrictions.

Current next step:
finish exact-source reconciliation/static alignment review before deciding whether one manual pinned-runtime preflight CI is justified.

No provider-data run. No model training. 2022-2025 remain sealed.


## Stage 2 off-CI review V2 passed

Decision record:
D-076

Documents:
- research/INFORMATION_PARITY_V1_STAGE2_PREFLIGHT_STATIC_REVIEW_ADDENDUM.md
- research/INFORMATION_PARITY_V1_STAGE2_LOCAL_REVIEW_V2.md

Four integrity gaps were fixed off-CI: macro simultaneous-event multiplicity, required structural distances, D1/W1 + previous-day validator recomputation, and duplicate/off-grid raw M1 guards.

The corrected local deterministic suite passes.

One exact-runtime deterministic-preflight CI is now authorized. Provider-data acquisition is still blocked until that confirmation succeeds.


## Exact-runtime Stage 2 preflight accepted

Decision record:
D-077

Accepted run:
- 37231660721 — SUCCESS
- head 1a008ac8ff70335ee7ef8793a81d55c6909db8bb

All deterministic gates passed under the frozen Python/pandas/Node environment.

Active next step:
run one corrected bounded 2016 real-data smoke on the accepted implementation because D-074 materially changed D1/W1/previous-day behavior after the earlier smoke.

Full TRAIN and model work remain blocked. 2022-2025 remain sealed.


## Corrected Stage 2 provider smoke accepted

Decision record:
D-078

Findings:
research/INFORMATION_PARITY_V1_STAGE2_CORRECTED_SMOKE_FINDINGS.md

Accepted run 37231837219 succeeded and produced non-empty corrected D1/W1:
- D1 5;
- W1 1;
with hierarchy, previous-day, structural-distance, DXY, macro and sealed-period checks all passing and no warnings.

Active next step:
implement and off-CI review the full 2016-2021 Stage 2 TRAIN orchestration. Do not trigger the expensive full build until that orchestration passes its own local/static gate.

No model training. 2022-2025 remain sealed.


## Full TRAIN continuity requirement discovered before build

Decision record:
D-079

Addendum:
research/INFORMATION_PARITY_V1_STAGE2_FULL_TRAIN_CONTINUITY_ADDENDUM.md

The full 2016-2021 Information Parity build must compute causal state continuously across year boundaries. Annual independent builds would incorrectly reset causally available context every January 1.

Current implementation task:
create continuous market/DXY concatenation, continuous Stage 2 state construction, post-state annual partitioning, boundary integrity checks and compact full-TRAIN manifests. Keep CI/provider full build blocked until off-CI review passes.


## BLS 2016-2021 full-TRAIN input gate complete

Decision record:
D-080

All six normalized BLS fallback snapshots are now present and passed off-CI static verification, including deterministic event-ID reconstruction and exact source/timezone checks.

Active blocker before the expensive full provider run:
finish and pass the deterministic full-TRAIN orchestration integration gate. CI remains manual-only and has not been triggered for this work.
