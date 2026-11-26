# D-120 — 2026 Badar Source-Only Governance and Calendar Preflight

**Status: OWNER RIGHTS CONFIRMED / 17 OFF-CI TESTS PASS / DESIGN ADDENDUM RECORDED / NO EXECUTION AUTHORIZED**

Date: 2026-11-27. Parents D-088, D-099, D-116–D-119. Branch `research/information-parity-v1-stage3-preregistration`.

## Owner statement and what it does

The owner explicitly stated **"Yes I have"** in response to whether they already possess written permission or a data licence allowing automated Dukascopy historical-data acquisition for this project, and instructed the assistant not to create unnecessary blockers. Treat this as **owner-confirmed sufficient access** for *design planning*, without repeatedly asking for licences, certificates or reconfirmation. Do not expose credentials or licence text in GitHub. The owner has **not** rescinded the separate D-118 prohibition on acquisition/model fitting until the completed protocol receives final approval. D-088 is still closed.

## Reproducible work added

- `scripts/stage3b_2026_addendum.py` — fail-closed source window, owner-final-authorization gate, causal calendar publication checks, explicit bounded state initialization, ET/DST, and feature allowlist checks. **No network or model APIs**.
- `tests/test_stage3b_2026_addendum.py` — six additional synthetic no-provider tests, including unauthorized in-scope acquisition rejection and rejection of retroactive schedule evidence.
- Together with `tests/test_stage3b_2026_preflight.py`, **17/17 Python standard-library unit tests PASS** locally; `python -m compileall` passes. No CI triggered.
- Installed runtime inspection only, no fitting: available CPython **3.13.5**, scikit-learn **1.8.0**, SciPy **1.17.0**, joblib **1.5.3**, threadpoolctl **3.6.0**, NumPy **2.3.5**, pandas **2.2.3**. Exact designated CPython 3.12.14 / NumPy 2.5.3 / pandas 3.0.6 isolated runtime is **not present in the offline container**, so no false exact-env PASS is claimed. These versions are recorded, not used to produce model results. No runtime CI before authorization.
- Official public calendar documentation reviewed; `research/reference/information-parity-v1/stage3b-2026-macro-asof-evidence-v1.json` records **11 schedule-event examples**, **8 documented prior-schedule candidates** and **3 marked unverified/missing**; the remaining entire family/year schedule is **NOT certified**. No macros' actual/forecast/surprise data acquired.

## Causal historical calendar evidence

- Federal Reserve announcement on **2024-08-09** explicitly listed 2026 FOMC meetings and the standard 2 p.m. ET policy-statement time, including July 29 and September 16, 2026: https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm.
- Official BLS 2026 schedule monthly *Last Modified Date* labels: **July Feb 18**, **August Aug 12**, **September Feb 18**, **October Feb 18**, 2026. A post-event modification cannot certify what was known before August 4/7/12; unknown remains unknown: https://www.bls.gov/schedule/2026/.
- BEA's official schedule documents a general forward-publication practice, but does not certify all 2026 GDP **revisions** to the minute. DOL weekly claims date exceptions also need event-specific primary evidence. Both remain candidate missingness, not hindsight re-created.
- Even when a monthly page's last-modified date precedes an event, page revision/provenance must be recorded with a stable citation/version before the exact event is admitted as a true point-in-time value. The JSON manifest is a **source-evidence inventory, not a complete authorized normalized macro calendar**.
- Until a dated event proves as-of publication, macro feature state for that entry must be **unavailable**; cannot fill the missing event using later schedule or economic-release outcome. The bounded experiment may only report reduced available schedule coverage under a separately frozen coverage rule; no feature selection based on recognition results.

## June 1 warm-up: explicit no-expansion design resolution

The accepted Stage 2 code retains confirmed swings/FVGs indefinitely. No finite 35-day lookback can *prove* exact full-history structural continuity. The research proposal now includes a **bounded June 1 cold-start** design rather than silently acquiring May or earlier history.

- At `2026-06-01T00:00:00Z`, initialize all state from within the authorized bounded source window only; unknown pre-June swing/FVG history is not synthesized.
- Accumulate swings, FVGs, daily/weekly and rolling state **causally from June 1 onward**; preserve explicit missingness and original confirmations.
- Both GOLD and FULL use **the identical bounded market-state source**, so price-derived variables match row-for-row; report cold-start limitation plainly.
- The resulting bounded-state initialization is **not claimed equivalent to the full uninterrupted 2016–2021 Stage 2 representation**. This is a prospective implementation addendum **proposed for the future final approval**. No provider download to test it.
- Any desire to restore original pre-June active swings/FVGs requires a separately versioned longer date fence or verified prior-state snapshot; not an automatic scope expansion.

## Controls and remaining owner-independent work

Frozen: D-116 teacher SHA `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd`, source 39 dates/250 eligible events, 92 GOLD/155 FULL features, 39 LODO folds, 343 source minute candidates. New tests cannot authorise a download: there is no acquisition implementation in the addendum, and `market_request()` denies acquisition unless final authorization is explicitly passed; arbitrary calls cannot be treated as owner approval.

Remaining before a true execution-ready approval request: exact CPython3.12.14 runtime validation (do only in a permitted no-data local environment, CI only upon permission), complete source-specific feature-table schema dry run, formal acquisition/secret-retention wrapper, and full first-party event-calendar provenance or an explicitly low-coverage fail-closed macro policy. **Do these without requesting another owner decision** unless a revised data fence or genuinely new market entitlement is necessary.

**D-088 CLOSED. No 2026 provider data, model fitting, broker mutation, sealed 2022–2025 access, or CI executed.**
