class Queries:

    @staticmethod
    def clear_database_query():
        return "MATCH (n) DETACH DELETE n"

    @staticmethod
    def create_transaction_node_query():
        return (
            "MERGE (t:Transaction {transactionhash: $transactionhash}) "
            "ON CREATE SET "
            "t.blocknumber = $blocknumber, "
            "t.value = $value, "
            "t.isinternaltransaction = $isinternaltransaction"
        )

    @staticmethod
    def create_internal_transaction_node_query():
        return (
            "MERGE (parent:Transaction {transactionhash: $parenttransactionhash}) "
            "MERGE (t:InternalTransaction {parenttransactionhash: $parenttransactionhash, sequence_id: $sequence_id}) "
            "ON CREATE SET "
            "t.amount = $amount, "
            "t.isinternaltransaction = $isinternaltransaction "
            "MERGE (parent)-[:HAS_INTERNAL_TRANSACTION]->(t)"
        )

    @staticmethod
    def create_block_node_query():
        return (
            "MERGE (b:Block {number: $block_number}) "
            "ON CREATE SET "
            "b.reward = $block_reward, "
            "b.time = $block_time"
        )

    @staticmethod
    def create_user_node_query():
        return (
            "MERGE (u:User {address: $address}) "
            "ON CREATE SET "
            "u.balance = $balance, "
            "u.iscontract = $is_contract"
        )

    @staticmethod
    def previous_block_edge_query():
        return (
            "MATCH (current:Block {number: $block_number}) "
            "MATCH (previous:Block {number: $previous_block_number}) "
            "MERGE (current)-[:PREVIOUS_BLOCK]->(previous)"
        )

    @staticmethod
    def fee_received_by_edge_query():
        return (
            "MATCH (block:Block {number: $block_number}) "
            "MATCH (user:User {address: $address}) "
            "MERGE (user)-[:FEE_RECEIVED_BY]->(block)"
        )

    @staticmethod
    def recorded_in_edge_query():
        return (
            "MATCH (tx:Transaction {transactionhash: $tx_hash}) "
            "MATCH (block:Block {number: $block_number}) "
            "MERGE (tx)-[:RECORDED_IN]->(block)"
        )

    @staticmethod
    def link_user_to_transaction_sent_by_query():
        return (
            "MATCH (u:User {address: $sender_address}) "
            "MATCH (t:Transaction {transactionhash: $transactionhash}) "
            "MERGE (u)-[:SENT_BY]->(t)"
        )

    @staticmethod
    def link_user_to_transaction_received_by_query():
        return (
            "MATCH (u:User {address: $receiver_address}) "
            "MATCH (t:Transaction {transactionhash: $transactionhash}) "
            "MERGE (u)-[:RECEIVED_BY]->(t)"
        )

    @staticmethod
    def link_user_to_internal_transaction_sent_by_query():
        return (
            "MATCH (u:User {address: $sender_address}) "
            "MATCH (it:InternalTransaction {parenttransactionhash: $parenttransactionhash, sequence_id: $sequence_id}) "
            "MERGE (u)-[:SENT_BY]->(it)"
        )

    @staticmethod
    def link_user_to_internal_transaction_received_by_query():
        return (
            "MATCH (u:User {address: $receiver_address}) "
            "MATCH (it:InternalTransaction {parenttransactionhash: $parenttransactionhash, sequence_id: $sequence_id}) "
            "MERGE (u)-[:RECEIVED_BY]->(it)"
        )

