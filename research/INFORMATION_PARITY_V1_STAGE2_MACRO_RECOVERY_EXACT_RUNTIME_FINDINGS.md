# Information Parity V1 — Stage 2 Macro Recovery Exact-Runtime Findings

Status: **ACCEPTED**

Accepted run:
- workflow: `information-parity-stage2-preflight`
- run: **37472945799**
- head: `7e74193cba68591883621c70c4645b4ad85a425d`
- conclusion: **SUCCESS**
- started: 2026-10-06T13:42:36Z
- completed: 2026-10-06T13:43:39Z

Trigger discipline:
- the repository connection did not expose a workflow-dispatch mutation;
- the already-established isolated trigger-file mechanism was used;
- the trigger was restricted to `research/information-parity-v1-stage2-preflight` and `.github/information-parity-stage2-preflight-trigger`;
- exactly one run was launched;
- the workflow was restored to manual-only and the trigger marker removed immediately after the run started.

Frozen runtime observed:
- Node v22.23.3
- npm 10.9.9
- CPython 3.12.14
- numpy 2.5.3
- pandas 3.0.6
- requests 2.34.2
- beautifulsoup4 4.15.0
- all other packages matched `requirements/information-parity-stage2.lock.txt`.

Terminal gates:
- `INFORMATION_PARITY_STAGE2_REPO_CONTRACT_PASS`
- `INFORMATION_PARITY_STAGE2_ENVIRONMENT_PASS`
- `INFORMATION_PARITY_STAGE2_FOUNDATION_PASS`
- `INFORMATION_PARITY_STAGE2_OFFLINE_PREFLIGHT_PASS`
- `INFORMATION_PARITY_STAGE2_FULL_TRAIN_PREFLIGHT_PASS`
- `INFORMATION_PARITY_STAGE2_PREFLIGHT_ALL_PASS`

The passing suite includes the D-083/D-084 macro-recovery regressions:
- Federal Reserve 2021 legacy-index failure with first-party 2021 FOMC press-index fallback;
- eight deterministic FOMC statement identities;
- BEA national-GDP comma/colon/parenthetical title variants;
- exclusion of GDP-by-state and GDP-by-industry titles;
- both admitted BEA embargo punctuation forms;
- workflow contract requiring the macro-only gate to avoid market acquisition;
- full-TRAIN macro readiness gate preceding expensive market acquisition.

GitHub emitted the same hosted-runner warning seen previously: some pinned Actions revisions target deprecated Node 20 internally and are forced by GitHub to Node 24. The project runtime used by the deterministic suite remained the configured Node 22.23.3 and every gate passed.

## Decision

The exact-runtime deterministic prerequisite for the D-083 macro recovery is accepted.

The next authorized action is exactly one **2016-2021 macro-only network confirmation** using the new `macro-preflight` mode.

This does not authorize a new full-TRAIN market acquisition yet. Another full same-snapshot build becomes authorized only if the macro-only confirmation reports complete admitted-family coverage for every TRAIN year.

No 2022-2025 XAUUSD data were accessed by this deterministic run.
No model training, P&L logic or broker mutation is authorized.
