# Information Parity V1 — Stage 2 Frozen Runtime Environment

Status: **FROZEN FROM ACCEPTED SMOKE RUNTIME**

Accepted smoke:
- run 37192128583
- head 273b93cc882ac954fcd6bc21b28155ef4ab5aa0f

## Runtime

Python:
- CPython 3.12.14

Node:
- Node v22.23.3
- npm 10.9.9

Dukascopy downloader:
- `dukascopy-node@1.50.0`

## Python package lock

Canonical lock:
`requirements/information-parity-stage2.lock.txt`

Exact versions observed in the accepted smoke:
- beautifulsoup4 4.15.0
- certifi 2026.7.22
- charset-normalizer 3.5.2
- idna 3.20
- numpy 2.5.3
- pandas 3.0.6
- python-dateutil 2.9.0.post0
- requests 2.34.2
- six 1.17.0
- soupsieve 2.10
- typing-extensions 4.16.0
- urllib3 2.8.0

## Why frozen

Recent Stage 2 failures exposed that runtime/library assumptions can become integration bugs, especially around pandas datetime resolution.

The full Stage 2 build must therefore run under the same pinned runtime family used by the accepted smoke.

## Preflight contract

Before any Stage 2 CI or provider-data run is intentionally triggered:

1. install the pinned Python lock;
2. use Python 3.12.14;
3. use Node 22.23.3 / npm 10.9.9 for the downloader layer;
4. run:
   `bash scripts/run_information_parity_stage2_preflight.sh`
5. do not trigger CI unless the offline preflight passes.

The preflight itself uses no network and no provider data.

## Change control

A runtime/package change is a material Stage 2 implementation change.

If any pinned runtime dependency must change:
- update this document and the lock file together;
- rerun the offline deterministic preflight first;
- only then run one intentional CI validation;
- record the reason for the runtime change in the decision log.

No dependency upgrades are allowed merely because newer versions exist.
