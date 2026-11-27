# D-141 — D-140 Credential-Free Datafeed Decoder/Fence Structural Preflight

STATUS AT COMMIT: LOCAL STRUCTURAL PASS / PROVIDER DISABLED / EXACT PYTHON 3.12.14 CI REQUIRED

Implemented files and Git blob identities:
- scripts/decode_dukascopy_datafeed_m1.py — 310c5d2cb0fbc9e4f5407eb1f6b43b947ea94ef2
- scripts/stage3b_2026_public_datafeed_preflight.py — 02fd41dca1622a5eb5d8535a870052ed59ed246a
- tests/test_stage3b_2026_public_datafeed.py — d60644a17e3ef5cae472ce75371b5599d5bbee7e

Local deterministic run:
- Python 3.13.5
- provider requests: 0
- CI runs: 0
- tests: 8/8 PASS
- exact Git blob SHAs of the locally tested files match the blobs being committed.

Covered invariants:
1. pinned v1.46.4 M1 binary field order and EURUSD normalization;
2. frozen XAUUSD decimal factor 1000;
3. malformed LZMA/record-length rejection;
4. minute alignment and strict timestamp ordering;
5. OHLC invariant failure;
6. exact zero-based month URL construction;
7. hard symbol/side/date fences including sealed dates;
8. exact eight-request Jun1 sanity set;
9. exact 130-day / 1040 full opportunity / 1050 hard GET budget;
10. one-attempt / zero-retry policy;
11. provider execution remains disabled.

The local host does not provide Python 3.12.14, so D-141 does not claim exact-runtime completion. A deliberately small no-provider GitHub Actions check is included solely to run these stdlib tests under CPython 3.12.14. It performs no datafeed request and installs no market-data package.

No provider access is authorized by D-141. Stage 3B remains NOT TESTED.