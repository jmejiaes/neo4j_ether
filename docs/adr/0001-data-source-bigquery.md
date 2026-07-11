# ADR-0001: Use BigQuery as the primary data source for ingestion

- Status: Accepted
- Date: 2026-07-06

## Context

The original pipeline (`src/ingestion/etherscan.py`) collects all data from the
Etherscan API. For every transaction it fetches sender and receiver account info
via two calls each (`eth_getCode` + `balance`), so a single block costs on the
order of hundreds of API calls. The paper reports an average of **~4 minutes to
load one block**, dominated by Etherscan rate limits — not by Neo4j, whose
queries run in <1s even at 100 blocks.

At 4 min/block, 1,000 blocks ≈ 66 hours, and the paper's stated main limitation
is that "100 blocks constitute a relatively small sample." The goal of this work
is to scale to ≥1,000 blocks across **several sections (eras)** of the chain, so
the acquisition bottleneck must be removed.

## Decision

Replace Etherscan bulk extraction with Google BigQuery's public dataset
`bigquery-public-data.crypto_ethereum` as the primary source. It provides
`blocks`, `transactions`, and `traces` (internal transactions), and contract
detection (via the `contracts` table / trace types), returning a full block
range in seconds per era at negligible cost (1 TB/month free tier). The user has
BigQuery access.

We are explicitly **not** bound to reproduce the paper's exact acquisition method
— correctness and scale take priority over methodological continuity.

## Consequences

- 1,000+ blocks × multiple eras becomes feasible (seconds–minutes, not days).
- Neo4j writes must be batched (UNWIND) to match the faster inflow — the
  per-row-round-trip write path becomes the next bottleneck (see backlog).
- Methodology section of the paper must be rewritten to describe BigQuery
  extraction instead of Etherscan.
- Current-balance is not available from BigQuery (see ADR-0002).
- Etherscan code (`src/ingestion/etherscan.py`) is retired or kept only as a
  reference/fallback.
