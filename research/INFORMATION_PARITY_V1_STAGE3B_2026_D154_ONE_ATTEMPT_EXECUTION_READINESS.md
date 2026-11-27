# D-154 — D-152 One-Time Execution Readiness, Before Any FREESERV Call

Status: **ACCEPTED / PROVIDER NOT YET ACCESSED / EXECUTION TRIGGER ABSENT**

Owner authorization: D-152, commit `ce9e4a1eef48df2e7f1ee8775afe74edc10cbe71`.

D-153 hardened preflight evidence:
- run `45975306543`, job `140425441301`
- head commit `419db1e5aab0fa171be29e04c585daa43326afeb`
- CPython 3.12.14
- explicit module compilation: PASS
- integration shell `bash -n`: PASS
- deterministic/mock tests: **18/18 PASS**
- provider requests: **0**
- workflow: SUCCESS

Transport hardening before authorization spend:
- direct HTTPS transport using `urllib.request.ProxyHandler({})` so system proxy environment cannot redirect the request;
- custom `NoRedirectHandler` returns no redirect request, refusing 3xx on same or different host;
- one opener call per transport request, no automatic retry;
- bounded response reads and cumulative raw budget;
- normalized CSV byte budget checked after every page write;
- no alternate host, mirror, VPN or source.

New separate execution workflow created:
`.github/workflows/stage3b-2026-freeserv-d148-execution.yml`.

Its job requires:
1. one exact D-155 trigger-file path change;
2. exact unique commit-message marker `[STAGE3B_D148_D152_ONE_ATTEMPT]`;
3. run attempt number 1;
4. exact trigger content including D-152 authorization commit SHA, representation, eight sanity requests, page/request caps and retry ceiling;
5. CPython 3.12.14, frozen Stage 3B dependency lock and deterministic tests before provider access;
6. exact authorization SHA allowlist and provider-enabled checks in the final executor;
7. sanity-first acquisition and only then the unchanged D-124 dataset/model pipeline;
8. unconditional compact evidence hashing, raw/derived cleanup and artifact upload.

No execution trigger exists at time of this record. The enabled/trigger commit must be made **once only** and must not be rerun, regardless of network/provider/scientific outcome.

All 2022-2025 sealed, 2026-10-09 through 2026-11-30 quarantined, December shadow and broker restrictions unchanged. Stage 3B remains **NOT TESTED** pending the first authorized provider attempt.
