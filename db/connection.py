from neo4j import GraphDatabase
from src.db.schema_queries import SchemaQueries
from src.db.analytics_queries import AnalyticsQueries


class Neo4JConnection:
    def __init__(self, url: str, user: str, password: str):
        driver = GraphDatabase.driver(url, auth=(user, password))
        self.session = driver.session()

    def close(self):
        self.session.close()

    # --- Schema / write operations ---

    def clear_database(self):
        self.session.run(SchemaQueries.clear_database_query())

    def create_block_node(self, block_info: dict):
        self.session.run(SchemaQueries.create_block_node_query(), {
            "block_number": block_info["block_number"],
            "block_reward": block_info["block_reward"],
            "block_time": block_info["block_time"],
        })

    def create_user_node(self, user_info: dict):
        # Neo4j MERGE requires non-null property values, so we fall back to 'undefined'
        address = user_info.get("address") or "undefined"
        if address == "undefined":
            balance, is_contract = -1, False
        else:
            balance = user_info.get("balance", -1)
            is_contract = user_info.get("is_contract", False)

        self.session.run(SchemaQueries.create_user_node_query(), {
            "address": address,
            "balance": balance,
            "is_contract": is_contract,
        })

    def create_transaction_node(self, tx: dict):
        self.session.run(SchemaQueries.create_transaction_node_query(), {
            "transactionhash": tx["transactionhash"],
            "blocknumber": tx.get("blocknumber", 0),
            "value": tx.get("value", 0),
            "isinternaltransaction": tx.get("isinternaltransaction", False),
        })

    def create_internal_transaction_node(self, tx: dict):
        self.session.run(SchemaQueries.create_internal_transaction_node_query(), {
            "parenttransactionhash": tx["parenttransactionhash"],
            "sequence_id": tx.get("sequence_id", 0),
            "amount": tx.get("amount", 0),
            "isinternaltransaction": tx.get("isinternaltransaction", True),
        })

    def previous_block_edge(self, block_number: int, previous_block_number: int):
        self.session.run(SchemaQueries.previous_block_edge_query(), {
            "block_number": block_number,
            "previous_block_number": previous_block_number,
        })

    def fee_received_by_edge(self, block_number: int, address: str):
        self.session.run(SchemaQueries.fee_received_by_edge_query(), {
            "block_number": block_number,
            "address": address,
        })

    def recorded_in_edge(self, tx_hash: str, block_number: int):
        self.session.run(SchemaQueries.recorded_in_edge_query(), {
            "tx_hash": tx_hash,
            "block_number": block_number,
        })

    def link_user_to_transaction_sent_by(self, user_info: dict, tx: dict):
        self.session.run(SchemaQueries.sent_by_edge_query(), {
            "sender_address": user_info["address"],
            "transactionhash": tx["transactionhash"],
        })

    def link_user_to_transaction_received_by(self, user_info: dict, tx: dict):
        self.session.run(SchemaQueries.received_by_edge_query(), {
            "receiver_address": user_info["address"],
            "transactionhash": tx["transactionhash"],
        })

    def link_user_to_internal_transaction_sent_by(self, user_info: dict, tx: dict):
        self.session.run(SchemaQueries.internal_sent_by_edge_query(), {
            "sender_address": user_info["address"],
            "parenttransactionhash": tx["parenttransactionhash"],
            "sequence_id": tx["sequence_id"],
        })

    def link_user_to_internal_transaction_received_by(self, user_info: dict, tx: dict):
        self.session.run(SchemaQueries.internal_received_by_edge_query(), {
            "receiver_address": user_info["address"],
            "parenttransactionhash": tx["parenttransactionhash"],
            "sequence_id": tx["sequence_id"],
        })

    # --- Analytics / read operations ---

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
