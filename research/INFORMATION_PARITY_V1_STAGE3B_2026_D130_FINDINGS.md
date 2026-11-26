# D-130 — Execute the Single D-124 Bounded Provider / Stage 3B Benchmark Attempt

**STATUS AT COMMIT: REAL PROVIDER ATTEMPT TRIGGERED — DO NOT RERUN**

Preconditions passed:
- D-124 final owner authorization commit `c99ad84e4b7254d074b96df7a5f4c371ccbe01c2`;
- D-126 exact runtime PASS;
- D-127 and D-128 synthetic exact-runtime end-to-end rehearsals PASS;
- D-129 production workflow parse validation run **45898223471** = **SKIPPED as designed** (valid YAML, no provider job).

D-130 replaces the non-authorizing placeholder with the exact trigger payload frozen in the production workflow and uses the required commit marker `[STAGE3B_PROVIDER_EXECUTE_D124]`.

This authorizes the workflow to spend the **one real provider attempt**:
- only Jun1 00:00 UTC through Oct9 00:00 UTC exclusive;
- only XAUUSD BID/ASK + six frozen FX BID M1 series;
- exact D-124 authorization and package hashes;
- raw <=350 MiB / normalized <=750 MiB;
- raw provider payload deleted before compact artifact upload;
- bounded June1 cold start and macro unavailable/fail-closed semantics;
- exact D-116 250-event teacher / 343 candidate-minute join;
- frozen GOLD/FULL 39-date LODO Stage 3B benchmark.

**Rerun is prohibited.** `GITHUB_RUN_ATTEMPT` must equal 1 before provider access. Stage4/5, shadow, sealed years and broker actions remain unauthorized.
