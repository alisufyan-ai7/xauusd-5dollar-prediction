# EXP-001 Dataset Lock

The first successful full-history acquisition run is the admitted historical dataset reference.

- admitted GitHub Actions run: 36029810579
- total rows: 3,542,055
- years: 2016-2025
- lock file: `research/EXP-001_DATASET_LOCK.json`

A later independent run reproduced 9 of 10 yearly chunks exactly, but its 2020 chunk differed by 120 rows and SHA-256. Because the public downloader can apparently return an incomplete year without failing validation, raw validation alone is insufficient for reproducibility.

Therefore:

1. every admitted historical chunk is pinned by row count and SHA-256;
2. re-downloads used for research must match the locked chunk exactly;
3. a mismatch is a data-acquisition failure, not a new admitted dataset;
4. no model/features may be built from a mismatching re-download;
5. targeted retries may be used to reproduce the locked public data.
