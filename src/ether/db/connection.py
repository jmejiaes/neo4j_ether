from neo4j import GraphDatabase
from ether.db.schema_queries import SchemaQueries
from ether.db.analytics_queries import AnalyticsQueries

DEFAULT_BATCH_SIZE = 5000


class Neo4JConnection:
    def __init__(self, url: str, user: str, password: str):
        self._driver = GraphDatabase.driver(url, auth=(user, password))
        self.session = self._driver.session()

    def close(self):
        self.session.close()
        self._driver.close()

    # --- batching helper ---------------------------------------------------

    def _write_batched(self, query: str, rows: list[dict], batch_size: int = DEFAULT_BATCH_SIZE):
        """UNWIND `rows` through `query` in chunks of `batch_size` (ADR-0005)."""
        for i in range(0, len(rows), batch_size):
            self.session.run(query, {"rows": rows[i:i + batch_size]})

    # --- schema / setup ----------------------------------------------------

    def create_constraints(self):
        for q in SchemaQueries.constraint_queries():
            self.session.run(q)

    def clear_database(self):
        for q in SchemaQueries.clear_database_queries():
            self.session.run(q).consume()

    # --- bulk node writes --------------------------------------------------

    def create_blocks(self, rows: list[dict]):
        self._write_batched(SchemaQueries.create_blocks_query(), rows)

    def create_users(self, rows: list[dict]):
        self._write_batched(SchemaQueries.create_users_query(), rows)

    def create_external_transactions(self, rows: list[dict]):
        self._write_batched(SchemaQueries.create_external_transactions_query(), rows)

    def create_internal_transactions(self, rows: list[dict]):
        self._write_batched(SchemaQueries.create_internal_transactions_query(), rows)

    # --- bulk edge writes --------------------------------------------------

    def create_previous_block_edges(self, rows: list[dict]):
        self._write_batched(SchemaQueries.previous_block_edges_query(), rows)

    def create_recorded_in_edges(self, rows: list[dict]):
        self._write_batched(SchemaQueries.recorded_in_edges_query(), rows)

    def create_sent_by_edges(self, rows: list[dict]):
        self._write_batched(SchemaQueries.sent_by_edges_query(), rows)

    def create_received_by_edges(self, rows: list[dict]):
        self._write_batched(SchemaQueries.received_by_edges_query(), rows)

    def create_internal_sent_by_edges(self, rows: list[dict]):
        self._write_batched(SchemaQueries.internal_sent_by_edges_query(), rows)

    def create_internal_received_by_edges(self, rows: list[dict]):
        self._write_batched(SchemaQueries.internal_received_by_edges_query(), rows)

    # --- analytics / read operations ---------------------------------------

    def get_accounts_most_received_eth(self):
        return self.session.run(AnalyticsQueries.top_accounts_by_eth_received_query())

    def get_accounts_most_sent_eth(self):
        return self.session.run(AnalyticsQueries.top_accounts_by_eth_sent_query())

    def get_most_active_accounts_received_percentage(self):
        return self.session.run(AnalyticsQueries.top_accounts_by_received_pct_query())

    def get_most_active_accounts_sent_percentage(self):
        return self.session.run(AnalyticsQueries.top_accounts_by_sent_pct_query())

    def get_most_active_accounts_total_percentage(self):
        return self.session.run(AnalyticsQueries.top_accounts_by_total_pct_query())

    def get_transaction_statistics(self):
        return self.session.run(AnalyticsQueries.external_tx_statistics_query())

    def get_internal_transaction_statistics(self):
        return self.session.run(AnalyticsQueries.internal_tx_statistics_query())

    def get_top_account_pairs_external(self):
        return self.session.run(AnalyticsQueries.top_pairs_by_tx_count_query())

    def get_top_account_pairs_internal(self):
        return self.session.run(AnalyticsQueries.top_pairs_internal_by_tx_count_query())

    def get_top_pairs_user_to_contract(self):
        return self.session.run(AnalyticsQueries.top_pairs_user_to_contract_query())

    def get_top_pairs_contract_to_user(self):
        return self.session.run(AnalyticsQueries.top_pairs_contract_to_user_query())

    def get_top_pairs_user_to_user(self):
        return self.session.run(AnalyticsQueries.top_pairs_user_to_user_query())

    def get_top_account_pairs_by_value_sent(self):
        return self.session.run(AnalyticsQueries.top_pairs_by_value_sent_query())

    def get_block_count(self):
        return self.session.run(AnalyticsQueries.block_count_query())
