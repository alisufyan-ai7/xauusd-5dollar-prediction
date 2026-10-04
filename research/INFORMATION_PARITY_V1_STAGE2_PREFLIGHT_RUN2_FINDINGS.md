# Information Parity V1 — Stage 2 Preflight Run 2 Findings

Status: **DETERMINISTIC SUITE FOUND A REAL D1 AGGREGATION BUG**

Run:
- workflow: `information-parity-stage2-preflight`
- run: **37227754869**
- head: `3d732cf2bf3b22dc1422dd1c85b16197bef04452`
- conclusion: FAILURE

## What passed

Before the failing assertion, the run successfully passed:

- static repository-contract check;
- frozen environment check;
- CPython 3.12.14;
- Node 22.23.3 / npm 10.9.9;
- exact pinned Python dependency set;
- foundation tests.

The deterministic end-to-end preflight then built far enough to inspect canonical D1/W1 output.

## Exact failure

The deterministic fixture spans exactly four continuous UTC weeks.

Expected:
- D1 = 28 canonical daily bars;
- W1 = 4 canonical weekly bars.

Observed:
- D1 count was below the required threshold;
- first failing assertion:
  `assert len(d1) >= 20`.

## Root cause

The problem was in `build_d1`.

The code did:

`idx = pd.to_datetime(h1["available_time_ms"], ...)`

then:

`tmp.index = idx`

then assigned:

`tmp["source_day"] = (idx - ...).dt.floor("D")`.

Here `idx` was a Series carrying a RangeIndex, while `tmp` had already been changed to a DatetimeIndex.

Pandas therefore aligned the assigned Series by index labels instead of by position.

Result:
- `source_day` became NaT;
- D1 grouping produced no valid daily groups;
- W1 also became empty;
- previous-day state could not be populated.

## Consequence for the accepted real-data smoke

Run 37192128583 remains valid evidence for:
- XAUUSD M1 synchronization;
- M3/M5/M15/M30/H1/H4 construction;
- DXY construction/alignment;
- macro schedule/state;
- structural/session state;
- decision index;
- neutral trade/risk state;
- the integrity checks those paths exercised.

However, its D1/W1 result is **invalidated**.

The previous interpretation that D1/W1 were empty merely because the smoke window was short was wrong.

The smoke therefore did not validate:
- D1 construction;
- W1 construction;
- previous-day state.

The smoke findings file has been corrected accordingly.

## Fix

`build_d1` now converts availability times to a DatetimeIndex and derives `source_day` directly from `tmp.index`:

`tmp["source_day"] = (tmp.index - 1ns).floor("D")`

This avoids label-alignment semantics entirely.

Regression coverage added:
- 48 deterministic H1 bars must produce exactly 2 D1 bars;
- each D1 must report source_count=24;
- the four-week end-to-end fixture must produce exactly 28 D1 and 4 W1 bars.

## Off-CI verification performed

The corrected D1 grouping was independently reproduced outside GitHub Actions with a 48-H1 fixture:
- D1 rows = 2;
- source counts = [24, 24].

A four-week deterministic M1 simulation with one both-sides-missing minute produced:
- H1 = 671;
- D1 = 28;
- W1 = 4;
- one D1 with 23 H1 bars;
- 27 D1 with 24 H1 bars.

This confirms the root cause and expected corrected behavior independently of CI.

## CI policy after this finding

Do **not** trigger another CI immediately.

The temporary preflight push trigger has been removed and the workflow restored to manual-only.

Before any next CI confirmation:
- review the remaining deterministic suite for similar pandas label-alignment assumptions;
- finish off-CI logical validation of the corrected D1/W1 path;
- only then perform one intentional manual preflight confirmation.

No provider-data workflow is authorized yet.

2022-2025 XAUUSD remain sealed.
