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
