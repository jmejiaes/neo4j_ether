class AnalyticsQueries:

    @staticmethod
    def top_accounts_by_eth_received_query():
        return """
        MATCH (u:User)-[:RECEIVED_BY]->(tx)
        WITH u.address AS account,
             CASE
               WHEN tx:ExternalTransaction THEN tx.value
               WHEN tx:InternalTransaction THEN tx.amount
             END AS received_amount
        RETURN account, SUM(received_amount) AS total_received
        ORDER BY total_received DESC
        LIMIT 10
        """

    @staticmethod
    def top_accounts_by_eth_sent_query():
        return """
        MATCH (u:User)-[:SENT_BY]->(tx)
        WITH u.address AS account,
             CASE
               WHEN tx:ExternalTransaction THEN tx.value
               WHEN tx:InternalTransaction THEN tx.amount
             END AS sent_amount
        RETURN account, SUM(sent_amount) AS total_sent
        ORDER BY total_sent DESC
        LIMIT 10
        """

    @staticmethod
    def top_accounts_by_received_pct_query():
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
    def top_accounts_by_sent_pct_query():
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
    def top_accounts_by_total_pct_query():
        # Denominator = the total number of participations (all SENT_BY + RECEIVED_BY
        # relationships = 2 x #transactions, since each transaction has one sender and
        # one receiver). The numerator is the account's own participations
        # (sent + received). This makes the ratio dimensionally coherent — a share of
        # participation slots — and independent of the (window-dependent) user/block
        # node counts. Using COUNT(all nodes) as the denominator (ADR-0008) inflated
        # the percentage as windows grew and fabricated a false "concentration
        # sharpens with scale" trend.
        #
        # The two OPTIONAL MATCHes are aggregated in SEPARATE WITH stages: doing them
        # together builds the cartesian product of a user's sent x received edges
        # before COUNT(DISTINCT) — catastrophic for hubs (WETH has ~100k of each).
        return """
        MATCH ()-[p:SENT_BY|RECEIVED_BY]->()
        WITH COUNT(p) AS total_participations

        MATCH (u:User)
        OPTIONAL MATCH (u)-[:SENT_BY]->(tx1)
        WITH total_participations, u, COUNT(DISTINCT tx1) AS sent_transactions
        OPTIONAL MATCH (u)-[:RECEIVED_BY]->(tx2)
        WITH u.address AS account,
             sent_transactions,
             COUNT(DISTINCT tx2) AS received_transactions,
             total_participations

        RETURN account,
               sent_transactions,
               received_transactions,
               (sent_transactions + received_transactions) AS total_transactions_user,
               ((sent_transactions + received_transactions) * 1.0 / total_participations) * 100 AS total_percentage
        ORDER BY total_percentage DESC
        LIMIT 10
        """

    @staticmethod
    def external_tx_statistics_query():
        return """
        MATCH (tx:ExternalTransaction)
        RETURN
          AVG(tx.value) AS average_value,
          MIN(tx.value) AS minimum_value,
          MAX(tx.value) AS maximum_value,
          percentileCont(tx.value, 0.25) AS percentile_25,
          percentileCont(tx.value, 0.5) AS median_value,
          percentileCont(tx.value, 0.75) AS percentile_75
        """

    @staticmethod
    def internal_tx_statistics_query():
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
    def top_pairs_by_tx_count_query():
        return """
        MATCH (sender:User)-[:SENT_BY]->(tx:ExternalTransaction)<-[:RECEIVED_BY]-(receiver:User)
        RETURN sender.address AS sender, receiver.address AS receiver,
               COUNT(tx) AS transaction_count
        ORDER BY transaction_count DESC
        LIMIT 10
        """

    @staticmethod
    def top_pairs_internal_by_tx_count_query():
        return """
        MATCH (sender:User)-[:SENT_BY]->(it:InternalTransaction)<-[:RECEIVED_BY]-(receiver:User)
        RETURN sender.address AS sender, receiver.address AS receiver,
               COUNT(it) AS transaction_count
        ORDER BY transaction_count DESC
        LIMIT 10
        """

    @staticmethod
    def top_pairs_user_to_contract_query():
        return """
        MATCH (sender:User {iscontract: false})-[:SENT_BY]->(tx:ExternalTransaction)<-[:RECEIVED_BY]-(receiver:User {iscontract: true})
        RETURN sender.address AS sender, receiver.address AS receiver,
            COUNT(tx) AS transaction_count
        ORDER BY transaction_count DESC
        LIMIT 10
        """

    @staticmethod
    def top_pairs_contract_to_user_query():
        return """
        MATCH (sender:User {iscontract: true})-[:SENT_BY]->(tx:ExternalTransaction)<-[:RECEIVED_BY]-(receiver:User {iscontract: false})
        RETURN sender.address AS sender, receiver.address AS receiver,
            COUNT(tx) AS transaction_count
        ORDER BY transaction_count DESC
        LIMIT 10
        """

    @staticmethod
    def top_pairs_user_to_user_query():
        return """
        MATCH (sender:User {iscontract: false})-[:SENT_BY]->(tx:ExternalTransaction)<-[:RECEIVED_BY]-(receiver:User {iscontract: false})
        RETURN sender.address AS sender, receiver.address AS receiver,
            COUNT(tx) AS transaction_count
        ORDER BY transaction_count DESC
        LIMIT 10
        """

    @staticmethod
    def top_pairs_by_value_sent_query():
        return """
        MATCH (sender:User)-[:SENT_BY]->(tx:ExternalTransaction)<-[:RECEIVED_BY]-(receiver:User)
        RETURN sender.address AS sender, receiver.address AS receiver,
            SUM(tx.value) AS total_value_sent,
            COUNT(tx) AS transaction_count
        ORDER BY total_value_sent DESC
        LIMIT 10
        """

    @staticmethod
    def block_count_query():
        return """
        MATCH (b:Block)
        RETURN COUNT(b) AS block_count
        """
