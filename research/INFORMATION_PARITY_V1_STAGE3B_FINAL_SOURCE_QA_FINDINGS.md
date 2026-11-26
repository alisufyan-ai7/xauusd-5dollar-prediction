# Information Parity V1 — Stage 3B Final Source QA and Adequacy Certification

Status: **D-116 SOURCE-ONLY DATASET FROZEN; NUMERICALLY ADEQUATE; EMPIRICAL JOIN BLOCKED BY D-088**

Source: `alisufyan-ai7/unpack-human-trading-strategies-claude`, pinned commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`; `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`.

## Canonical artifacts and byte hashes

- `research/reference/information-parity-v1/stage3b-source-events-v1.csv`
  - SHA-256 `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd`
- `research/reference/information-parity-v1/stage3b-source-row-dispositions-v1.csv`
  - SHA-256 `bf9fed8d952b9a0195ef1bfa3b036ba1e5489daec1169c7075ac36968a722604`
- `research/reference/information-parity-v1/stage3b-source-freeze-manifest-v1.json`

SHA-256 values identify the exact UTF-8 file bytes including terminating newline. Historical 15 batch event files and the non-table backfill remain untouched.

## Final primary-eligible source counts

- **251 canonical event records** in total; **250 primary eligible**.
- **107 ACT** (**47 LONG**, **60 SHORT**); **39 ACT dates**.
- **143 explicit P3 REJECT/WAIT** eligible; **39 paired ACT-and-P3 dates**.
- Five independently source-supported P2 unfilled limit commitments were added through D-115, outside the original trade table.

Under D-099, Task A's minimum of 40 ACT / 40 P3 / 20 paired dates and Task B's 40 ACT / 20 dates / 15 LONG / 15 SHORT are all exceeded: **SOURCE_EVIDENCE_ADEQUATE**.

This is *not* a Stage 3B recognition-model PASS, and does not imply economic profitability or live-trading authorization.

## Complete pinned trade-table accounting

The pinned trade table contains **123 source rows**, including **122 XAUUSD** and **1 BTCUSD**. Exactly **107 source keys** are attached to eligible ACT events; five are explicit same-plan additional pieces, so those 107 keys map to **102 table-derived ACT**. The other **16 table rows** (15 XAUUSD and one BTCUSD) receive individually explicit exclusions in the disposition register, including pre-stream activity, other-person trades, signal-only, chart-tool-only, and insufficient personal ownership evidence. Every source row is accounted for, none is attached to two independent ACTs, and no nonexistent source key is referenced.

## Canonical corrections, preserved as audit history

1. Six Batch01 rows — `S3B-ACT-0002`, `S3B-ACT-0004`, `S3B-ACT-0006`, `S3B-ACT-0007`, `S3B-ACT-0008`, `S3B-ACT-0011` — had a surplus empty CSV cell immediately before `source_evidence_refs`, shifting their evidence and eligibility columns. The canonical derivative removes **only that extra empty cell** to restore the frozen 25-column schema. Underlying evidence, timing, eligibility and historical batch files are otherwise unchanged.
2. The Oct 2 `S3B-REJ-0141` statement at 13:08Z ('today is enough') is followed by `S3B-ACT-0100`, a new Badar Exness-real short at 13:11–13:12Z. The statement remains present for source provenance, but its `primary_task_a_eligible` is **false**, with an explicit `exclusion_reason`, because it is not a defensible final session-stop hard negative. Thus the D-115 provisional 144 P3 is corrected to **143 eligible P3**.

No inference from realized trade outcomes, subsequent price paths or provider prices contributed to eligibility decisions.

## Static cross-batch QA

- 251 unique event IDs; 25 schema columns; nonempty source-evidence references after the documented six-row repair.
- All source identities match the pinned Badar commit and table blob.
- UTC interval endpoints follow inclusive candidate M1-minute semantics; widths are consistent and within the frozen 1–5-minute cap.
- No primary ACT and P3 candidate-minute intervals overlap; no retained same-day session-stop P3 precedes an eligible later ACT.
- Source-specific UTC+4/UTC+5 chart/broker UTC mappings retained per event; no universal timezone assumed.
- Same-plan collapses remain visible via source-row keys and the separate original-row disposition register.
- Review of pinned source notes and source-cited frames does not claim independent pixel-by-pixel examination of every original source frame.

## Governance

**D-088 remains closed.** This source-only freeze does *not* authorize acquisition/reconstruction/joining of 2026 provider XAUUSD (nor DXY), Stage 3B empirical fitting, Stage 4 ablation, Stage 5 economics, CI/provider runs, broker mutations or opening sealed 2022–2025 evaluation periods. Original D-097 exact-real-entry teacher benchmark remains **INSUFFICIENT / NOT TESTED**.

Next action: a **separately recorded D-088 chronology/reserve-boundary scientific review**. No chronology modification is implicit in D-116.
