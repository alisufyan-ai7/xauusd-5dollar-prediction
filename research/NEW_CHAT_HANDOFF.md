# New Chat Handoff — Chat 05 -> Chat 06

GitHub source of truth: branch `research/information-parity-v1-stage3-preregistration`. Fetch HEAD fresh before acting.

D-139 no-manual-setup constraint remains active. Do not ask the owner to configure AWS/accounts/credentials/infrastructure.

D-144 authorized exactly one D-140 credential-free direct-M1 attempt. D-145 exact-runtime no-provider preflight passed: run 45962942690 / job 140384800318, Python 3.12.14, 14/14 tests PASS, zero provider requests.

D-146 consumed the single D-144 attempt: run 45963138729 / job 140385418030. The first XAUUSD BID Jun1 sanity connection to datafeed.dukascopy.com was reset by the peer during TLS before any HTTP response. No retry; no valid sanity object; requests 2-8 not made; full acquisition/model benchmark skipped.

Artifact 15181796258, digest sha256:28979e29c96c0f6682ec7f4be1aecf41de63b087e9fb6b292a54430f3cd1df05. Stage3B remains NOT TESTED.

D-147 fail-closes D140: provider disabled, executable allowlist empty, one-time trigger removed. Never rerun D132, D136 or D146.

Next owner-independent action: research/document another assistant-operable read-only access path without making a market-data request. Any future provider execution requires a new explicit owner authorization. Keep D124 science and all sealed/quarantine/shadow/broker restrictions unchanged.
