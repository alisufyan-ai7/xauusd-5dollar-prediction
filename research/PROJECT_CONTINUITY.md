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
