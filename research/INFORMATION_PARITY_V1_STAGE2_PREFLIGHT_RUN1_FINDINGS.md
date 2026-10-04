# Information Parity V1 — Stage 2 Preflight Run 1 Findings

Status: **HARNESS FAILURE BEFORE DETERMINISTIC SUITE**

Run:
- workflow: `information-parity-stage2-preflight`
- run: **37196172995**
- head: `031cafbeab86b9d700fd41220335fad9079d13d7`
- conclusion: FAILURE

## What passed before failure

The isolated CI successfully established the pinned environment:
- Node v22.23.3;
- npm 10.9.9;
- CPython 3.12.14;
- exact Python lock installed successfully.

Pinned GitHub Actions revisions also loaded successfully.

## Exact failure

The job failed immediately when executing:

`scripts/check_information_parity_stage2_repo_contract.py`

because two intended newline-containing string literals were written into the source as literal physical newlines inside a quoted Python string.

Result:

`SyntaxError: unterminated string literal`

The deterministic Stage 2 preflight suite itself did **not** run.

Therefore this run provides no negative evidence about:
- BID/ASK synchronization;
- synthetic DXY;
- timeframe construction;
- session/DST logic;
- macro state;
- structural causality;
- leakage validation.

## Root cause

This was a preflight-harness construction defect.

The wrapper also executed the repository-contract checker before the global `py_compile` step, which meant a syntax defect in the checker itself was discovered during execution rather than at the explicit compile gate.

## Fix

1. newline checks were rewritten using escaped `"\\n ..."` string literals;
2. the trigger-policy check now accepts either:
   - manual-only workflow; or
   - the explicitly scoped temporary trigger on the isolated preflight branch and single trigger file;
3. the preflight runner now compiles the entire Stage 2/preflight Python surface **before** executing any checker or test.

## Off-CI validation before another run

Before authorizing another CI confirmation:
- the corrected repository-contract checker was syntax-compiled successfully outside GitHub Actions;
- the deterministic preflight test file was syntax-compiled successfully outside GitHub Actions;
- the shell preflight runner passed `bash -n`;
- provider-data Stage 2 scripts remain unchanged from the already accepted real-data smoke / subsequent green foundation checks.

The remaining purpose of CI is now narrow and legitimate:
confirm the complete deterministic suite under the exact pinned accepted-smoke runtime.

No provider-data smoke/full run is authorized by this finding.
No model work is authorized.
2022-2025 XAUUSD remain sealed.
