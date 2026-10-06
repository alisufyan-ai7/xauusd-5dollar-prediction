# Information Parity V1 — Stage 2 Full-TRAIN Run 1 Findings

Status: **FAILED AT MACRO NORMALIZATION — NOT AN ACCEPTED FULL-TRAIN BUILD**

Run:
- workflow: `information-parity-stage2`
- run: **37434856203**
- head: `cdf2129d0c6df64ab67c5b192f828b2cbc3731a4`
- conclusion: **FAILURE**
- artifact: `information-parity-stage2-full-train`
- artifact ID: **11400771061**
- artifact digest: `sha256:4f8cff0e95191d7992be27ee4e2bc058fdc003e69e33da6f412c2df108d753a4`

## What passed

Before the failure:
- frozen runtime / compilation gate passed;
- repository-controlled full-TRAIN prerequisite verifier passed;
- one 2016-2021 market snapshot was acquired;
- all six annual XAUUSD BID/ASK histories synchronized successfully;
- one continuous 2016-2021 synthetic DXY series built successfully.

Observed synchronized XAUUSD rows:
- 2016: 354,364
- 2017: 352,788
- 2018: 353,292
- 2019: 352,664
- 2020: 355,495
- 2021: 354,346

Continuous DXY report:
- status: PASS
- cross-year state preserved: true
- common six-constituent timestamps: 2,084,095
- union timestamps: 2,244,275
- sealed XAUUSD periods accessed: none

These are useful diagnostic identities only. Because the workflow did not reach the layer build, integrity validator, normalized manifest or final summary, run 37434856203 is **not** an accepted Stage 2 full-TRAIN build.

## Exact failure

The `Acquire and normalize 2016-2021 macro schedule` step failed.

Coverage:
- 2016: complete
- 2017: complete
- 2018: GDP 9, below floor 11
- 2019: complete
- 2020: GDP 10, below floor 11
- 2021: GDP 10, below floor 11; FOMC 0, below floor 8

2021 FOMC root cause:
- the legacy `fomchistorical2021.htm` Federal Reserve URL returns HTTP 404;
- first-party 2021 FOMC statement indexes/pages remain available elsewhere on federalreserve.gov.

GDP root cause:
- the BEA archive contains legitimate national-GDP title variants using colon or parenthetical syntax after `Gross Domestic Product`;
- the parser admitted only the comma form;
- the embargo text also has punctuation variants such as `A.M., EDT` that the previous regex rejected.

The coverage artifact also accumulated parse errors from unrelated older BEA archive pages because the all-years scan follows candidates before filtering by parsed release year. Those errors become irrelevant once the requested year's admitted national-GDP floor is met, but the undercount prevented that cleanup path.

## Process finding

The full workflow acquired the expensive six-year market snapshot before proving macro readiness. Since macro acquisition is independently fail-fast, this ordering is inefficient.

Correction is frozen in:
`research/INFORMATION_PARITY_V1_STAGE2_MACRO_RECOVERY_ADDENDUM.md`

## Next gate

Do **not** rerun full TRAIN yet.

Required sequence:
1. implement the narrow Fed/BEA parser corrections;
2. add deterministic regressions;
3. pass off-CI deterministic validation;
4. pass one exact-runtime deterministic confirmation;
5. pass one 2016-2021 macro-only network confirmation;
6. only then authorize a second full same-snapshot build.

No model training is authorized.
2022-2025 XAUUSD remain sealed.
