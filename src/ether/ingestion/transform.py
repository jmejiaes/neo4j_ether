def process_transaction(tx: dict) -> dict:
    return {
        "blocknumber": int(tx["blockNumber"], 16),
        "transactionhash": tx["hash"],
        # Wei to Ether conversion
        "value": int(tx["value"], 16) / 10**18,
        "isinternaltransaction": False,
    }
