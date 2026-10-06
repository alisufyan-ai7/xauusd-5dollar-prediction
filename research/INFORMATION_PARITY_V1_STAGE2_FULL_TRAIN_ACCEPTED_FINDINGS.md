# Information Parity V1 — Stage 2 Full-TRAIN Accepted Findings

Status: **ACCEPTED — STAGE 2 COMPLETE**

Accepted run:
- workflow: `information-parity-stage2`
- run: **37474263432**
- head: `51664a31ab7739e2a4bdba9df70eadf02249133a`
- conclusion: **SUCCESS**
- artifact: `information-parity-stage2-full-train`
- artifact ID: **11421634040**
- artifact digest: `sha256:41ebcaacaaaddafc6433e787ee9232eccf5128205b8648cecfd20f595d52985a`

This run is the accepted one-shot same-job 2016-2021 TRAIN Information Parity V1 Stage 2 build.

## Governance

- 2016-2021 TRAIN only.
- 2022-2025 XAUUSD accessed: **none**.
- no future-return, target/stop, trade-outcome, P&L or model-training fields were used.
- raw provider market files were not committed.
- Exness/broker state was not mutated.

## Runtime

The accepted run used the frozen Stage 2 environment:
- CPython 3.12.14
- pandas 3.0.6
- numpy 2.5.3
- requests 2.34.2
- beautifulsoup4 4.15.0
- Node v22.23.3
- npm 10.9.9
- dukascopy-node 1.50.0

## Final status

Final summary:
- status: **PASS**
- scope: `2016-2021_TRAIN_CONTINUOUS`
- continuous state across years: **true**
- integrity warnings: **none**
- integrity checks: **27/27 PASS**
- macro status: **PASS**
- sealed XAUUSD periods accessed: `[]`

The workflow completed every required stage:
1. macro readiness;
2. same-job 2016-2021 market acquisition;
3. continuous synthetic DXY construction;
4. raw-provider release after identities/DXY were frozen;
5. continuous Information Parity layer build;
6. full-range integrity validation;
7. normalized identity manifest;
8. hard-checked full-TRAIN summary;
9. compact evidence upload.

## Core row counts

- XAUUSD M1 market state: **2,124,206**
- decision index: **2,124,206**
- structural state: **2,124,206**
- macro event state: **2,124,206**
- neutral trade/risk template: **2,124,206**
- synthetic DXY M1: **2,138,819**
- macro event schedule: **652**

Canonical XAUUSD bars:
- M3: **707,260**
- M5: **423,907**
- M15: **140,644**
- M30: **69,898**
- H1: **34,606**
- H4: **7,487**
- D1: **1,459**
- W1: **292**

## Per-year decision/readiness coverage

### 2016
- decision rows: 354,364
- feature-ready market share: 0.821449
- DXY available share: 0.976197
- previous-day available share: 0.995939

### 2017
- decision rows: 352,788
- feature-ready market share: 0.823866
- DXY available share: 0.999660
- previous-day available share: 1.000000

### 2018
- decision rows: 353,923
- feature-ready market share: 0.799148
- DXY available share: 0.996423
- previous-day available share: 1.000000

### 2019
- decision rows: 353,290
- feature-ready market share: 0.720669
- DXY available share: 0.960520
- previous-day available share: 1.000000

### 2020
- decision rows: 355,495
- feature-ready market share: 0.806805
- DXY available share: 0.960697
- previous-day available share: 1.000000

### 2021
- decision rows: 354,346
- feature-ready market share: 0.820170
- DXY available share: 0.949947
- previous-day available share: 1.000000

Feature readiness is an information-availability property, not a trade-selection result.

## Synthetic DXY coverage

Per-year exact six-constituent common-share of union:
- 2016: 0.965366
- 2017: 0.989852
- 2018: 0.986066
- 2019: 0.945356
- 2020: 0.932871
- 2021: 0.898733

Sum-by-year common timestamps: **2,138,819**.

The final validator passed backward-as-of/staleness integrity and the continuous-DXY cross-year-state check.

## Macro coverage

Normalized schedule rows: **652**.

Every admitted family/year passes with no recorded errors.

2016:
- CLAIMS 52 / CPI 12 / FOMC 8 / GDP 12 / JOLTS 12 / NFP 12

2017:
- CLAIMS 52 / CPI 12 / FOMC 8 / GDP 12 / JOLTS 12 / NFP 12

