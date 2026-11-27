# D-143 — D-140 Exact-Runtime No-Provider Preflight Accepted

STATUS: PASS / PROVIDER STILL DISABLED / AWAITING TEXT AUTHORIZATION

Accepted exact-runtime run:
- workflow run: 45953279060
- job: 140353837712
- head: b71f5be55cc34b0d7577b5de0651f9154964acff
- CPython: 3.12.14
- compile: PASS
- deterministic D-140 tests: 8/8 PASS
- static plan assertions: PASS
- provider requests: 0
- conclusion: SUCCESS

Frozen implementation blobs:
- decoder: 310c5d2cb0fbc9e4f5407eb1f6b43b947ea94ef2
- guard: 02fd41dca1622a5eb5d8535a870052ed59ed246a
- tests: d60644a17e3ef5cae472ce75371b5599d5bbee7e

Verified static plan:
- source representation: DUKASCOPY_PUBLIC_DATAFEED_DIRECT_M1_V1
- date fence: 2026-06-01 through 2026-10-09 exclusive
- logical series: 8
- calendar dates: 130
- sanity GETs: 8
- full GET opportunities: 1040
- hard GET cap: 1050
- raw cap: 350 MiB
- normalized cap: 750 MiB
- max attempts: 1
- retries after provider failure: 0
- provider enabled: false

D-142's earlier CI failure was harness-only; the actual unit tests had already passed. The corrected harness now passes completely.

No AWS, account, credential, browser profile, payment setup, or owner-operated infrastructure is required by D-140.

Only one governance step remains before a provider request: explicit owner text authorization of the versioned D-140 attempt. That authorization does not require any external setup. Stage 3B remains NOT TESTED until valid provider data are acquired and the frozen benchmark actually runs.