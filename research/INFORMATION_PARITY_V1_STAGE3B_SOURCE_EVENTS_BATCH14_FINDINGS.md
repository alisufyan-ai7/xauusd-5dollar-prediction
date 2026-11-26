# Information Parity V1 — Stage 3B Source Event Construction Batch 14

Status: **SEP 30 + OCT 1 FROZEN — ONE TEAM-OWNED EXCLUSION AND ONE SAME-PLAN SELL COLLAPSE**

Decision: D-113. Parent: D-099 through D-112.
Source: `alisufyan-ai7/unpack-human-trading-strategies-claude` at `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`; trade-table blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`.
Artifact: `research/reference/information-parity-v1/stage3b-source-events-v1-batch14.csv`.

## Coverage and dispositions

Four pinned XAUUSD trade-table rows across two dates:

| Source row | Adjudication | Reason |
|---|---|---|
| `EOBnMz2Y_9k#1` (Sep 30) | **EXCLUDED — OTHER_PERSON / NOT_BADAR_ACT** | Team presenter was running VIP-group short before Badar joined; Badar at [22:49] explicitly says he forgot to take it |
| `EOBnMz2Y_9k#2` (Sep 30) | **ACT-0094 P2 E1 SHORT** | Badar explicitly commits at [50:03]-[51:06] |
| `EOBnMz2Y_9k#3` (Sep 30) | **SAME_PLAN_COLLAPSE into ACT-0094** | [52:08]-[54:15] describes a smaller tighter-stop addition to his *existing* sell, not an independent thesis |
| `PYPzCJV-YXE#1` (Oct 1) | **ACT-0095 P2 E1 SHORT** | Direct M15-close sell commitment at [5:56] corroborated by current position tool |

Two independent ACT events, zero LONG, two SHORT; both P2 E1. Sep 30 original ACT timing uses the initial commitment, not the later add; source-supported 2-minute interval. Oct 1 entry is minute-anchored by frame clock and [5:56] statement.

## Primary P3 decisions

Seven distinct explicit Badar REJECT/WAIT events:
- Sep 30: `REJ-0131` reject chasing sell after extended drop [20:16]; `REJ-0132` defer sell until gap/retrace [29:48]; `REJ-0133` explicitly refuse buy at current low [30:58].
- Oct 1: `REJ-0134` defer buy without bullish M5 close [3:50]; `REJ-0135` wait for M15/retrace confirmation before new scalp sell [11:04]; `REJ-0136` refuse sell at current low [15:27]; `REJ-0137` reject current buy because no sign/weak buy liquidity [25:03].

No P3 was created for presenter-only remarks before Badar joins Sep 30, generic teaching, viewer trades, routine management of existing positions, or repeated versions of the same deferred retrace plan. Timing derives from source frame-clock anchors, not provider prices. All seven decisions are single-minute anchors with explicit source transcript citations; uncertainty in transcript translation remains an audit caveat.

## Cumulative Stage 3B source state after Batch 14

- **95 ACT / 43 LONG / 52 SHORT**
- **36 ACT dates**
- **137 explicit P3 REJECT/WAIT**
- **36 paired ACT+REJECT dates**

All D-099 numerical adequacy floors remain exceeded. This is *numerical source construction*, not final source adequacy certification.

## Constraints and next work

No `derived/` content, provider XAUUSD, market reconstruction, fitting, sealed years or CI used.

Next chronological source-only chunks: Oct 2, Oct 6, Oct 8. Then non-table ACT backfill, complete source-row coverage/disposition audit, duplicate/collapse and temporal-conflict QA, timing/timezone QA, final canonical merge/SHA-256 and certification. D-088 remains closed.
