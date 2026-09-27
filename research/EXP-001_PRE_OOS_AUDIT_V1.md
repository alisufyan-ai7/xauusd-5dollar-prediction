# EXP-001 Pre-OOS Specification Audit V1

Status: IN PROGRESS — FINAL_OOS GATE NOT READY

## Scope

This audit is performed before any 2025 FINAL_OOS opening.

## Correctness findings

### A-001 — Internal forward-label gaps

Finding:
The original label engine considered coverage complete when the final expected M1 timestamp existed, even if an internal minute was missing.

Risk:
A row could be treated as having a complete 60-minute outcome horizon despite missing internal price path information.

Disposition:
FIXED in scripts/label_exp001.py.

New rule:
coverage_complete requires exactly 60 consecutive expected M1 timestamps for the default 60-minute horizon.

Deterministic internal-gap test added.

### A-002 — Same-partition year-boundary forward context

Finding:
Historical years were labeled independently, so eligible decisions near Dec 31 could lose next-year forward bars even when both years belonged to the same frozen partition.

Disposition:
FIXED for non-sealed revalidation.

Next-year context is used only for year transitions that stay inside the same frozen partition:
- 2016 -> 2017
- 2017 -> 2018
- 2018 -> 2019
- 2019 -> 2020
- 2020 -> 2021
- 2023 -> 2024

No context is crossed at:
- 2021 -> 2022
- 2022 -> 2023
- 2024 -> 2025

This preserves partition-horizon isolation and avoids using 2025.

### A-003 — Feature year-start context

Current V2 yearly feature files conservatively mark early-year rows incomplete until 240 minutes of same-file history exist.

This loses some otherwise usable rows at year starts but does not introduce future leakage.

Disposition:
Accepted for the current corrected revalidation because it is conservative and matches the prior model-development implementation.

Before eventual 2025 production/shadow scoring, the operational feature pipeline must explicitly carry prior available history across the year boundary so a live system is not artificially blind during the first 240 minutes of a calendar year.

### A-004 — Multi-timeframe semantics

The current V2 multi-timeframe directional context uses deterministic rolling M1-window measures rather than fully separate closed OHLC M5/M15/H1/H4 bars.

Disposition:
Accepted as the frozen V2 feature definition for EXP-001. It must not be renamed or interpreted as literal closed-timeframe OHLC structure in reporting.

Changing this definition would require a new experiment version.

## Economic interpretation finding

The +$5 / -$3 two-barrier break-even success rate is 37.5% before transaction costs if every non-success is treated as a full -$3 loss.

The strongest DEVELOPMENT_TEST top-1% success rates observed before this audit were below 37.5%.

However UNRESOLVED rows are not necessarily -$3 losses; their realized 60-minute exit P&L has not yet been modeled.

Therefore predictive hit-rate evidence alone is insufficient to claim trading profitability.

Before FINAL_OOS:
- freeze expiry-exit semantics for UNRESOLVED trades;
- incorporate spread, slippage, and other relevant execution costs;
- evaluate deterministic trade-level economic outcomes on non-sealed data only.

## Corrected revalidation requirement

The frozen GBT/calibration/abstention stack must be rerun on freshly acquired 2016-2024 data using the corrected label semantics.

Required artifacts:
- acquisition manifest;
- corrected partition summary;
- corrected GBT V1 report;
- corrected calibration/abstention V1 report;
- corrected robustness V1 report.

No 2025 input is permitted.

## Candidate-policy freeze

DEFERRED.

A single operating candidate will be frozen only if:
1. corrected non-sealed revalidation preserves the core ranking edge;
2. execution-economics semantics are frozen and tested;
3. all remaining implementation semantics are documented;
4. candidate specification is hashed before any FINAL_OOS opening.

## Current gate decision

FINAL_OOS 2025: DO NOT OPEN.
