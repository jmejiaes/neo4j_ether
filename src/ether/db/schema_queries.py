"""Write-side Cypher.

All bulk writers take a `$rows` list and `UNWIND` it (ADR-0005) — one round-trip
per batch instead of per entity, which is what makes 1k–10k-block loads feasible.
MERGE is used throughout for idempotency (safe to re-run).

External transactions use the label `ExternalTransaction` (ADR-0006), matching the
paper's model and its printed Cypher. Internal transactions use `InternalTransaction`.
No `balance` (ADR-0002) and no block reward — both were unused by every query.
"""


class SchemaQueries:

    # --- constraints / indexes (run once before loading) -------------------
    # Single-property uniqueness is supported in Community Edition. Composite
    # node keys are Enterprise-only, so InternalTransaction gets a composite
    # INDEX (still makes its MERGE lookups O(log n)).

    @staticmethod
    def constraint_queries() -> list[str]:
        return [
            "CREATE CONSTRAINT block_number IF NOT EXISTS "
            "FOR (b:Block) REQUIRE b.number IS UNIQUE",
            "CREATE CONSTRAINT ext_tx_hash IF NOT EXISTS "
            "FOR (t:ExternalTransaction) REQUIRE t.transactionhash IS UNIQUE",
            "CREATE CONSTRAINT user_address IF NOT EXISTS "
            "FOR (u:User) REQUIRE u.address IS UNIQUE",
            "CREATE INDEX internal_tx_key IF NOT EXISTS "
            "FOR (it:InternalTransaction) ON (it.parenttransactionhash, it.sequence_id)",
        ]

    @staticmethod
    def clear_database_queries():
        # Two-phase batched deletion for multi-million-element graphs. A single
        # `MATCH (n) DETACH DELETE n` OOMs the heap; even batched DETACH DELETE
        # cascades huge per-node relationship deletes for hub accounts (WETH has
        # ~300k edges). Deleting relationships first in small batches, then the now
        # edge-free nodes, keeps every inner transaction small. Each statement runs
        # in an auto-commit transaction (required by CALL { } IN TRANSACTIONS).
        return [
            "MATCH ()-[r]->() CALL (r) { DELETE r } IN TRANSACTIONS OF 25000 ROWS",
            "MATCH (n) CALL (n) { DELETE n } IN TRANSACTIONS OF 25000 ROWS",
        ]

    # --- node writers ------------------------------------------------------

    @staticmethod
    def create_blocks_query():
        return (
            "UNWIND $rows AS r "
            "MERGE (b:Block {number: r.number}) "
            "SET b.time = r.time"
        )

    @staticmethod
    def create_users_query():
        return (
            "UNWIND $rows AS r "
            "MERGE (u:User {address: r.address}) "
            "SET u.iscontract = r.iscontract"
        )

    @staticmethod
    def create_external_transactions_query():
        return (
            "UNWIND $rows AS r "
            "MERGE (t:ExternalTransaction {transactionhash: r.transactionhash}) "
            "SET t.blocknumber = r.blocknumber, "
            "    t.value = r.value, "
            "    t.isinternaltransaction = false"
        )

    @staticmethod
    def create_internal_transactions_query():
        return (
            "UNWIND $rows AS r "
            "MERGE (parent:ExternalTransaction {transactionhash: r.parenttransactionhash}) "
            "MERGE (it:InternalTransaction {parenttransactionhash: r.parenttransactionhash, "
            "                               sequence_id: r.sequence_id}) "
            "SET it.amount = r.amount, it.isinternaltransaction = true "
            "MERGE (parent)-[:HAS_INTERNAL_TRANSACTION]->(it)"
        )

    # --- edge writers ------------------------------------------------------

    @staticmethod
    def previous_block_edges_query():
        return (
            "UNWIND $rows AS r "
            "MATCH (c:Block {number: r.number}) "
            "MATCH (p:Block {number: r.previous}) "
            "MERGE (c)-[:PREVIOUS_BLOCK]->(p)"
        )

    @staticmethod
    def recorded_in_edges_query():
        return (
            "UNWIND $rows AS r "
            "MATCH (t:ExternalTransaction {transactionhash: r.transactionhash}) "
            "MATCH (b:Block {number: r.blocknumber}) "
            "MERGE (t)-[:RECORDED_IN]->(b)"
        )

    @staticmethod
    def sent_by_edges_query():
        return (
            "UNWIND $rows AS r "
            "MATCH (u:User {address: r.address}) "
            "MATCH (t:ExternalTransaction {transactionhash: r.transactionhash}) "
            "MERGE (u)-[:SENT_BY]->(t)"
        )

    @staticmethod
    def received_by_edges_query():
        return (
            "UNWIND $rows AS r "
            "MATCH (u:User {address: r.address}) "
            "MATCH (t:ExternalTransaction {transactionhash: r.transactionhash}) "
            "MERGE (u)-[:RECEIVED_BY]->(t)"
        )

    @staticmethod
    def internal_sent_by_edges_query():
        return (
            "UNWIND $rows AS r "
            "MATCH (u:User {address: r.address}) "
            "MATCH (it:InternalTransaction {parenttransactionhash: r.parenttransactionhash, "
            "                               sequence_id: r.sequence_id}) "
            "MERGE (u)-[:SENT_BY]->(it)"
        )

    @staticmethod
    def internal_received_by_edges_query():
        return (
            "UNWIND $rows AS r "
            "MATCH (u:User {address: r.address}) "
            "MATCH (it:InternalTransaction {parenttransactionhash: r.parenttransactionhash, "
            "                               sequence_id: r.sequence_id}) "
            "MERGE (u)-[:RECEIVED_BY]->(it)"
        )
