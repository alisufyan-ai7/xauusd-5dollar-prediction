# D-137 — D-136 Transport Recovery Consumed on Plain HTTP 403; Stage 3B Still NOT TESTED

**STATUS: D-134 RECOVERY ATTEMPT CONSUMED / PROVIDER ACCESS DENIED / ZERO USABLE MARKET ROWS / NO MODEL FIT / NO RERUN**

D-136 execution:
- commit: `c20e987e559f9ed4a1c7d8d5674e017baeb211b9`
- workflow run: **45901570026**
- job: **140188341343**
- workflow attempt: **1**
- exact trigger/runtime/browser/no-provider guards: **PASS**
- transport: **dukascopy-node 1.51.1**
- sanity symbol: **XAUUSD BID**
- sanity interval: `2026-06-01T00:00:00Z <= t < 2026-06-02T00:00:00Z`
- generated endpoint: `https://jetta.dukascopy.com/v1/candles/minute/XAU-USD/BID/2026/6/1`
- observed transport response: **HTTP 403**
- WAF token used: **no**
- classifier: `HTTP_403_ACCESS_DENIED`
- market file saved: **no**
- usable provider rows: **0**
- full eight-series acquisition started: **no**
- candidate dataset built: **no**
- model fitted: **no**
- Stage 3B scientific result: **NOT TESTED**

The exact 1.51.1 diagnostic says the provider returned a **plain 403** and that WAF token recovery does not apply to a plain 403. This is no longer an inferred zero-byte/WAF diagnosis; the HTTP status is directly observed.

## Compact evidence

D-136 artifact:
- ID: **15156486347**
- digest: `sha256:3c12148febd6ae8f624510541440750064a52b5a301d42a5e6b62888eb119742`
- ZIP size: **1452 bytes**
- exactly three files:
  - `reports/transport-sanity-xauusd-bid.json` — 523 bytes
  - `reports/compact-evidence-sha256.txt` — 381 bytes
  - `reports/transport-sanity-xauusd-bid.log` — 852 bytes
- no provider CSV
- no WAF token/cache
- no normalized market layer
- no candidate dataset
- no predictions or benchmark result.

Evidence file hashes:
- sanity JSON: `39715ecfae217a3a048738372604380e58144a05f640ecde48c682d628a1764c`
- sanitized sanity log: `5f5fbfb3c1accad5f0b742b1c744f8abf95231e84faa97a75ecfe7555ebcd023`

Cleanup of raw/private/derived paths completed before artifact upload.

## Scientific interpretation

This is a **provider-access failure**, not a recognition-model result.

No usable market observation entered the Stage 3B experiment. Therefore:
- do not classify Stage 3B as PASS, FAIL, NEGATIVE or MIXED;
- do not infer anything about FULL-vs-GOLD information value;
- do not infer profitability;
- do not tune or alter the frozen teacher/features/models/gates based on this failure.

The correct scientific state is **NOT TESTED**.

## Governance

The one D-134 recovery attempt is consumed. D-136 must not be rerun.

The machine-readable plan is now `RECOVERY_ATTEMPT_CONSUMED_HTTP_403_ACCESS_DENIED`; provider/model/CI-provider execution is disabled and the recovery authorization allowlist is empty.

A future attempt cannot be justified as another 1.51.1 retry. It requires a separately documented **provider-access strategy** because the currently pinned supported transport received a direct plain 403 before WAF recovery could apply.

Safe owner-independent work remains:
- repository/upstream documentation research;
- alternative authorized access-path design;
- deterministic/no-network tests and documentation;
- no Dukascopy market request.

2022–2025, Oct9–Nov30 2026, December shadow, 2027, Stage4/5 and broker actions remain blocked.
