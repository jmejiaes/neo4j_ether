# ADR-0006: Unify the external-transaction node label

- Status: Accepted
- Date: 2026-07-06

## Context

The paper's Cypher and model use the node label `ExternalTransaction`
(e.g. `MATCH (tx:ExternalTransaction)`), but the code creates and queries the
label `:Transaction` (`src/db/schema_queries.py`, `analytics_queries.py`).
Internal transactions use `:InternalTransaction` in both. This mismatch means
the paper's listed queries don't run against the actual database as built.

## Decision

Standardize on **`ExternalTransaction`** for external-transaction nodes, matching
the paper's model (external vs internal is the model's central distinction) and
the queries already printed in the manuscript. Update `schema_queries.py`,
`analytics_queries.py`, and `connection.py` accordingly. Keep
`:InternalTransaction` as-is.

Property names stay: `value` for external, `amount` for internal.

## Consequences

- Paper's printed Cypher becomes copy-paste runnable — a correctness fix reviewers
  could otherwise catch.
- Glossary updated to drop the "label mismatch" caveat once code is changed.
- One-time find/replace across the db layer; no data-model change.
