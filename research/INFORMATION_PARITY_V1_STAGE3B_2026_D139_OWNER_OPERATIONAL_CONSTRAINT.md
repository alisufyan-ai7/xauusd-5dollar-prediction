# D-139 — Owner Operational Constraint: No Manual External Infrastructure Setup

STATUS: ACTIVE PROJECT CONSTRAINT

The owner states that project execution must not depend on the owner manually configuring AWS, cloud credentials, broker/demo accounts, external infrastructure, or other operational plumbing. Where a workflow is possible, the assistant should carry it end-to-end using available project/chat tools.

Interpretation:
- do not ask the owner to create/configure AWS IAM, OIDC, access keys, cloud buckets, CI secrets, broker/demo accounts, or similar infrastructure;
- do not ask the owner to paste credentials into chat;
- prefer credential-free/public/read-only sources and tooling that can be fully executed by the assistant;
- if a candidate path inherently requires a user-owned external identity that current tools cannot create/configure, mark it operationally infeasible and find another route;
- textual owner authorization for a materially new provider-access plan may still be required, but operational setup should not be delegated to the owner.

Consequence for D-138:
D-138 Requester-Pays S3 requires valid AWS credentials. Current project tools do not provide an authenticated AWS identity suitable for that bucket, and the owner will not configure one. D-138 is therefore PREREGISTERED_BUT_OPERATIONALLY_INFEASIBLE_UNDER_D139. No S3 LIST/HEAD/GET should be attempted.

Current access research:
- live browser inspection on 2026-11-27 found the Dukascopy Historical Data Export widget temporarily unavailable;
- the public widget did not visibly require login, so it remains a potential zero-setup route if restored;
- JForex historical access requires demo/live login and does not satisfy D-139 in its current form.

D-140 therefore explores the credential-free legacy public datafeed route.