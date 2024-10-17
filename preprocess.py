import os

def make_dir_for_results(cantidad_bloques, initial_block, final_block):
    result_dir = f"results_for_{cantidad_bloques}_({initial_block}_{final_block})"
    os.makedirs(result_dir, exist_ok=True)
    return result_dir

def save_results_to_csv(results, filename, result_dir):
    results.to_csv(f"{result_dir}/{filename}.csv", index=False)

def process_transaction(tx):
    processed_tx = {
        'blocknumber': int(tx['blockNumber'], 16),
        'transactionhash': tx['hash'],
        'value': int(tx['value'], 16) / 10**18,  # Convertir de wei a ether
        'isinternaltransaction': False
    }

    return processed_tx