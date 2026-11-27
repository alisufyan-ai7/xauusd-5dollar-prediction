# D-147 — D-144/D-140 Direct Public Datafeed Attempt Closure

**STATUS: D-144 ATTEMPT CONSUMED / TLS CONNECTION RESET BEFORE HTTP / ZERO VALID MARKET OBJECTS / NO MODEL FIT / STAGE 3B NOT TESTED / NO RERUN**

## Pre-execution acceptance

D-145 exact-runtime no-provider run:
- workflow run: **45962942690**
- job: **140384800318**
- head: `3c9d524a31956f3b12193689bfbd9acfa983537c`
- CPython: 3.12.14
- deterministic tests: **14/14 PASS**
- provider requests: **0**
- conclusion: **SUCCESS**

The frozen execution plan was 8 June 1 sanity requests plus 1,040 full daily opportunities = 1,048 maximum planned GETs, below the hard 1,050 ceiling.

## Single authorized execution

D-146:
- commit: `942168a0c46541705f44ca3d0c8630d092800d9e`
- workflow run: **45963138729**
- job: **140385418030**
- workflow attempt: **1**
- exact trigger/runtime/deterministic guards: **PASS**
- representation: `DUKASCOPY_PUBLIC_DATAFEED_DIRECT_M1_V1`
- retries authorized/performed after failure: **0**
- alternate host/source: **not used**

First sanity request:
- logical series: **XAUUSD BID**
- requested market date: **2026-06-01 UTC**
- URL: `https://datafeed.dukascopy.com/datafeed/XAUUSD/2026/05/01/BID_candles_min_1.bi5`
- month component `05` is the frozen zero-based June convention
- failure stage: **TLS handshake**
- observed HTTP status: **none**
- failure: `URLError: <urlopen error [Errno 104] Connection reset by peer>`
- valid payload: **none**
- valid decoded rows: **0**

Because the first sanity connection failed before an HTTP response, the fail-closed workflow stopped immediately:
- sanity requests 2-8: **not made**
- full 1,040-object acquisition: **not started**
- normalized market layer: **not built**
- candidate dataset: **not built**
- model fit / GOLD-vs-FULL benchmark: **not run**

## Compact evidence

Artifact:
- ID: **15181796258**
- digest: `sha256:28979e29c96c0f6682ec7f4be1aecf41de63b087e9fb6b292a54430f3cd1df05`
- size: 2043 bytes

Exactly three files:
- `reports/execution-identity.json` — SHA-256 `a759674abc274911188a9333db5cc0edfd373b9b8f9ce104bbf31689a38e620d`
- `reports/public-datafeed-execution.log` — SHA-256 `da815fbd2de81bde38ecfa73ff9f5167934870a0a4b6a02372c49ec1315f7991`
- `reports/compact-evidence-sha256.txt` — SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The cleanup step ran before artifact upload; there is no raw/derived market or model payload in the artifact.

## Scientific interpretation

This is an access/transport failure before usable market data, not a recognition-model result.

Correct scientific state:
**Stage 3B = NOT TESTED**.

Do not call this PASS, FAIL, NEGATIVE or MIXED for the frozen hypothesis. No FULL-vs-GOLD score exists and no profitability inference is permitted.

## Governance closure

The one D-144 authorization is consumed. D-146 must never be rerun.

D-147:
- disables the D-140 provider flag;
- empties the executable D-140 authorization allowlist;
- removes the one-time execution trigger;
- leaves D-116 teacher data, 92/155 feature sets, 39 LODO folds, models, thresholds, dates and all sealed/quarantine/shadow/broker restrictions unchanged.

Any future provider request requires a separately preregistered access strategy and a new explicit owner authorization. Safe owner-independent research may continue without issuing market-data requests.
