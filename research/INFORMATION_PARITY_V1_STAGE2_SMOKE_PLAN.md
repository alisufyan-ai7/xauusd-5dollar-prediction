# Information Parity V1 — Stage 2 Bounded Smoke Plan

Status: **FROZEN BEFORE LIVE SMOKE BUILD**

Parent:
`research/INFORMATION_PARITY_V1_STAGE2_SCHEMA_PREREGISTRATION.md`

Purpose:
Verify that the Stage 2 acquisition, normalization, macro-calendar, DXY, causal state, and integrity pipeline can execute end-to-end before launching the full 2016-2021 same-snapshot build.

No profitability or future XAUUSD outcomes are examined.

## Fixed XAUUSD / FX window

Use the first full Monday-Friday trading week of February 2016:

- from: **2016-02-01 00:00 UTC**
- to: **2016-02-06 00:00 UTC**

This date window is fixed before smoke results and was not selected from XAUUSD outcomes.

Acquire:
- XAUUSD BID M1
- XAUUSD ASK M1
- EURUSD BID M1
- USDJPY BID M1
- GBPUSD BID M1
- USDCAD BID M1
- USDSEK BID M1
- USDCHF BID M1

## Macro scope

Acquire/normalize the **2016** Stage 2 macro schedule only.

Reason:
the macro parser needs enough annual history to verify family counts and historical source coverage; one week alone cannot test the calendar completeness contract.

Allowed families are frozen by D-069.

## Smoke operations

1. download and validate fixed M1 source files;
2. synchronize XAUUSD BID/ASK;
3. build synthetic DXY;
4. acquire/normalize 2016 macro schedule;
5. build the partial-2016 Stage 2 information layer;
6. run the Stage 2 leakage/integrity validator;
7. write compact source/hash/build manifests;
8. upload compact evidence only.

## Required pass criteria

The smoke passes only if:

- all market downloads validate;
- XAUUSD synchronization succeeds;
- synthetic DXY has nonzero synchronized observations;
- macro normalization executes and records family counts/errors;
- Stage 2 annual builder succeeds;
- integrity validator status is PASS;
- no forbidden future/P&L/macro-outcome fields exist;
- no 2022-2025 XAUUSD access occurs.

Macro source coverage may be reported INCOMPLETE if a first-party live source/parser fails; that does not become a silent pass. Such a result blocks the full Stage 2 run until fixed or separately re-decided.

## Artifact policy

Do not upload or commit raw provider files.

Upload only:
- raw/normalized manifests and SHA identities;
- DXY coverage report;
- macro coverage report;
- annual build report;
- integrity report;
- compact summary hashes.

## After smoke

If smoke passes and macro year coverage is complete:
- clean temporary trigger;
- add/finalize the full 2016-2021 same-snapshot workflow;
- run once.

If smoke fails:
- diagnose the concrete implementation/source failure;
- do not alter the frozen information contract based on economic results.
