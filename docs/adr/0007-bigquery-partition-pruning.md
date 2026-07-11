# ADR-0007: Prune BigQuery partitions by block_timestamp

- Status: Accepted
- Date: 2026-07-06

## Context

The `bigquery-public-data.crypto_ethereum` tables are partitioned by DAY on their
timestamp column (`blocks.timestamp`, `transactions.block_timestamp`,
`traces.block_timestamp`, `contracts.block_timestamp`) — **not** by block number.

The first cut of `ingestion/bigquery.py` filtered only on `block_number`, so every
query scanned the entire table. Measured via dry-run for a 100-block window:

| table        | filter by block_number only | + block_timestamp bounds |
|--------------|------------------------------|--------------------------|
| transactions | 599.6 GB                     | 0.186 GB (3,230× less)   |
| traces       | 2,947.8 GB (2.9 TB)          | 1.294 GB (2,278× less)   |

A single unpruned `traces` query exceeds the 1 TB/month free tier. This exhausted
the sandbox quota on the first real load attempt (403 `quotaExceeded`,
`unbilled.analysis`).

## Decision

Derive the window's block-timestamp bounds once from the small `blocks` scan
(`block_time_bounds`), then inject them as **literal** `block_timestamp BETWEEN …`
filters on the transactions/traces/contracts queries so BigQuery prunes to the ~1–2
relevant daily partitions.

- Literals (not query parameters) are used for the timestamp bounds, because
  parameterized values do not reliably trigger partition pruning. The literals are
  BigQuery-formatted timestamps derived from `blocks`, so there is no injection risk.
- A transaction/trace's `block_timestamp` equals its block's timestamp, so the
  bounds are exact for the window — no padding needed. `block_number BETWEEN` is
  kept as the precise row filter; the timestamp filter only prunes partitions.
- `contracts` is pruned to partitions `<= ts1` (it is a ~60M-row table, so a few GB
  even at the upper bound — acceptable and inherently far smaller than txs/traces).
- `dry_run_bytes()` added so pruning can be verified for free (no quota use) before
  any real load.

## Consequences

- A 100-block window drops from ~3.5 TB to ~1.5 GB scanned; a 10k-block era is a
  few GB. The full multi-era ladder fits well within 1 TB/month.
- `fetch_transactions/_internal_transactions/_contract_addresses` now take `ts0,
  ts1` args; the pipeline computes them up front.
- Operational note: the sandbox project whose free quota was exhausted by the
  unpruned attempt is blocked until monthly reset or until billing is enabled.
  Pruned queries make ongoing cost effectively $0 within the free tier.
