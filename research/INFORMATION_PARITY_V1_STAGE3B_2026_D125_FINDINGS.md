# D-125 — Admit D-124 Authorization and Trigger Exact Runtime Preflight

**STATUS AT COMMIT: D-124 SHA ADMITTED; TARGETED NO-PROVIDER EXACT-RUNTIME CI TRIGGERED**

Owner authorization commit: `c99ad84e4b7254d074b96df7a5f4c371ccbe01c2`.

The exact authorization SHA is now the sole admitted execution token. The acquisition plan is FINAL_APPROVED for the D-124 scope, but provider execution remains ordered after this exact-runtime preflight. The new workflow is path-isolated and performs **no market download and no model fitting**. It checks CPython 3.12.14, the complete frozen Python lock, authorization/manifest hashes, and all deterministic Stage 3B guard tests.

This CI is justified because the available local Python 3.13.5 runtime cannot certify the preregistered Python 3.12.14 environment. No 2022–2025, quarantine/shadow, or broker scope changes.
