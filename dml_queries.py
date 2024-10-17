class Queries:

    @staticmethod
    def clear_database_query():
        return "MATCH (n) DETACH DELETE n"

    @staticmethod
    def get_accounts_most_received_eth_query():
        return """
        MATCH (u:User)-[:RECEIVED_BY]->(tx)
        WITH u.address AS account,
             CASE 
               WHEN tx:Transaction THEN tx.value 
               WHEN tx:InternalTransaction THEN tx.amount 
             END AS received_amount
        RETURN account, SUM(received_amount) AS total_received
        ORDER BY total_received DESC
        LIMIT 10
        """

    @staticmethod
    def get_accounts_most_sent_eth_query():
        return """
        MATCH (u:User)-[:SENT_BY]->(tx)
        WITH u.address AS account,
             CASE 
               WHEN tx:Transaction THEN tx.value 
               WHEN tx:InternalTransaction THEN tx.amount 
             END AS sent_amount
        RETURN account, SUM(sent_amount) AS total_sent
        ORDER BY total_sent DESC
        LIMIT 10
        """

    @staticmethod
    def get_most_active_accounts_received_percentage_query():
        return """
        MATCH (u:User)-[:RECEIVED_BY]->(tx)
        WITH COUNT(tx) AS total_transactions
        MATCH (u:User)-[:RECEIVED_BY]->(tx)
        WITH u.address AS account, COUNT(tx) AS received_transactions, total_transactions
        RETURN account, 
            received_transactions, 
            (received_transactions * 1.0 / total_transactions) * 100 AS received_percentage
        ORDER BY received_percentage DESC
        LIMIT 10
        """

    @staticmethod
    def get_most_active_accounts_sent_percentage_query():
        return """
        MATCH (u:User)-[:SENT_BY]->(tx)
        WITH COUNT(tx) AS total_transactions
        MATCH (u:User)-[:SENT_BY]->(tx)
        WITH u.address AS account, COUNT(tx) AS sent_transactions, total_transactions
        RETURN account, 
            sent_transactions, 
            (sent_transactions * 1.0 / total_transactions) * 100 AS sent_percentage
        ORDER BY sent_percentage DESC
        LIMIT 10
        """

    @staticmethod
    def get_most_active_accounts_total_percentage_query():
        return """
        // Contamos el total de transacciones tanto enviadas como recibidas
        MATCH (tx)
        WITH COUNT(tx) AS total_transactions
        
        // Obtenemos la cuenta y el número de transacciones enviadas y recibidas por cada usuario
        MATCH (u:User)
        OPTIONAL MATCH (u)-[:SENT_BY]->(tx1)
        OPTIONAL MATCH (u)-[:RECEIVED_BY]->(tx2)
        
        // Sumamos las transacciones enviadas y recibidas para obtener la actividad total
        WITH u.address AS account,
             COUNT(DISTINCT tx1) AS sent_transactions,
             COUNT(DISTINCT tx2) AS received_transactions,
             (COUNT(DISTINCT tx1) + COUNT(DISTINCT tx2)) AS total_transactions_user,
             total_transactions  // Traemos la variable 'total_transactions' al WITH
        
        // Calculamos el porcentaje de la actividad total respecto al total de transacciones
        RETURN account, 
               sent_transactions, 
               received_transactions,
               total_transactions_user,
               (total_transactions_user * 1.0 / total_transactions) * 100 AS total_percentage
        ORDER BY total_percentage DESC
        LIMIT 10
        """

    @staticmethod
    def get_transaction_statistics_query():
        return """
        MATCH (tx:Transaction)
        RETURN
          AVG(tx.value) AS average_value,
          MIN(tx.value) AS minimum_value,
          MAX(tx.value) AS maximum_value,
          percentileCont(tx.value, 0.25) AS percentile_25,
          percentileCont(tx.value, 0.5) AS median_value,
          percentileCont(tx.value, 0.75) AS percentile_75
        """

    @staticmethod
    def get_internal_transaction_statistics_query():
        return """
        MATCH (it:InternalTransaction)
        RETURN
          AVG(it.amount) AS average_amount,
          MIN(it.amount) AS minimum_amount,
          MAX(it.amount) AS maximum_amount,
          percentileCont(it.amount, 0.25) AS percentile_25,
          percentileCont(it.amount, 0.5) AS median_amount,
          percentileCont(it.amount, 0.75) AS percentile_75
        """
    
    
    @staticmethod
    def get_top_account_pairs_external_query():
        return """
        MATCH (sender:User)-[:SENT_BY]->(tx:Transaction)<-[:RECEIVED_BY]-(receiver:User)
        RETURN sender.address AS sender, receiver.address AS receiver,
               COUNT(tx) AS transaction_count
        ORDER BY transaction_count DESC
        LIMIT 10
        """

    @staticmethod
    def get_top_account_pairs_internal_query():
        return """
        MATCH (sender:User)-[:SENT_BY]->(it:InternalTransaction)<-[:RECEIVED_BY]-(receiver:User)
        RETURN sender.address AS sender, receiver.address AS receiver,
               COUNT(it) AS transaction_count
        ORDER BY transaction_count DESC
        LIMIT 10
        """

    @staticmethod
    def get_top_pairs_user_to_contract_query():
        return """
        MATCH (sender:User {iscontract: false})-[:SENT_BY]->(tx)<-[:RECEIVED_BY]-(receiver:User {iscontract: true})
        RETURN sender.address AS sender, receiver.address AS receiver,
            COUNT(tx) AS transaction_count
        ORDER BY transaction_count DESC
        LIMIT 10
        """

    @staticmethod
    def get_top_pairs_contract_to_user_query():
        return """
        MATCH (sender:User {iscontract: true})-[:SENT_BY]->(tx)<-[:RECEIVED_BY]-(receiver:User {iscontract: false})
        RETURN sender.address AS sender, receiver.address AS receiver,
            COUNT(tx) AS transaction_count
        ORDER BY transaction_count DESC
        LIMIT 10
        """

    @staticmethod
    def get_top_pairs_user_to_user_query():
        return """
        MATCH (sender:User {iscontract: false})-[:SENT_BY]->(tx)<-[:RECEIVED_BY]-(receiver:User {iscontract: false})
        RETURN sender.address AS sender, receiver.address AS receiver,
            COUNT(tx) AS transaction_count
        ORDER BY transaction_count DESC
        LIMIT 10
        """

    @staticmethod
    def get_top_account_pairs_by_value_sent_query():
        return """
        MATCH (sender:User)-[:SENT_BY]->(tx:Transaction)<-[:RECEIVED_BY]-(receiver:User)
        RETURN sender.address AS sender, receiver.address AS receiver,
            SUM(tx.value) AS total_value_sent,
            COUNT(tx) AS transaction_count
        ORDER BY total_value_sent DESC
        LIMIT 10
        """

    @staticmethod
    def get_block_count_query():
        return """
        MATCH (b:Block)
        RETURN COUNT(b) AS block_count
        """