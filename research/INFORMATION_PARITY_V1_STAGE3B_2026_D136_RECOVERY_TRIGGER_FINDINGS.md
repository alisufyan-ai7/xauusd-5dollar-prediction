# D-136 — D-135 PASS; Enable and Trigger the Single D-134 Transport-Recovery Attempt

**STATUS AT COMMIT: D-135 PREFLIGHT PASS / SINGLE RECOVERY PROVIDER ATTEMPT TRIGGERED / NO RERUN**

D-135 exact-runtime no-market-provider evidence:
- workflow run: **45901246019**
- job: **140187267884**
- head: `dc869b2b4ca1fae4b9ec5d516243a3a6a1bbb52a`
- conclusion: **SUCCESS**
- Node: **22.23.3**
- npm: **10.9.9**
- CPython: **3.12.14**
- pinned Python lock: PASS
- `dukascopy-node 1.51.1` CLI/WAF flags: PASS
- matching browser install: **Chrome for Testing 156.0.8078.4 / Playwright chromium v1248**
- deterministic tests: **30/30 PASS**
- synthetic real-teacher/fake-market pipeline: PASS
- market-provider requests in D-135: **none**

D-136 changes only the execution readiness state. The exact D-134 SHA remains the sole recovery authorization; transport remains 1.51.1 and all D-124 science remains frozen.

The one-time recovery workflow is bound to:
- exact trigger file `.github/stage3b-2026-transport-recovery-trigger`;
- commit marker `[STAGE3B_PROVIDER_RECOVERY_D134]`;
- `GITHUB_RUN_ATTEMPT=1`;
- D-135 preflight run ID **45901246019**;
- one recovery attempt only, no rerun.

Recovery sequence:
1. checkout and exact trigger guard;
2. exact Node/Python + package/browser setup;
3. all no-provider guards/tests;
4. same-attempt XAUUSD BID Jun1→Jun2 sanity request with 1.51.1 diagnostics;
5. only if sanity passes, full unchanged eight-series Jun1→Oct9 acquisition;
6. all eight raw files must validate before any teacher join/model fit;
7. frozen dataset and GOLD/FULL 39-date LODO benchmark;
8. raw/derived/WAF state removed before compact artifact upload.

No further owner approval is required. **Do not rerun this recovery workflow under any outcome.**
