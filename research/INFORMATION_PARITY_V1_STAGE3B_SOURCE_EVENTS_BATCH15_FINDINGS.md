# Information Parity V1 — Stage 3B Source Event Construction Batch 15

Status: **OCT 2 + OCT 6 + OCT 8 FROZEN — FINAL PINNED TRADE-TABLE DATES REVIEWED**

Decision D-114. Parent D-099 through D-113.
Pinned Badar source commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`; live_trades blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`.
Artifact: `research/reference/information-parity-v1/stage3b-source-events-v1-batch15.csv`.

## Source table dispositions

Nine XAUUSD table rows reviewed:

| Date | Source row | Disposition | Evidence |
|---|---|---|---|
| Oct 2 | `PxDGTxs-Cvc#1` | ACT-0096 LONG P2 E1 | Current NFP one-minute action [22:02]; low-risk commitment |
| Oct 2 | `PxDGTxs-Cvc#2` | ACT-0097 LONG P2 E1 | Distinct later pullback/engulfing confirmation, second entry [27:49]-[30:54] |
| Oct 2 | `PxDGTxs-Cvc#3` | ACT-0098 LONG P2 E1 | New OB/FVG return and close-confirmed entry [35:28]-[39:42]; uncertain interim exit/re-entry not double-counted |
| Oct 2 | `PxDGTxs-Cvc#4` | ACT-0099 LONG P2 E1 | New M5 bullish-close action [51:36] |
| Oct 2 | `PxDGTxs-Cvc#5` | ACT-0100 SHORT P1 E1 | Direct Exness **Real** sell/size-management demo [64:00]-[66:20] |
| Oct 6 | `EsAa5_T_kbQ#1` | **EXCLUDED PRE_STREAM / OTHER_PERSON_UNCLEAR** | Before-live short described by co-host while Badar had not joined; no live Badar commitment [5:39]-[6:41] |
| Oct 6 | `EsAa5_T_kbQ#2` | ACT-0101 SHORT P2 E1 | Badar's current sell limit at 4158.5, [34:10]; first-person commitment |
| Oct 8 | `D85FC79tI6w#1` | ACT-0102 SHORT P2 E2 | First-person sell plan [8:34] and explicit current holding [14:33] corroborated by position/P&L frames |
| Oct 8 | `D85FC79tI6w#2` | **EXCLUDED SIGNAL_OR_TOOL_ONLY** | Drawn bullish breakout position tool at ~26:00, no personal buy commitment or confirmed execution |

Oct 2 #1-#4 have separate intervening market setups, entries and management/exit episodes; no forced collapse. Oct 2 #3's ambiguous early exit/possible re-entry stays one ACT. The Oct 2 P1 classification applies only to the final Exness real-account short, not to TradingView position tools.

## Explicit P3 decisions

Seven unique source-supported decisions:
- **Oct 2 (4)**: reject mid-range/pre-NFP entry [10:10]; wait for buy confirmation at marked zone [34:26]; wait for strong close instead of weak new entry [45:51]; stop further chart trade attempts [61:11].
- **Oct 6 (2)**: defer until H1 close [19:57]; explicitly decline another scalp while prior trade runs [45:16].
- **Oct 8 (1)**: end session instead of further entries due to chaotic event environment [27:45]-[28:48].

Co-host-only Oct 6 early trade advice, viewer remarks, tutorial examples, and October 8's tool-only long are excluded as primary P3/ACT where no qualifying current decision exists.

## Cumulative provisional source state

- **102 ACT / 47 LONG / 55 SHORT**
- **39 distinct ACT dates**
- **144 explicit P3 REJECT/WAIT**
- **39 paired ACT+REJECT dates**

The frozen numerical D-099 floors remain exceeded. Counts are provisional until mandated backfill and cross-batch reconciliation.

## Integrity cautions

- Oct 6 trade #2 source row gives an approximate chart time around 19:04 UTC+5 while direct frame-derived offset of [34:10] suggests about 19:06; event interval spans both, not midpoint-imputed.
- Oct 8 frame source is 360p and timing/execution less legible, so short #1 is P2/E2 and breakout long #2 remains excluded.
- Timing intervals all <=5 M1 minutes. No outcome fields used for labels.
- Oct 2's real Exness evidence does not retroactively promote other trades.

No provider XAUUSD, sealed periods, `derived/` interpretation, fitted model or CI accessed.

Next: non-table ACT backfill from all pinned source notes/transcripts/frames; explicit 122-row XAUUSD trade disposition, 1 non-XAUUSD exclusion, same-plan collision audit, ACT/P3 timing conflict QA, final canonical merge/hash and source adequacy certification. D-088 remains closed.
