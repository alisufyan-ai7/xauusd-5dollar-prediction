# D-129 — Repair Production Workflow YAML and Validate It Without Provider Execution

**STATUS AT COMMIT: PRODUCTION YAML REPAIRED; NON-AUTHORIZING WORKFLOW VALIDATION TRIGGERED**

D-128 synthetic revalidation:
- run **45897995539**
- job **140176557797**
- conclusion **SUCCESS**
- no provider market data.

The production workflow's previous zero-job records were caused by a malformed YAML block: an embedded shell heredoc expanded with unindented content. No production job was created in either record and no provider command ran.

D-129 repairs that block using an indentation-safe `printf`/compare guard and retains all pre-provider controls:
- D-124 execution commit marker required at job level;
- exact trigger-file contents required;
- `GITHUB_RUN_ATTEMPT=1`;
- exact runtime and all deterministic tests before provider access;
- fixed bounded date/symbol/budget authorization.

To validate GitHub workflow parsing without spending the provider attempt, D-129 creates `.github/stage3b-2026-authorized-trigger` with **validation-only non-authorizing content** and uses a commit message that intentionally lacks the execution marker. A valid workflow should therefore parse and produce a skipped provider job. No acquisition is authorized by this placeholder.

The actual provider trigger will replace this file only in a later commit whose message contains `[STAGE3B_PROVIDER_EXECUTE_D124]` and whose file content exactly matches the frozen D-130 execution payload.
