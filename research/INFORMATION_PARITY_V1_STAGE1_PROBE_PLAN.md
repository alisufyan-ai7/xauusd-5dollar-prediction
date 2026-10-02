# Information Parity V1 — Stage 1 Fixed Probe Plan

Status: **FROZEN BEFORE EMPIRICAL SOURCE PROBES**

Parent:
- `research/INFORMATION_PARITY_V1_STAGE1_SOURCE_FEASIBILITY_PREREGISTRATION.md`

## Purpose

Freeze the tiny, outcome-independent samples used to verify source coverage, timestamp continuity, schema, volume behavior, and tick practicality.

These samples are **not** selected from XAUUSD outcomes and must not be used for trading P&L or feature selection.

## M1 anchor days

Use the first Monday of February in three fixed TRAIN-era anchor years:

- **2016-02-01**
- **2019-02-04**
- **2021-02-01**

Rationale:
- early / middle / late TRAIN coverage;
- ordinary weekdays;
- deterministic calendar rule rather than market-outcome selection.

For each anchor day download one UTC day of M1 BID data for:

- `dollaridxusd` — Dukascopy US Dollar Index candidate;
- `ustbondtrusd` — Dukascopy US T-Bond candidate/proxy.

For XAUUSD volume-side semantics, download one UTC day of:

- `xauusd` BID M1 with volume;
- `xauusd` ASK M1 with volume.

## Tick anchor windows

Use two fixed one-hour UTC windows:

- **2016-02-01 14:00:00–15:00:00 UTC**
- **2021-02-01 14:00:00–15:00:00 UTC**

Rationale:
- early and late TRAIN;
- active US-session hours useful for practical quote-density/file-size testing;
- fixed before any tick result is observed.

Download XAUUSD tick data only for these windows.

## Required probe outputs

For every M1 file:

- SHA-256;
- file bytes;
- row count;
- first/last timestamp;
- exact M1-grid check;
- duplicate/non-monotonic check;
- gap count and largest gap;
- OHLC sanity;
- volume field presence;
- finite/nonnegative volume check;
- zero-volume share;
- volume quantiles.

For XAUUSD BID/ASK pairs:

- timestamp overlap/alignment;
- spread summary;
- BID/ASK volume equality share;
- BID/ASK volume correlation when defined;
- side-specific volume quantiles.

For tick windows:

- schema;
- SHA-256;
- file bytes;
- row count;
- first/last timestamp;
- monotonicity;
- spread summary;
- quote-update density;
- presence and behavior of askVolume/bidVolume when available.

## Acceptance meaning

A successful probe establishes only technical availability and observed sample behavior.

It does **not** by itself resolve:
- whether Dukascopy's US Dollar Index is economically identical to ICE DXY;
- whether `ustbondtrusd` is an acceptable 10Y-rate proxy;
- the economic meaning of volume fields;
- predictive value.

Those require Stage 1 findings and source-semantics evidence.

## Raw-data policy

Raw probe files:
- must not be committed;
- may exist ephemerally in CI;
- only compact summaries, hashes, and manifests may be retained as artifacts or committed findings.

## Sealed data

No 2022-2025 XAUUSD data are permitted in these probes.
