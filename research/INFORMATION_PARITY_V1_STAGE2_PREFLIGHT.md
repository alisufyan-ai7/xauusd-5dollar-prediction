# Information Parity V1 — Stage 2 Offline Preflight Gate

Status: **REQUIRED BEFORE ANY NEW STAGE 2 CI / PROVIDER RUN**

## Why this exists

The accepted Stage 2 smoke eventually passed, but too many earlier GitHub Actions runs were used to discover ordinary integration defects:

- provider-site transport behavior;
- parser assumptions;
- pandas API mistakes;
- datetime storage-resolution assumptions;
- empty-table serialization;
- test-import-path setup.

Those failures did not expose a scientific flaw in Information Parity V1, but they did expose an engineering-process flaw:

> GitHub Actions was being used as the first integration test environment.

That is no longer allowed for Stage 2.

## Development branch

Preflight work is isolated on:

`research/information-parity-v1-stage2-preflight`

This branch is intentionally not the head of PR #15 and is not listed in the project's automatic foundation-check push branches.

Therefore ordinary commits to this branch do not trigger CI.

## Frozen runtime

See:

`research/INFORMATION_PARITY_V1_STAGE2_ENVIRONMENT.md`

Canonical Python lock:

`requirements/information-parity-stage2.lock.txt`

Accepted-smoke runtime:

- CPython 3.12.14
- Node v22.23.3
- npm 10.9.9
- dukascopy-node 1.50.0

## Offline runner

Command:

`bash scripts/run_information_parity_stage2_preflight.sh`

The preflight must require no network and no provider data.

## What the deterministic preflight tests

### 1. BID/ASK synchronization

Synthetic XAUUSD M1 includes:
- one ASK-only missing minute;
- one BID-only missing minute;
- one minute absent from both sides.

Required behavior:
- one-sided rows are reconstructed only under the frozen conservative rule;
- reconstructed-side volume is zero;
- the both-sides-missing timestamp is not invented;
- spread remains nonnegative.

### 2. Higher-timeframe aggregation

The synthetic dataset spans four continuous weeks and must produce:
- M3;
- M5;
- M15;
- M30;
- H1;
- H4;
- nonempty D1;
- nonempty W1.

This specifically catches:
- timestamp-unit mistakes;
- ordering mistakes;
- daily/weekly aggregation regressions;
- schema loss on completed tables.

### 3. Empty canonical tables

A separate fixture deliberately produces:
- zero D1;
- zero W1.

Header-only CSV.GZ round-trip must succeed.

This protects the edge case that previously failed after the smoke builder succeeded.

### 4. Synthetic DXY

Six deterministic M1 FX constituent series are generated.

One constituent has a six-minute hole.

Required behavior:
- DXY only exists on exact six-way common timestamps;
- backward decision-row alignment never uses future DXY;
- available DXY age is <=5 minutes;
- at least one decision row becomes unavailable after the >5m gap.

### 5. Session / DST behavior

The synthetic period spans:
- U.S. daylight-saving transition;
- U.K. daylight-saving transition.

Assertions verify the 08:00 local New York and London session boundaries shift correctly in UTC.

No fixed UTC offset is accepted.

### 6. Swing causality

A deterministic five-bar fixture creates a known swing high.

The swing must become visible only after the second right-hand confirmation bar closes.

### 7. FVG causality

A deterministic bar fixture creates a bullish FVG and later invalidates it.

Assertions verify:
- exact creation availability time;
- invalidation occurs strictly after creation;
- boundaries are deterministic.

### 8. Macro schedule state

Synthetic schedule-only events include simultaneous CPI and NFP.

Required behavior:
- simultaneous families are deterministically sorted as a multi-label;
- minutes-to / minutes-since are causal;
- no actual/forecast/previous/surprise field is introduced.

### 9. Trade/risk state

The end-to-end builder must leave the Stage 2 trade/risk template neutral:
- FLAT;
- no trades;
- zero deployed risk;
- null entry/stop/target.

### 10. Positive integrity path

The complete synthetic layer must pass:
`scripts/validate_information_parity_stage2.py`.

### 11. Negative leakage path

The test deliberately injects a `future_return` column into a copy of the decision index.

The integrity validator must reject it.

A validator that accepts this corrupted fixture fails the preflight.

## CI policy

CI is now a confirmation gate, not an exploratory debugger.

Do not trigger a Stage 2 CI run merely because code was edited.

Sequence:

1. implement on the isolated preflight branch;
2. run the offline preflight under the frozen environment;
3. fix all deterministic failures locally/offline;
4. only after the offline suite passes, run **one intentional Stage 2 preflight CI** under the same pinned environment;
5. if that CI fails, classify whether the difference is:
   - CI/runtime/environment-specific;
   - an external-provider boundary;
   - or a genuine missed deterministic test;
6. add a deterministic regression before retrying;
7. do not repeatedly trigger provider-data smoke/full runs while debugging local logic.

## Provider-data runs

The offline preflight does not replace:
- the accepted real-data smoke;
- the future full 2016-2021 same-snapshot build.

It prevents preventable code defects from consuming those runs.

Before the full TRAIN run:
- offline preflight must pass;
- one intentional pinned-environment CI confirmation must pass;
- 2017-2021 BLS reference snapshots must be verified;
- the full workflow must be reviewed before triggering.

## Scientific boundary

The preflight contains:
- no profitability logic;
- no labels;
- no future XAUUSD outcomes;
- no 2022-2025 XAUUSD data;
- no model fitting.

It is purely an engineering integrity gate.
