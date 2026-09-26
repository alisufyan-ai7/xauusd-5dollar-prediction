# EXP-001 Chronological Partition Policy

Status: FROZEN BEFORE MODEL DEVELOPMENT

## Historical research window

The admitted historical acquisition covers 2016-01-01 through 2025-12-31.

## Frozen partitions

- TRAIN: 2016-01-01 00:00 UTC through 2021-12-31 23:59:59 UTC
- VALIDATION: 2022-01-01 00:00 UTC through 2022-12-31 23:59:59 UTC
- DEVELOPMENT_TEST: 2023-01-01 00:00 UTC through 2024-12-31 23:59:59 UTC
- FINAL_OOS: 2025-01-01 00:00 UTC through 2025-12-31 23:59:59 UTC

The 2025 FINAL_OOS partition is sealed from feature selection, model selection, threshold tuning, and hyperparameter tuning.

The 2026 calendar year remains outside historical model development and is reserved for later forward/shadow comparison and operational validation.

## Barrier-horizon boundary rule

EXP-001 labels use a 60-minute future horizon.

A decision sample is eligible for a partition only if its complete label horizon remains inside that same partition.

Therefore decisions whose 60-minute horizon would cross a partition end are marked boundary-ineligible and excluded from modeling/evaluation for that partition.

This prevents a TRAIN, VALIDATION, or DEVELOPMENT_TEST sample from using future outcome information belonging to a later partition.

## Feature-history rule

Features may use only information available at or before the decision timestamp.

At a partition start, historical lookback may use earlier observations, because those observations would have been available in real time. Future observations are never permitted.

## Governance

1. FINAL_OOS 2025 is not to be inspected for model-performance selection decisions.
2. A failed final OOS result must not be repaired by tuning on 2025.
3. Any future experiment that changes these partitions must be registered as a new experiment/version rather than silently modifying EXP-001.
