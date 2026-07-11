# ADR-0005: Neo4j runtime (local Community) and batched write path

- Status: Accepted
- Date: 2026-07-06

## Context

`NEO4J_URI` currently points at `neo4j+s://…databases.neo4j.io` — Neo4j **Aura**.
Aura's free tier caps at ~200k nodes / 400k relationships. Even the 1,000-block
ladder step in 2024 (~200 external txs/block ⇒ 200k+ transaction nodes alone,
before user nodes, internal txs, and edges) exceeds that; the 10,000 step is far
beyond it. Aura also adds a network round-trip per write.

Separately, the existing write path issues one `session.run` per node/edge
(`src/db/connection.py`). At millions of rows that is millions of round-trips —
the new bottleneck once BigQuery removes the acquisition bottleneck (ADR-0001).

## Decision

1. **Run Neo4j Community locally** (Docker or Neo4j Desktop) for all heavy
   loading and analysis. No node/relationship cap, no network latency, free; the
   M4 / 16 GB machine handles millions of nodes. `NEO4J_URI` → `bolt://localhost`.
   Aura is retired for the heavy runs (optionally kept for a small shareable demo
   of the original 100-block window).

2. **Batch all writes with parameterized `UNWIND`.** Group nodes/edges by type,
   send in batches of ~1–5k rows per transaction (e.g. `UNWIND $rows AS row
   MERGE …`). Keeps the MERGE-based idempotent schema and the existing Cypher
   unchanged; loads millions of rows in minutes.

3. **Create indexes/constraints before loading** (unique on `Block.number`,
   `Transaction.transactionhash`, `User.address`, and the composite
   `InternalTransaction(parenttransactionhash, sequence_id)`) so MERGE lookups
   are O(log n), not scans.

## Consequences

- The 10k ladder across eras becomes feasible on a laptop.
- `connection.py` gains batch methods; `pipeline.py` accumulates rows and flushes
  in batches instead of per-entity writes.
- Config/docs must document the local Docker setup and the `.env` change.
- Reproducibility: pin the Neo4j Community version (paper cites 2026.01.3).
