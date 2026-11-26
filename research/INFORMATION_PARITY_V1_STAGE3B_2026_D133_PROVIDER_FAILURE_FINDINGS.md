# D-133 — D-132 Provider Transport Failure; Stage 3B Remains NOT TESTED

**STATUS: SINGLE D-124 PROVIDER ATTEMPT CONSUMED / ZERO USABLE MARKET ROWS / NO MODEL FIT / NO RERUN AUTHORIZED**

D-132 execution:
- commit: `707bdf424b4a810c93dc9ae7d30a07aff245582c`
- workflow run: **45898796339**
- job: **140179219355**
- workflow attempt: **1**
- exact runtime/authorization/pre-provider tests: **PASS**
- first provider request: **XAUUSD BID M1**, `2026-06-01` to `2026-10-09`
- provider download duration: about **12.2 seconds**
- returned file: **0 bytes**
- local guard result: `VALIDATION_FAILED: file missing or empty`
- later symbols requested: **no**
- usable provider market rows: **0**
- dataset built: **no**
- model fitted: **no**
- Stage 3B empirical result: **NOT TESTED**

The frozen D-124 rule allowed one controlled provider attempt. D-132 reached the provider, so that attempt is consumed. **Do not rerun D-132 or create another provider trigger under D-124.**

## Compact artifact verification

D-132 uploaded compact failure evidence only:
- artifact ID: **15155230246**
- artifact digest: `sha256:1ffaac4dc19f6b4edaf8075ef197a53cd0b182fabf57bf7d7dfe0ace92cf8e14`
- artifact ZIP size: **283 bytes**
- contained exactly one file: `reports/compact-evidence-sha256.txt` (**115 bytes**)
- that file records SHA-256 of an empty compact-evidence file:
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- no raw provider file, normalized market layer, predictions, or benchmark result was uploaded.
- raw/derived cleanup step ran.

## Transport diagnosis

The D-124 package pinned **dukascopy-node 1.50.0**. Public upstream evidence created before this run shows a material transport change after that pin:

- upstream issue **#261**, opened 2026-10-17: AWS WAF HTTP 202 challenge can resolve as an empty dataset in older JSON-API code paths, including zero-retry behavior:
  https://github.com/Leo4815162342/dukascopy-node/issues/261
- upstream issue **#264**, opened 2026-10-27: historical requests on 1.51.0 can receive WAF 202 then 403:
  https://github.com/Leo4815162342/dukascopy-node/issues/264
- upstream changelog: **1.51.1 (2026-10-28)** added export-widget headers/tighter 403 handling and stopped inappropriate retry/browser recovery after plain 403:
  https://github.com/Leo4815162342/dukascopy-node/blob/master/CHANGELOG.md

D-132 logs did not enable HTTP/WAF debug, so they do **not prove** the exact HTTP status. The observed zero-byte result is nevertheless strongly consistent with the documented October 2026 provider/WAF transport changes. This is therefore classified as:

`PROVIDER_TRANSPORT_FAILURE — SCIENTIFIC BENCHMARK NOT TESTED`

It is **not** a negative model result, not evidence that FULL lacks signal, and not a profitability conclusion.

## Governance after D-133

The machine-readable plan is now `ATTEMPT_CONSUMED_PROVIDER_TRANSPORT_FAILURE`; provider/model/CI execution flags are disabled. `AUTHORIZED_FINAL_DECISION_SHAS` is empty and the execution guard fails closed.

A recovery may preserve all scientific labels/features/folds/model/gates because no usable market rows or model scores were observed, but a recovery requires a **new explicit transport-recovery authorization** because it necessarily changes the frozen transport and spends another provider attempt.
