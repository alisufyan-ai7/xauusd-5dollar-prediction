# EXP-001 Feature/Baseline Execution

The executable stage processes only calendar years 2016 through 2024.

2025 FINAL_OOS is not opened, joined, summarized, or supplied to the baseline program.

For each admitted locked yearly raw chunk, the pipeline:

1. constructs timestamp-safe M1 features;
2. joins them to that year's deterministic partitioned labels;
3. excludes incomplete feature/outcome coverage and partition-boundary-ineligible rows;
4. computes unconditional and coarse regime baselines;
5. derives volatility tertile thresholds from TRAIN only;
6. applies those fixed TRAIN-derived thresholds to VALIDATION and DEVELOPMENT_TEST.

The resulting report is descriptive research evidence. It does not authorize trading or set an entry threshold.
