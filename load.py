
from api_utils import get_address_info, get_block_info, get_block_internal_transactions, get_block_transactions
from preprocess import process_transaction

def load_data_from_block_interval(initial_block, final_block, neo4j_connection):

    for block_number in range(initial_block, final_block + 1):
        print(f"Processing block: {block_number}")

        # Obtener la informacion del bloque
        block_info = get_block_info(block_number)

        # Crear nodo de bloque
        neo4j_connection.create_block_node(block_info)

        # Obtener las transacciones del bloque
        transactions = get_block_transactions(block_number)

        # Obtener las transacciones internas del bloque
        internal_transactions = get_block_internal_transactions(block_number)

        # iterar por las transacciones normales
        for tx in transactions:
            # procesara la transaccion
            processed_tx = process_transaction(tx)

            # Obtener informacion de los usuarios
            sender_info = get_address_info(tx['from'])
            receiver_info = get_address_info(tx['to'])

            # Crear nodos de usuario
            neo4j_connection.create_user_node(sender_info)
            neo4j_connection.create_user_node(receiver_info)

            # Crear nodo de transaccion
            neo4j_connection.create_transaction_node(processed_tx)

            # Crear relaciones entre la transaccion y el bloque
            neo4j_connection.recorded_in_edge(processed_tx['transactionhash'], processed_tx['blocknumber'])

            # crear sender y receiver
            neo4j_connection.link_user_to_transaction_sent_by(sender_info, processed_tx)
            neo4j_connection.link_user_to_transaction_received_by(receiver_info, processed_tx)

        # Iterar por las transacciones internas
        for tx2 in internal_transactions:
            neo4j_connection.create_internal_transaction_node(tx2)

            # sender y receiver para transaccion
            sender_info = get_address_info(tx2['from'])
            receiver_info = get_address_info(tx2['to'])

            # Crear nodos de usuario
            neo4j_connection.create_user_node(sender_info)
            neo4j_connection.create_user_node(receiver_info)

            # Crear relaciones de receptor y emisor
            neo4j_connection.link_user_to_internal_transaction_sent_by(sender_info, tx2)
            neo4j_connection.link_user_to_internal_transaction_received_by(receiver_info, tx2)


        # Crear relaciones entre bloques
        if block_number > initial_block:
            neo4j_connection.previous_block_edge(block_number, block_number - 1)

        print(f"Block {block_number} processed successfully!")

    return
