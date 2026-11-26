# D-127 — Implement Bounded 2026 Pipeline and Trigger Synthetic End-to-End Rehearsal

**STATUS AT COMMIT: PRODUCTION PIPELINE IMPLEMENTED; PROVIDER ATTEMPT NOT YET SPENT**

This milestone adds the production code surface for the exact D-124 package:
- strict eight-file/date/raw-size provider validator;
- bounded June1 cold-start Information Parity builder reusing accepted Stage2 causal transforms;
- frozen D-116 event-to-market join for exactly 250 eligible events / 343 candidate minutes;
- frozen GOLD/FULL L2 logistic 39-date LODO benchmark with paired 10,000-date bootstrap and preregistered advancement gate;
- one-attempt provider acquisition wrapper with raw deletion and compact manifests only;
- production provider workflow, **without its trigger file**;
- synthetic market generator and exact-runtime synthetic end-to-end workflow.

The D-127 push triggers only the **synthetic no-provider rehearsal**. It uses the real frozen teacher events and 155-feature manifest with deterministic fake prices, exercising the full causal layer, dataset join, preprocessing, model fitting, pooling, metrics and reporting before the one provider attempt is allowed.

No real 2026 provider rows are acquired by D-127. The production provider workflow can only run later when a separate one-time trigger file is committed after this rehearsal passes.
