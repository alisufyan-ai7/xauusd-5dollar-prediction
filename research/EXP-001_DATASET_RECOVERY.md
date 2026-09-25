# EXP-001 Locked Dataset Recovery and Durable Asset Plan

Status: ACTIVE

## Problem

The admitted dataset is pinned by yearly SHA-256 hashes, but the public source can later return a different historical snapshot for the same yearly request. This was observed for 2020 transiently and for 2017 repeatedly.

Therefore the project must not depend indefinitely on a fresh one-shot public download to reproduce the admitted research dataset.

## Recovery method

For a mismatching year:

1. download the year in independent monthly chunks;
2. validate every monthly chunk;
3. concatenate the chunks deterministically with one CSV header;
4. validate the reconstructed yearly CSV;
5. compare row count and SHA-256 against the immutable dataset lock;
6. admit the reconstructed bytes only if the exact locked hash matches.

This is a reconstruction attempt, not permission to alter the dataset lock.

## Durable asset objective

Once every locked yearly file is available again, persist compressed copies as immutable project research assets so downstream research consumes the admitted bytes directly.

Fresh Dukascopy downloads then become external reproducibility/integrity checks rather than prerequisites for model research.

## Fail-closed rule

If chunked reconstruction cannot reproduce a locked hash:

- do not silently replace the locked dataset;
- do not build features/models from the changed snapshot;
- record the mismatch and investigate the missing intervals separately.
