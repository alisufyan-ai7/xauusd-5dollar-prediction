# D-151 — D-148 FREESERV Full Disabled Execution Surface Accepted

**STATUS: PASS / PROVIDER DISABLED / AUTHORIZATION ALLOWLIST EMPTY / ZERO FREESERV MARKET REQUESTS / AWAITING OWNER AUTHORIZATION**

## Candidate representation

`DUKASCOPY_FREESERV_CHART_JSON3_M1_V1`

Pinned public protocol source:
- repository: `Eghosa-Osayande/dukascopy`
- commit: `2e48b12cb3f5d81426a08886e9427af81d10f002`
- DataFeedV1 blob: `47738a147d42c71312329d76e766afe658f8d575`
- compatibility implementation blob: `765850e2c6569e7fa9dcc6f55c6beffd3df37da7`
- compatibility instruments blob: `16493bd886629fb2fd99b56205e2b6d0300fb436`
- generated 2026-10-28 instrument metadata blob: `689b457f9beda4a52c62c255df3594f341030def`

Frozen request semantics:
- host/path: `https://freeserv.dukascopy.com/2.0/index.php`
- `path=chart/json3`
- `interval=1MIN`
- BID=`B`; ASK=`A`
- `time_direction=N`
- UTC epoch-ms `last_update`
- JSONP OHLCV rows
- full page limit: 30,000
- pinned browser-style User-Agent and chart Referer from the inspected public DataFeedV1 source.

## Frozen project implementation blobs

- request/JSONP/fence guard: `59232e36164b26b5e7f647c087e4da9b44b3adf2`
- disabled production acquisition wrapper: `41add4f45ad2f21f9f0b013014fd52e9919a0208`
- structural tests: `245faf527942250af60570a073e20bcf23521d49`
- mocked execution tests: `47a7800261d8c972db5ce7c8eb68f695063c93ac`
- frozen Stage 3B build integration shell: `a74cdfa3da643a3d72d1390867eec49abde514b0`

The production wrapper is deliberately fail-closed:
- `PROVIDER_EXECUTION_ENABLED = False`
- `AUTHORIZED_D148_DECISION_SHAS = frozenset()`

It cannot start an acquisition without a future exact owner-authorization SHA being admitted and the provider flag being enabled in a later decision.

## Deterministic evidence

Local/off-provider suite:
- 16/16 tests PASS
- no network request.

D-149 exact-runtime request/parser gate:
- run: `45964639309`
- job: `140390290104`
- head: `5deec2e6d2e6cf3f46746275792053e7dc4ec5e0`
- CPython 3.12.14
- 8/8 tests PASS
- preflight module contains no provider-network primitive
- provider requests: 0
- conclusion: SUCCESS.

D-150 full disabled-surface run:
- run: `45965048319`
- job: `140391623088`
- head: `03335c626c02c13556e6932a2c072f3cf539068b`
- 16/16 mocked tests PASS
- provider=false / allowlist empty
- conclusion: SUCCESS.
- A harness review found that two intended static checks (explicit production-wrapper compilation and integration-shell `bash -n`) were not actually present in that run's compile step. The functional tests still passed, but D-150 was not used as final acceptance evidence.

D-151 corrected final exact-runtime verification:
- run: **45965177800**
- job: **140392035933**
- head: `4ccf140e567d9251f834f5c808caf513552a05fd`
- CPython: **3.12.14**
- explicit compile of guard, production wrapper and both test modules: **PASS**
- `bash -n scripts/acquire_information_parity_stage3b_2026_freeserv.sh`: **PASS**
- deterministic tests: **16/16 PASS**
- provider flag: **false**
- executable owner-authorization allowlist: **empty**
- provider requests: **0**
- conclusion: **SUCCESS**

The workflow output marker retained the D-150 string from the prior harness, but D-151's run identity and the executed compile/shell/test steps above are the acceptance evidence.

## Frozen candidate execution ceilings for owner review

If later explicitly authorized:
- source representation: `DUKASCOPY_FREESERV_CHART_JSON3_M1_V1`
- market fence: `2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z`
- logical series: 8
- sanity requests: exactly 8
- sanity limit: 2 rows/request
- full page limit: 30,000 rows/request
- maximum full requests per logical series: 11
- hard total request cap: **96** (8 sanity + at most 88 full)
- raw-response byte cap: **350 MiB**
- normalized/intermediate cap: **750 MiB**
- attempts: 1
- retries after any provider/transport failure: 0
- alternate host/source/proxy/VPN/mirror within attempt: forbidden
- no rerun.

The theoretical maximum calendar M1 slots in the 130-day fence is 187,200 per series; seven 30,000-row pages would cover that count if pages fill. The 11-page per-series ceiling is conservative slack, not a promise about server page-fill behavior. If the end fence is not reached within 11 pages for any series, fail closed.

## Scientific invariants

Unchanged from D-124:
- D-116 teacher corpus and hashes;
- 92 GOLD / 155 FULL feature allowlists;
- 39 LODO folds;
- D-120 bounded cold start;
- D-121 macro fail-closed semantics;
- synchronization and synthetic-DXY semantics;
- fixed L2 logistic models and preprocessing;
- event weighting/pooling;
- metrics/bootstrap/advancement thresholds;
- no rescue tuning;
- sealed 2022-2025;
- Oct9-Nov30 quarantine;
- December shadow restrictions;
- no broker/order mutation.

This representation is not claimed byte-identical to Stage-2 JETTA or D-140 direct .bi5.

## Authorization boundary

All owner-independent D-148 code/static/runtime work is complete.

**No FREESERV market request is authorized yet.**

The only remaining prerequisite before a single D-148 provider attempt is a new explicit owner text authorization for the exact ceilings above. No AWS, account, credential, payment method, browser profile or owner-operated infrastructure is required.

Current scientific state remains **STAGE 3B = NOT TESTED**.
