# EXP-001 Full-History Labeling Stage

Status: IMPLEMENTED / FINAL_OOS SEALED

## Purpose

Generate deterministic EXP-001 labels and frozen chronological partition annotations for the admitted 2016-2025 XAU/USD M1 history.

## Sealed final-OOS rule

2025 is the frozen FINAL_OOS partition.

The pipeline may create deterministic 2025 label files and hashes so that the dataset can be reproduced, but research summaries must not expose 2025 BUY/SELL success, failure, unresolved, ambiguity, calibration, or performance distributions before the final-OOS gate is intentionally opened.

Compact summaries therefore report only:

- 2025 row count;
- partition-boundary eligibility counts;
- file hash;
- explicit SEALED status.

## Current limitation

Yearly raw files are labeled independently. Decisions within the final hour of a yearly file can have incomplete future coverage even when the following year belongs to the same research partition.

Those rows remain auditable through `coverage_complete` and must not be admitted to model fitting/evaluation until a later continuity pass either:

1. provides the necessary next-year overlap; or
2. excludes incomplete-coverage observations.

The 60-minute partition-boundary purge remains mandatory regardless.
