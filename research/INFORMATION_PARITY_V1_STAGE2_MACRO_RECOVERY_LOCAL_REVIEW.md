# Information Parity V1 — Stage 2 Macro Recovery Off-CI Review

Status: **PASS FOR CHANGED SURFACE; EXACT-RUNTIME FULL PREFLIGHT REQUIRED NEXT**

Decision:
D-084

Branch:
`research/information-parity-v1-stage2-preflight`

Reviewed implementation blobs:
- `scripts/acquire_macro_schedule_stage2.py`: `3bb77fd78d77a569fc1a0a4d520e461fea03aa09`
- `tests/test_information_parity_stage2_preflight.py`: `358ba27b429e8d25acddd8bb496e03cf8395edab`
- `.github/workflows/information-parity-stage2.yml`: `d0417bb63cd38abb3b7a8a2da81b10afbcdebb2e`
- `scripts/check_information_parity_stage2_repo_contract.py`: `09df093ec6683d8877c560ab1ac79675147fb8ec`

## Static review

The changed source was reread from GitHub after commit.

Verified:
- 2021 FOMC falls back from the obsolete legacy historical-year URL only to the Federal Reserve first-party 2021 FOMC press-release index;
- admitted statement links still require `monetaryYYYYMMDDa.htm` for the requested year;
- exact release time still comes from the first-party statement page;
- BEA national-GDP admission accepts only the same series name followed, after optional whitespace, by comma, colon or opening parenthesis;
- BEA by-state/by-county/by-industry product titles remain excluded by that predicate;
- embargo parsing now accepts both `A.M. EDT` and `A.M., EDT` punctuation;
- the macro-only workflow job cannot call `acquire_information_parity_stage2.sh`;
- the full-TRAIN job's macro gate now precedes XAUUSD/FX market acquisition;
- provider workflow remains manual-only;
- no 2022-2025 XAUUSD path was added;
- no macro outcome fields, model fitting, P&L or broker action was added.

## Deterministic changed-surface execution

A deterministic off-CI regression was executed in the available local tool runtime.

Local runtime:
- Python 3.13.5
- pandas 2.2.3
- numpy 2.3.5
- beautifulsoup4 4.14.3
- requests 2.32.5

Result:
`TARGETED_MACRO_RECOVERY_OFF_CI_PASS 8 []`

The regression exercised:
- legacy 2021 FOMC index failure followed by first-party press-index fallback;
- exactly eight synthetic 2021 statement identities;
- comma, colon and parenthetical BEA national-GDP title admission;
- rejection of GDP-by-state and GDP-by-industry titles;
- old BEA embargo syntax;
- comma-before-timezone BEA embargo syntax.

The first attempted predicate test failed because the real parenthetical title contains whitespace before `(`. The recovery addendum was corrected before implementation to state "after optional whitespace"; the corrected deterministic regression then passed.

## Environment limitation

This off-CI runtime is not the frozen Stage 2 runtime and therefore is not exact-runtime acceptance. The complete repository preflight was already accepted at D-082 before this macro change; because the changed surface is now covered by a deterministic local regression and exact-source static review, one full exact-runtime deterministic preflight is justified next.

No provider-data workflow is authorized by this review alone.

## Next gate

Run one exact-runtime `information-parity-stage2-preflight` confirmation on the current branch.

Only if it passes may the D-083 macro-only 2016-2021 network confirmation be triggered.

2022-2025 XAUUSD remain sealed.
