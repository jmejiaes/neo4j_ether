from neo4j import GraphDatabase
from ddl_queries import Queries as DDLQueries
from dml_queries import Queries as DMLQueries

class Neo4JConnection:
    def __init__(self, url: str, user: str, password: str):
        driver = GraphDatabase.driver(url, auth=(user, password))
        self.session = driver.session()

    def close_connection(self):
        self.session.close()

    # Limpiar la base de datos
    def clear_database(self):
        query = DDLQueries.clear_database_query()
        self.session.run(query)

    def create_transaction_node(self, tx):
        query = DDLQueries.create_transaction_node_query()
        parameters = {
            "transactionhash": tx['transactionhash'],
            "blocknumber": tx.get('blocknumber', 0),
            "value": tx.get('value', 0),
            "isinternaltransaction": tx.get('isinternaltransaction', False)
        }
        self.session.run(query, parameters)

    def create_internal_transaction_node(self, tx):
        query = DDLQueries.create_internal_transaction_node_query()
        parameters = {
            "parenttransactionhash": tx['parenttransactionhash'],
            "sequence_id": tx.get('sequence_id', 0),
            "amount": tx.get('amount', 0),
            "isinternaltransaction": tx.get('isinternaltransaction', True)
        }
        self.session.run(query, parameters)

    def create_block_node(self, block_info):
        query = DDLQueries.create_block_node_query()
        parameters = {
            "block_number": block_info['block_number'],
            "block_reward": block_info['block_reward'],
            "block_time": block_info['block_time']
        }
        self.session.run(query, parameters)

    def create_user_node(self, user_info):
        user_address = user_info.get('address', 'undefined')
        if user_address is None:
            user_address = 'undefined'
            user_balance = -1
            is_contract = False
        else:
            user_balance = user_info.get('balance', -1)
            is_contract = user_info.get('is_contract', False)

        query = DDLQueries.create_user_node_query()
        parameters = {
            "address": user_address,
            "balance": user_balance,
            "is_contract": is_contract
        }
        self.session.run(query, parameters)

    def previous_block_edge(self, block_number, previous_block_number):
        query = DDLQueries.previous_block_edge_query()
        parameters = {
            "block_number": block_number,
            "previous_block_number": previous_block_number
        }
        self.session.run(query, parameters)
    
    def fee_received_by_edge(self, block_number, address):
        query = DMLQueries.fee_received_by_edge_query()
        parameters = {
            "block_number": block_number,
            "address": address
        }
        self.session.run(query, parameters)

    def recorded_in_edge(self, tx_hash, block_number):
        query = DMLQueries.recorded_in_edge_query()
        parameters = {
            "tx_hash": tx_hash,
            "block_number": block_number
        }
        self.session.run(query, parameters)

    def link_user_to_transaction_sent_by(self, user_info, transaction_info):
        query = DMLQueries.link_user_to_transaction_sent_by_query()
        parameters = {
            "sender_address": user_info['address'],
            "transactionhash": transaction_info['transactionhash']
        }
        self.session.run(query, parameters)

    def link_user_to_transaction_received_by(self, user_info, transaction_info):
        query = DMLQueries.link_user_to_transaction_received_by_query()
        parameters = {
            "receiver_address": user_info['address'],
            "transactionhash": transaction_info['transactionhash']
        }
        self.session.run(query, parameters)

    def link_user_to_internal_transaction_sent_by(self, user_info, internal_transaction_info):
        query = DMLQueries.link_user_to_internal_transaction_sent_by_query()
        parameters = {
            "sender_address": user_info['address'],
            "parenttransactionhash": internal_transaction_info['parenttransactionhash'],
            "sequence_id": internal_transaction_info['sequence_id']
        }
        self.session.run(query, parameters)

    def link_user_to_internal_transaction_received_by(self, user_info, internal_transaction_info):
        query = DMLQueries.link_user_to_internal_transaction_received_by_query()
        parameters = {
            "receiver_address": user_info['address'],
            "parenttransactionhash": internal_transaction_info['parenttransactionhash'],
            "sequence_id": internal_transaction_info['sequence_id']
        }
        self.session.run(query, parameters)

    
    # DML Queries

    def get_accounts_most_received_eth(self):
        query = DMLQueries.get_accounts_most_received_eth_query()
        return self.session.run(query)

    def get_accounts_most_sent_eth(self):
        query = DMLQueries.get_accounts_most_sent_eth_query()
        return self.session.run(query)

    def get_most_active_accounts_received_percentage(self):
        query = DMLQueries.get_most_active_accounts_received_percentage_query()
        return self.session.run(query)

    def get_most_active_accounts_sent_percentage(self):
        query = DMLQueries.get_most_active_accounts_sent_percentage_query()
        return self.session.run(query)

    def get_most_active_accounts_total_percentage(self):
        query = DMLQueries.get_most_active_accounts_total_percentage_query()
        return self.session.run(query)

    def get_transaction_statistics(self):
        query = DMLQueries.get_transaction_statistics_query()
        return self.session.run(query)

    def get_internal_transaction_statistics(self):
        query = DMLQueries.get_internal_transaction_statistics_query()
        return self.session.run(query)

    def get_top_account_pairs_external(self):
        query = DMLQueries.get_top_account_pairs_external_query()
        return self.session.run(query)

    def get_top_account_pairs_internal(self):
        query = DMLQueries.get_top_account_pairs_internal_query()
        return self.session.run(query)

    def get_top_pairs_user_to_contract(self):
        query = DMLQueries.get_top_pairs_user_to_contract_query()
        return self.session.run(query)

    def get_top_pairs_contract_to_user(self):
        query = DMLQueries.get_top_pairs_contract_to_user_query()
        return self.session.run(query)

    def get_top_pairs_user_to_user(self):
        query = DMLQueries.get_top_pairs_user_to_user_query()
        return self.session.run(query)

    def get_top_account_pairs_by_value_sent(self):
        query = DMLQueries.get_top_account_pairs_by_value_sent_query()
        return self.session.run(query)

    def get_block_count(self):
        query = DMLQueries.get_block_count_query()
        return self.session.run(query)