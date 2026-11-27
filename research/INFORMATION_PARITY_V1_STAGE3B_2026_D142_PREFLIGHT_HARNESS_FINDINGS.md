# D-142 — Diagnose D-141 CI Failure and Patch Harness Only

Run 45953090143 / job 140353234366:
- CPython 3.12.14 setup: PASS
- py_compile of decoder, guard and tests: PASS
- D-140 unit tests: 8/8 PASS
- provider requests: 0
- failure occurred only in the workflow's post-test static-plan loader.

Root cause:
The ad-hoc importlib loader executed stage3b_2026_public_datafeed_preflight.py without adding the module to sys.modules. Python dataclasses consult sys.modules during class processing, so the loader raised AttributeError after the real tests had already passed.

Patch:
- change workflow harness to a normal module import via sys.path;
- no decoder changes;
- no guard changes;
- no test changes;
- no scientific-scope changes;
- no provider access.

A single follow-up exact-runtime no-provider run is justified specifically to verify the corrected harness. This is not a blind CI retry.