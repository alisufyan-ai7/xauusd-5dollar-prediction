# Information Parity V1 — Stage 2 Preflight Static-Review Addendum

Status: **FROZEN BEFORE EXACT-RUNTIME PREFLIGHT CONFIRMATION**

Parent:
- `research/INFORMATION_PARITY_V1_STAGE2_SCHEMA_PREREGISTRATION.md`
- `research/INFORMATION_PARITY_V1_STAGE2_IMPLEMENTATION_ADDENDUM.md`

Purpose:

Record implementation clarifications and integrity hardening discovered during the off-CI static review after D-074. No profitability, future XAUUSD outcome, or sealed-period information was used.

## A9 — Signed structural distance convention

Where Stage 2 requires distance from current XAUUSD BID close, the physical field uses:

`signed_distance = structural_level - current_bid_close`

Therefore:
- positive = level is above current BID close;
- negative = level is below current BID close;
- zero = current BID close equals the level.

This convention now applies to:
- last confirmed swing high/low on M5/M15/H1/H4;
- previous-day high/low/open/close;
- Asia high/low;
- London high/low.

FVG signed distance retains its already-frozen interval-distance convention.

## A10 — Simultaneous macro-event counts

The parent schema requires:
- count of admitted events in the prior 120 minutes;
- count of admitted events in the next 120 minutes.

When two or more admitted events share one timestamp:
- categorical family state remains one deterministic sorted multi-label;
- **count fields count admitted event records, not distinct timestamps**.

Example:
simultaneous CPI + NFP contributes 2 to the event count.

This corrects an implementation bug found during static review.

## A11 — Canonical hierarchy integrity

The Stage 2 validator must independently cross-check:
- canonical D1 against H1;
- canonical W1 against D1.

The validator recomputes the expected hierarchy from child bars and requires matching:
- row count;
- bar start;
- availability time;
- source count;
- OHLC;
- provider-volume sum.

This turns the D1/W1 path from a warning-only surface into an executable integrity contract.

## A12 — Previous-day as-of integrity

The validator independently recomputes previous-day state from canonical D1 using only:
`available_time_ms <= decision_time_ms`.

It verifies:
- high;
- low;
- open;
- close;
- signed distance from current BID close.

## A13 — Raw M1 timestamp integrity

Stage 2 synchronization and synthetic-DXY constituent loading now reject:
- duplicate timestamps;
- timestamps not aligned to the 60,000 ms M1 grid.

They must not silently overwrite duplicate provider rows.

## A14 — CI authorization boundary

The deterministic local logic gate passed after these corrections.

One exact-runtime deterministic-preflight CI is now justified solely to confirm:
- exact branch bytes;
- Python 3.12.14;
- pandas 3.0.6;
- Node 22.23.3;
- the frozen dependency lock.

No provider-data acquisition is authorized by this addendum.
