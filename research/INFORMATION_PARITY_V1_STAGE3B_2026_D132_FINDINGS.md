# D-132 — Corrected Single Real D-124 Provider / Stage 3B Benchmark Attempt

**STATUS AT COMMIT: SINGLE REAL PROVIDER ACQUISITION ATTEMPT TRIGGERED — NO RERUN**

Final pre-provider evidence:
- D-126 exact runtime PASS;
- D-127 synthetic end-to-end PASS;
- D-128 synthetic revalidation PASS;
- D-129 production workflow parse validation clean/skipped;
- D-130 failed before checkout/provider access;
- D-131 corrected checkout-before-guard regression run **45898582347** = **SUCCESS**.

D-132 replaces the previous trigger contents with the exact payload expected by the validated workflow and uses commit marker `[STAGE3B_PROVIDER_EXECUTE_D124]`.

This is the one real provider acquisition attempt under D-124. It may:
- download only the eight frozen M1 series for `2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z`;
- validate raw bytes/date/symbol schema under the frozen 350 MiB cap;
- derive synchronized XAUUSD + synthetic DXY and bounded Information Parity state;
- delete raw provider payloads before compact artifact upload;
- join only the frozen D-116 teacher corpus;
- run only the frozen GOLD/FULL 39-date LODO Stage 3B benchmark.

**No rerun is permitted regardless of scientific result or runtime outcome.** Stage4/5, shadow, sealed years and broker actions remain blocked.
