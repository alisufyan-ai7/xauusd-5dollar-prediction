# EXP-001 Historical Acquisition Range

Status: FROZEN FOR ACQUISITION

## Historical window

Primary historical research window:

- start: 2016-01-01 00:00 UTC
- end: 2026-01-01 00:00 UTC
- included calendar years: 2016 through 2025
- timeframe: M1
- price side: BID
- instrument: XAU/USD
- source: admitted free public Dukascopy historical feed

The 2026 calendar year is intentionally excluded from historical model development so it can remain available for later forward/shadow comparison and operational validation.

## Why this range

A ten-year window is large enough to span materially different volatility and macro regimes while remaining practical to acquire, validate, hash, and reproduce in yearly chunks.

This is an acquisition decision only. It does not define train/validation/final-OOS partitions. Those partitions will be frozen separately after full acquisition and integrity diagnostics are complete.

## Chunking

Data must be acquired in independent yearly chunks:

- 2016
- 2017
- 2018
- 2019
- 2020
- 2021
- 2022
- 2023
- 2024
- 2025

Each chunk must be:

1. downloaded independently;
2. validated independently;
3. labeled independently only after validation;
4. hashed with SHA-256;
5. recorded in a machine-readable manifest.

A failed year must not be silently skipped.

## Data retention in Git

Raw and derived datasets remain outside Git history.

Only code, specifications, manifests, compact diagnostics, and small deterministic fixtures may be version-controlled.
