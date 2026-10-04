# Information Parity V1 — Stage 2 Smoke Findings

Status: **ACCEPTED FOR M1-H4 / DXY / MACRO PATHS; D1/W1 PATH INVALIDATED BY D-074**

Accepted workflow run:
- workflow: `information-parity-stage2`
- run: **37192128583**
- head: `273b93cc882ac954fcd6bc21b28155ef4ab5aa0f`
- conclusion: SUCCESS
- artifact: `information-parity-stage2-smoke`
- artifact id: `11299477067`
- artifact digest: `sha256:cc46e7a2d7e3875533440e11c73846de5ed92e27b6182aff62a4a7f743d34d82`

Scope:
- fixed smoke market window: 2016-02-01 through 2016-02-06 UTC
- macro schedule: full 2016
- 2022-2025 XAUUSD accessed: none

## End-to-end result

The smoke completed all frozen operations:

1. XAUUSD BID/ASK acquisition and validation;
2. synchronized executable-side M1 construction;
3. six-constituent synthetic DXY construction;
4. first-party/verified-reference macro schedule normalization;
5. causal multi-timeframe/structural/session information-layer build;
6. decision-index and neutral trade/risk-state construction;
7. leakage/integrity validation;
8. compact hash/manifests.

## Market-state coverage

XAUUSD synchronized M1 rows:
- 6,840

Synthetic DXY:
- 7,008 common six-constituent observations
- common share of constituent-union timestamps: 98.9831%
- decision-row DXY availability share: 100.0%

Decision rows:
- 6,840

Feature-ready market share:
- 82.5292%

BID/ASK reconstruction in smoke:
- BID flat-fill rows: 0
- ASK flat-fill rows: 0

## Canonical timeframe rows

- M3: 2,280
- M5: 1,368
- M15: 456
- M30: 228
- H1: 114
- H4: 25
- D1: 0
- W1: 0

**Correction (D-074):** these zero D1/W1 counts were initially interpreted as expected for the short smoke window. The deterministic preflight later proved that interpretation was wrong. The Stage 2 D1 builder assigned a RangeIndex-backed timestamp Series into a DatetimeIndex-backed frame, causing pandas label alignment to produce all-NaT `source_day` values. Therefore the smoke did **not** validate D1/W1 construction or previous-day state.

The smoke remains valid evidence for the successfully exercised M1 through H4, DXY, macro, synchronization, structural/session, decision-index, and neutral trade-state paths. A corrected real-data smoke is required after the deterministic preflight is fully green.

## Macro schedule

Normalized 2016 rows:
- 108

Counts:
- Initial Claims: 52
- CPI: 12
- FOMC: 8
- GDP: 12
- JOLTS: 12
- NFP / Employment Situation: 12

Macro schedule availability:
- 100%

Macro errors:
- none

ISM Manufacturing and Services remain explicitly deferred under D-069.

## Integrity result

`integrity-2016-smoke.json` status:
- PASS

Passed checks include:
- M1 decision-time relation;
- M1 TRAIN-year scope;
- nonnegative spread;
- all non-empty canonical timeframe availability ordering;
- structural state alignment;
- structural causal creation/confirmation timing;
- DXY backward as-of alignment and <=5m staleness;
- macro outcome-field exclusion;
- macro timezone alignment;
- macro-state alignment;
- neutral trade/risk-state template;
- sealed-period assertion.

Warnings:
- `xauusd_d1:empty`
- `xauusd_w1:empty`

**Correction (D-074):** these warnings were not benign smoke-window effects; they exposed a latent D1 grouping bug that the original validator treated only as warnings. D1/W1 and previous-day coverage from run 37192128583 must not be used as validated evidence.

## Scientific interpretation

The smoke validates **implementation feasibility and causal integrity for the exercised M1-H4/DXY/macro paths only**. D1/W1 and previous-day state are excluded from that claim under D-074.

It does not:
- establish predictive value;
- establish profitability;
- select a trading policy;
- authorize Stage 3;
- authorize opening 2022.

## Next required work before full TRAIN build

1. verify and commit normalized official-BLS schedule reference snapshots for 2017-2021, using the same D-070 provenance rule as the accepted 2016 snapshot;
2. ensure Stage 2 foundation CI is green after the empty-table regression test import-path fix;
3. replace the placeholder blocked `full-train` job with the frozen 2016-2021 same-snapshot acquisition/build/integrity workflow;
4. remove the temporary smoke trigger;
5. run the full TRAIN workflow once.

No model training begins before the full Stage 2 layer passes.
