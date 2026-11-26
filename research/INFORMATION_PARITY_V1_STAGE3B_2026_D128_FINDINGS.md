# D-128 — Synthetic Pipeline PASS and Production Trigger Guard Repair

**STATUS: SYNTHETIC END-TO-END PASS; REAL PROVIDER ATTEMPT STILL UNSPENT**

D-127 exact-runtime synthetic workflow:
- run: **45897637362**
- job: **140175383322**
- head: `2aa93137929853fcbab7ac101d262ef283deab44`
- conclusion: **SUCCESS**
- runtime: about one minute.

The rehearsal used the real frozen D-116 teacher file and exact 155-feature manifest but deterministic **fake** market prices. It validated:
- provider-like schema/date/raw-size guards;
- XAUUSD synchronization and synthetic DXY construction;
- bounded causal information layer;
- exactly **250 eligible source events / 343 candidate minutes / 39 dates**;
- zero-minute XAUUSD state age at source candidate times;
- macro fail-closed state = unavailable;
- all frozen LODO fitting, pooling, bootstrap and report paths.

The fake-data benchmark printed `NEGATIVE FOR FROZEN STAGE 3B HYPOTHESIS`; that value has **no scientific meaning** because prices were generated synthetic. Only pipeline integrity is inferred.

### Production workflow anomaly and correction

GitHub also created run **45897634530** for the newly added production workflow, but it had **zero jobs** and completed immediately; no runner, download command, model fit or provider request occurred. Therefore the D-124 one real provider attempt remains unspent.

The original production YAML used the `runner.temp` context at job-level `env`, which is not a safe workflow-parse surface. D-128 replaces it with a fixed workspace path and removes the brittle `GITHUB_RUN_NUMBER == 1` rule (run number 1 was already consumed by the zero-job validation failure).

Before any provider step, the production job now requires all of:
1. a commit message containing `[STAGE3B_PROVIDER_EXECUTE_D124]`;
2. an exact dedicated trigger file with the frozen D-124 scope and `attempt=1`;
3. `GITHUB_RUN_ATTEMPT == 1`;
4. exact runtime, authorization, unit and pipeline guards.

The actual provider trigger file is **still absent** in D-128. No provider access occurs from this decision.
