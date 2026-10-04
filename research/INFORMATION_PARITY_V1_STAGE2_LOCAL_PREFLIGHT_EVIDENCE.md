# Information Parity V1 — Local Deterministic Preflight Evidence

Status: **LOCAL LOGIC GATE PASSED — NOT CI**

Source branch:
`research/information-parity-v1-stage2-preflight`

Source head reviewed/materialized:
`eebee1891b906aae1bfce6d6d9422ce52b8b5281`

## What was actually executed

The Stage 2 deterministic preflight was executed in the local container, not in GitHub Actions.

Local runtime:
- Python 3.13.5
- Node v22.16.0
- npm 10.9.2
- numpy 2.3.5
- pandas 2.2.3
- requests 2.32.5
- beautifulsoup4 4.14.3

Commands executed locally:
1. Python `py_compile` over the materialized Stage 2 synchronization/DXY/macro/builder/validator/preflight files.
2. `python3 tests/test_information_parity_stage2_preflight.py`.
3. A separate deterministic diagnostic replay to print exact D1/W1/DXY/integrity results and explicitly verify the negative leakage test.

No GitHub Actions workflow was triggered for this local execution.

## Local deterministic result

Overall:
- compile: PASS
- offline deterministic preflight: PASS
- exit code: 0
- integrity validator: PASS
- sealed periods accessed: none
- injected `future_return` contamination: correctly rejected

Deterministic outputs:
- synchronized M1 rows: 40,319
- BID flat fills: 1
- ASK flat fills: 1
- DXY common timestamps: 40,314
- DXY common share: 0.9998511904761904
- DXY-unavailable decision rows: 1
- maximum age on DXY-available rows: 5.0 minutes
- D1 rows: **28**
- D1 source-count distribution: 23 H1 bars on 1 day; 24 H1 bars on 27 days
- W1 rows: **4**
- macro schedule available on all deterministic decision rows: yes
- previous-day high populated on 38,880 deterministic rows
- integrity warnings: none

These exact D1/W1 results are the intended regression for D-074.

## Local execution-log identity

Local execution log SHA-256:

`a80a1e9b6e001d1a5b62a7fe9e9e3b8fe57330f1fbc0f92756e94f8543516014`

The chat runtime retains the local log and structured summary as user-visible artifacts for this conversation.

## Important limitation

This is a **logic-gate execution**, not the final exact-runtime confirmation.

The local container does not provide the frozen accepted-smoke environment:
- required final CI Python: 3.12.14
- required final CI Node: 22.23.3
- required final CI pandas: 3.0.6

Also, because the local container cannot clone GitHub over the network, the source was materialized through the GitHub connector. Three critical files and the BLS snapshot were byte-identical to their GitHub blobs:
- synchronization script
- synthetic-DXY script
- BLS 2016 schedule snapshot

Some larger materialized files were semantically reconstructed from the fetched branch content and therefore were not byte-identical after local formatting.

Therefore this result means:

> The corrected Stage 2 logic now passes the deterministic integration scenario locally, including the D1/W1 path that previously failed.

It does **not** yet mean:

> the exact branch bytes under the exact pinned CI runtime have passed.

## Next gate

Do not trigger provider-data CI.

Before any exact-runtime preflight CI:
1. reconcile the remaining locally materialized test-critical files against their GitHub blob identities or complete an equivalent exact-source review;
2. finish static review for pandas index-alignment / merge / as-of assumptions;
3. then run one intentional manual deterministic-preflight CI under the pinned runtime;
4. poll that CI for up to the first four minutes, per user instruction.

No model training is authorized.

2022-2025 XAUUSD remain sealed.
