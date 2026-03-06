from src.ingestion.etherscan import (
    get_address_info,
    get_block_info,
    get_block_transactions,
    get_block_internal_transactions,
)
from src.ingestion.transform import process_transaction
from src.db.connection import Neo4JConnection


def load_blocks(connection: Neo4JConnection, initial_block: int, final_block: int):
    for block_number in range(initial_block, final_block + 1):
        print(f"Processing block {block_number}...")
        _load_single_block(connection, block_number, initial_block)
        print(f"Block {block_number} done.")


def _load_single_block(connection: Neo4JConnection, block_number: int, initial_block: int):
    block_info = get_block_info(block_number)
    connection.create_block_node(block_info)

    _load_external_transactions(connection, block_number)
    _load_internal_transactions(connection, block_number)

    # Only link to previous block if not the first block in the interval
    if block_number > initial_block:
        connection.previous_block_edge(block_number, block_number - 1)


def _load_external_transactions(connection: Neo4JConnection, block_number: int):
    for raw_tx in get_block_transactions(block_number):
        tx = process_transaction(raw_tx)
        sender = get_address_info(raw_tx["from"])
        receiver = get_address_info(raw_tx["to"])

        connection.create_user_node(sender)
        connection.create_user_node(receiver)
        connection.create_transaction_node(tx)
        connection.recorded_in_edge(tx["transactionhash"], tx["blocknumber"])
        connection.link_user_to_transaction_sent_by(sender, tx)
        connection.link_user_to_transaction_received_by(receiver, tx)


def _load_internal_transactions(connection: Neo4JConnection, block_number: int):
    internal_txs = get_block_internal_transactions(block_number)
    if not internal_txs:
        return

    for tx in internal_txs:
        sender = get_address_info(tx["from"])
        receiver = get_address_info(tx["to"])

        connection.create_internal_transaction_node(tx)
        connection.create_user_node(sender)
        connection.create_user_node(receiver)
        connection.link_user_to_internal_transaction_sent_by(sender, tx)
        connection.link_user_to_internal_transaction_received_by(receiver, tx)
