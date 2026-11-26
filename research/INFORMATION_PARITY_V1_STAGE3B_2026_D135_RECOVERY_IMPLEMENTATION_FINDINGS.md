# D-135 — Implement D-134 Transport Recovery and Trigger No-Provider Exact-Runtime Regression

**STATUS AT COMMIT: RECOVERY IMPLEMENTED / PROVIDER STILL DISABLED / NO-PROVIDER CI TRIGGERED**

D-134 authorization commit: `8cdd4edf222b88ac1d7ce15e3d3ac8639a2be155`.

Implemented transport-only recovery surface:
- exact recovery package: `dukascopy-node 1.51.1`;
- upstream release commit identity: `068bf57b67e3cae3f5c952653ef20157d3852699`;
- upstream annotated tag object: `fffda56b04e68a1fa9b6ccbb0404ac33c6a6f516`;
- separate recovery downloader; the consumed D-124/1.50.0 downloader is unchanged for provenance;
- selective debug namespaces capture CLI version, generated URLs/fetch records, WAF HTTP status, WAF-token yes/no and rate-limit diagnostics;
- log classifier distinguishes successful recovery, HTTP 202 challenge, HTTP 403 access denial, valid HTTP-200 empty dataset, invalid/non-JSON response and other transport errors;
- any token-like `aws-waf-token=` value is redacted from compact classification output;
- one shared **ephemeral** WAF token cache may be reused only inside the one recovery job and is deleted with raw data;
- same-attempt XAUUSD BID sanity window: `2026-06-01T00:00:00Z <= t < 2026-06-02T00:00:00Z`;
- sanity uses 1.51.1 `--retry-on-empty`, making valid HTTP-200 empty data explicitly different from WAF/HTTP failure;
- full acquisition remains the exact D-124 eight series and same Jun1–Oct9 fence;
- no benchmark code runs until all eight full files pass provider integrity;
- raw budget includes the sanity file; raw + WAF token are deleted before compact evidence upload.

The recovery execution guard admits the exact D-134 SHA and frozen science but deliberately has `RECOVERY_PROVIDER_ENABLED=False`. The machine-readable plan is `RECOVERY_AUTHORIZED_PREFLIGHT_PENDING`; provider/model/CI execution flags remain false.

The D-135 push triggers the existing synthetic exact-runtime workflow with additional **no-market-provider** recovery checks. It may access npm/Playwright distribution infrastructure to resolve the exact 1.51.1 package and install its matching Chromium, but it makes no Dukascopy market-data request.

If D-135 passes, a later owner-independent commit may enable the already-authorized single recovery job. No further owner approval is required. No rerun is authorized after the real recovery attempt begins.
