# Information Parity V1 — Stage 3 Source Timestamp Audit V1 Findings

Status: **INTERMEDIATE SOURCE-ONLY AUDIT — NOT A STAGE 3 PASS/FAIL**

Parent:
- `research/INFORMATION_PARITY_V1_STAGE3_PROTOCOL_PREREGISTRATION.md`
- D-088 chronology blocker
- D-089 frozen Stage 3 protocol

No market-price lookup was used.

## Pinned Badar source

Repository:
`alisufyan-ai7/unpack-human-trading-strategies-claude`

Pinned commit:
`2df3d588c4b6d82761df2ee0c6f6639e82ce3414`

Pinned teacher table:
- path: `dataset/live_trades.csv`
- blob: `ea620cb44937f276be2e65ae7da25ae9503be655`
- rows: 119
- streams: 43
- epoch: 2026 only

Everything inside the Badar repository's `derived/` directory remained excluded.

## Durable audit artifacts

Teacher timestamp audit:
`research/reference/information-parity-v1/stage3-teacher-timestamp-audit-v1.csv`

Git blob:
`fdfe6f2be6fd7633daaf0be69d5b738cdda0e315`

Stream observation-window metadata:
`research/reference/information-parity-v1/stage3-stream-observation-windows-v1.csv`

Git blob:
`6c1ee6b6450e688bc267c309e410b95472c53e07`

## V1 metadata-only timestamp resolver

A teacher row is marked `EXACT_M1` in this first audit only when one of these source-only conditions is met:

1. source `chart_time` names one explicit minute with no approximation/range marker; or
2. the source explicitly records an exact event/fill minute, such as a confirmed NFP release-candle fill; or
3. an exact relative stream timestamp/range plus an exact source chart-clock anchor independently resolve to one minute and corroborate the displayed chart minute.

The automatic corroboration path does not use relative timestamps labelled as:
- approximate;
- pre-stream/before-stream;
- limit placement/fill ranges;
- box/panel/display times whose relation to the actual entry is ambiguous.

Rows that do not meet those rules remain `INTERVAL_ONLY`.

This V1 resolver intentionally prefers false negatives to invented precision.

## Current timestamp result

Before any authorship/live-execution filtering:

- `EXACT_M1` candidate rows: **35**
- distinct source dates represented: **16**
- LONG: **14**
- SHORT: **21**

Frozen D-089 minimum teacher-evidence gate:

- >=40 positive minutes;
- >=20 dates;
- >=15 LONG;
- >=15 SHORT.

Therefore the **metadata-only resolver does not yet meet the frozen gate**.

This is not a final Stage 3 failure because D-089 permits source-frame/note adjudication. Several approximate source-table rows have frame/contact-sheet evidence that may independently resolve a unique entry minute without using market-price data or relaxing the exact-M1 rule.

## Stream observation-window metadata

All 43 streams now have a durable source-window record containing:
- source date;
- note-header session/window text;
- source chart-clock anchor text;
- anchor quality/status;
- pinned source commit.

These are deliberately marked:

`COARSE_HEADER_WINDOW_ONLY_NOT_CONTROL_AUTHORIZED`

They are not yet valid minute-by-minute negative-control windows because a stream can temporarily show:
- DXY or another instrument;
- a browser/news page;
- a student's screen;
- off-chart discussion.

A later source-only visibility audit must identify reliably observed XAUUSD minutes before controls are built.

## Important non-result

Do **not** interpret 35 as the final number of eligible Badar trades.

This audit has not yet completed:
- source-frame timestamp promotions;
- Badar-authorship adjudication;
- live/real execution adjudication;
- multiple-entry same-minute collapse;
- exact XAUUSD-visibility control windows.

The current number is only the strict metadata-level exact-timestamp count.

## Targeted next source-only review

The next bounded task is a targeted frame/note review of `INTERVAL_ONLY` rows, prioritizing:

1. dates not represented among the 16 current exact dates;
2. LONG rows, because the current exact set has only 14 LONG;
3. rows whose source note has an exact chart-clock anchor and a trade box/entry call visible in a source frame.

A row may be promoted only when source evidence independently pins one unique M1 entry minute.

Do not:
- infer the minute from current/historical XAUUSD prices;
- choose the midpoint of a range;
- round toward a convenient candle;
- use outcome information to resolve an entry;
- use any `derived/` Badar file.

Only after the timestamp set is stable should the full source-only authorship/execution adjudication and primary-eligibility count be frozen.

## Governance

- no 2022-2025 XAUUSD accessed;
- no 2026 XAUUSD market data accessed;
- no model fitted;
- no CI triggered;
- D-088 chronology blocker remains fully in force.
