# New Chat Handoff Instructions

When continuing this project in a new ChatGPT chat:

1. Work only from this repository, the new project's current chat, and fresh public research/data.
2. Read these files before changing the research design:
   - PROJECT_CONTEXT_POLICY.md
   - research/PROJECT_CONTINUITY.md
   - research/DECISION_LOG.md
   - research/EXP-001_PREREGISTRATION.md
   - research/EXP-001_LABELING_SPEC.md
   - research/EXP-001_ACQUISITION_RANGE.md
   - research/EXP-001_DATASET_LOCK.md
   - research/EXP-001_PARTITIONS.md
   - research/EXP-001_FULL_HISTORY_LABELING.md
   - research/EXP-001_FEATURES_BASELINES.md
   - research/EXPERT_TRADER_OBSERVATION_MODEL.md
3. Inspect the current branch and CI state before assuming the latest stage passed.
4. Keep 2025 FINAL_OOS sealed unless the project explicitly reaches the registered final-OOS gate.
5. Never silently alter frozen labels, partitions, target/adverse distances, horizon, or dataset hashes.
6. Record any new material decision in research/DECISION_LOG.md.
7. Update research/PROJECT_CONTINUITY.md whenever the current project state or immediate next step changes.

The repository, not chat memory, is the durable source of truth.
