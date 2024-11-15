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

if __name__ == "__main__":
    
    string = {'blockHash': '0x2d2aa2faa5f0dcc4ff68226af85c3b7825929f89762ef1b5c6c105098d6966e8', 'blockNumber': '0x139006e', 'from': '0xf389646222f841787fb09162e7d29ba11d9faae8', 'gas': '0xfeb3', 'gasPrice': '0x1e1f57d7f', 'maxFeePerGas': '0x2502c939b', 'maxPriorityFeePerGas': '0x77359400', 'hash': '0x01a0cea9b1cdc357e1dac30f899f0863e5f79ca40c2ad51163058f14cef2b2ee', 'input': '0x095ea7b3000000000000000000000000ae2d4617c862309a3d75a0ffb358c7a5009c673fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 'nonce': '0x0', 'to': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'transactionIndex': '0x0', 'value': '0x0', 'type': '0x2', 'accessList': [], 'chainId': '0x1', 'v': '0x0', 'r': '0xa6e10076fe6d74dc8b3f9d1bf6fb43f0dd1423ff3c5a9db08d9ce6d9df24b1ff', 's': '0x77a847523b0d5393ca6c59b60114e63a94dabd3a7cf00b56fa2afd8a1adb6efc', 'yParity': '0x0'}
    print(process_transaction(string))