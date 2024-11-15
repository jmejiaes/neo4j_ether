from model_connection import Neo4JConnection
from config import NEO4J_API_PASSWORD, NEO4J_API_URI, NEO4J_API_USERNAME
from load import load_data_from_block_interval
from process_results import process_results
from preprocess import make_dir_for_results

def main():
    # Create a connection to the Neo4J database
    neo4j_connection = Neo4JConnection(NEO4J_API_URI, NEO4J_API_USERNAME, NEO4J_API_PASSWORD)

    # Clear the database
    neo4j_connection.clear_database()

    print("Database cleared")

    # Define interval of blocks to process
    initial_block = 20512878
    final_block   = 20512888

    

    # Load data from the block interval
    load_data_from_block_interval(initial_block, final_block, neo4j_connection)

    # make_dir_for_results
    cantidad_bloques = neo4j_connection.get_block_count().single()['block_count']

    result_dir = make_dir_for_results(
        cantidad_bloques, 
        initial_block, 
        final_block
    )

    # Process results
    process_results(neo4j_connection, result_dir)


if __name__ == "__main__":
    main()
