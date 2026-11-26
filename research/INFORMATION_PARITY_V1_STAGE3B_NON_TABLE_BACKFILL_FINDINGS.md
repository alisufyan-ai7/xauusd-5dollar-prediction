# Information Parity V1 — Stage 3B Mandatory Non-Table ACT Backfill

Status: **SOURCE-ONLY BACKFILL FROZEN (D-115); FIVE ELIGIBLE UNFILLED LIMIT COMMITMENTS**

Pinned Badar source commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`; pinned trade-table blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`. Only Badar source-layer notes/transcripts/frame descriptions used, never `derived/`, provider market data or trade outcomes.

Artifact: `research/reference/information-parity-v1/stage3b-source-events-v1-backfill.csv`.

## Primary-eligible non-table ACT

All five events are Badar-owned live-stream SHORT resting-limit commitments, **not broker-confirmed fills**; therefore P2 (not P1). No trade-table key is assigned because none is in the pinned table.

| Event | Date | Stream | Grade | Source proof / reason |
|---|---|---|---|---|
| ACT-0103 | Jul 7 | `9d7IHhIAi6M` | E1 | Direct [56:00] 'I have applied the direct limit'; unfilled at end |
| ACT-0104 | Jul 23 | `m0l1wj9IZ2o` | E2 | First-person/plural [38:38] 'we also put a limit', tool and subsequent personal missed-by-3-4-pips account |
| ACT-0105 | Sep 2 | `CKTqdFza1HE` | E2 | Real-terminal sell-limit ticket after explicit [4:21] limit discussion; 4420→4435 amendment treated as one plan |
| ACT-0106 | Sep 14 | `C18mm9p2oW4` | E1 | Direct [5:19] 'I am putting a limit' at 4302; frame 6:00 tool; no fill |
| ACT-0107 | Sep 17 | `6trb-6A2t6Q` | E2 | [19:21]-[20:54] placed limit; Badar specifies 'my order is short basically'; translation earlier has ambiguous buy language, so not E1 |

All events have source-clock-derived inclusive 1-5 M1-minute intervals, no midpoint inference. Their source timestamps are distinct from existing ACT/P3 intervals.

## Other reviewed non-table candidates — excluded or collapsed

- `2c249LLRY_Q` Jul 29 upper main sell limit: explicitly a paired/split plan with the already included lower sell; do not create a second independent ACT event. The missed fill is acknowledged but does not force duplication.
- `EVm0u9Csglk` Aug 4 unfilled upper sell: source says *planned* and 'I will take if higher'; no sufficiently confirmed personal active limit placement.
- `M078bAYBc-E` Jul 22 two unfilled buy-limit drawings: conditional 'if it comes' language and tool movement lack unambiguous E1/E2 personal *placement*, so not primary.
- `suuicaoUvDQ` Jul 28 missed sell from mid supply: 'my entry did not hit' suggests possible personal order, but no unambiguous placement; excluded conservatively at E3-like ambiguity.
- `gfP4EW1IfVE` unlogged 'another sell': no separate new box; could be redrawing management of prior trade; excluded without proof of an independent action.
- `HOidQitTyAc` tentative buy limit 'I can put it': not placed; semantic plan only.

This backfill screened all 46 pinned stream notes for limit/unfilled/non-table indications and revisited the detailed transcripts for potential personal placements. It does **not** turn generic instruction, chart projections, viewer trades, or outcomes into ACT.

## Provisional cumulative after D-115

**107 ACT / 47 LONG / 60 SHORT / 39 ACT dates / 144 explicit P3 / 39 paired dates**.

All D-099 numerical floors still exceeded. Final CSV/adequacy certification requires cross-batch schema repair and complete row disposition validation. D-088 remains closed.