2018:
- CLAIMS 52 / CPI 12 / FOMC 8 / GDP 12 / JOLTS 12 / NFP 12

2019:
- CLAIMS 52 / CPI 12 / FOMC 9 / GDP 11 / JOLTS 12 / NFP 12

2020:
- CLAIMS 53 / CPI 12 / FOMC 11 / GDP 12 / JOLTS 12 / NFP 12

2021:
- CLAIMS 52 / CPI 12 / FOMC 8 / GDP 12 / JOLTS 12 / NFP 12

No actual/forecast/previous/revision/surprise fields are admitted.

## Causal continuity across year boundaries

The validator reports `year_boundary_continuity=PASS`.

At each 2017-2021 first observed row:
- previous-day state is available;
- DXY is available with age 0 minutes.

The first observed XAUUSD minute is not one-minute contiguous with the preceding year's last observed minute at any boundary because of real market-closure gaps. Therefore the frozen contiguous rolling-window rule legitimately reports `feature_ready_market=0` at those first observed rows. This is **not** an artificial January cold start.

## Integrity checks

All final checks passed:
- M1 decision-time semantics
- year scope
- nonnegative spread
- M3/M5/M15/M30/H1/H4/D1/W1 availability
- D1 <- H1 hierarchy
- W1 <- D1 hierarchy
- structural alignment/causality/distances
- previous-day backward as-of state
- DXY backward as-of
- macro coverage/counts
- macro timezone alignment
- macro state alignment
- macro outcome-field exclusion
- neutral trade/risk state
- decision-index alignment/year continuity
- year-boundary continuity
- sealed-period guard

Warnings: **none**.

## Frozen evidence identities

Artifact digest:
`sha256:41ebcaacaaaddafc6433e787ee9232eccf5128205b8648cecfd20f595d52985a`

Compact evidence identities:
- raw market manifest: `128496c869cc99aff7790a1b2f8ad3fd03505fbfa41202edd6a4d07bd6717919`
- synchronized XAUUSD manifest: `4041c62ddcd1717f466dd5cdc9ce0426053603c8ef0c692794ab249f7740ea11`
- normalized full-TRAIN manifest: `e9440bb0971c52456d1a79ddaa0144aa36fd758666421392bc4e7203132ea4c9`
- build report: `938748f27bfb4da7b1e4681d768a8cd251dd5c5b4e6971c9e704fcb9accd467b`
- full-TRAIN summary: `34e577e7755b2e3ebd9d619329c84ea26a9eca3d134677fc736236ed5c622d1f`
- integrity report: `79867cb548feeec8b537cfbbc80678057c664867e86c8ddb9fdba771376c5bf4`
- macro coverage report: `38b8fd9a0944b3a8f0a3823a27008d7649ee5a02d1ffc1f58b6b0a08f3a8b498`
- continuous DXY report: `d11f9650602773cc7c408f7430e56a4c990431a342400fbd4454b1fc19ea8092`

Raw manifest:
- files: **48**
- total bytes: **932,099,909**

Normalized manifest:
- files: **19**
- total bytes: **852,247,735**

## Compact SHA-file self-hash note

`compact-evidence-sha256.txt` was generated by hashing the evidence directory while simultaneously writing into that same file. Its own line therefore hashes a partially written version of itself and is not a stable identity for the final file.

This does **not** invalidate the run:
- the GitHub artifact digest is authoritative for the uploaded ZIP;
- all scientific/integrity reports were produced before upload and passed;
- the individual non-self evidence hashes above remain meaningful;
- no provider/data rerun is justified solely to repair a self-referential bookkeeping hash.

Future compact-hash generation should exclude `compact-evidence-sha256.txt` itself.

## Scientific interpretation

Stage 2 has achieved its stated purpose: a reproducible, timestamp-safe, causally continuous 2016-2021 information environment has been built and integrity-validated from the frozen V1 source set.

This is **not** evidence of profitability or expert-level decision quality.

Passing Stage 2 does not authorize opening 2022-2025 or training/tuning against sealed periods.

## Next stage

Per the frozen Stage 2 preregistration, the next research action is:
1. freeze this accepted information-layer identity;
2. preregister Stage 3 Badar decision-recognition dataset construction;
3. define teacher-record provenance and matched non-trade controls;
4. define one fixed recognition/evaluation protocol before fitting.

No Stage 3 empirical/model run is authorized until that preregistration is committed.
