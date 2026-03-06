import requests
from datetime import datetime
from src.config import API_KEY, ETHERSCAN_API_URL


def get_address_info(address: str) -> dict:
    info = {"address": address}
    try:
        code_data = _get({"module": "proxy", "action": "eth_getCode", "address": address, "tag": "latest"})
        info["is_contract"] = code_data.get("result") != "0x"

        balance_data = _get({"module": "account", "action": "balance", "address": address, "tag": "latest"})
        # Wei to Ether conversion
        info["balance"] = int(balance_data["result"]) / 10**18 if "result" in balance_data else 0

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for address {address}: {e}")
        info.update({"balance": -1, "is_contract": False, "error": str(e)})
    except requests.exceptions.RequestException as e:
        print(f"Request error for address {address}: {e}")
        info.update({"balance": -1, "is_contract": False, "error": str(e)})
    except (KeyError, ValueError) as e:
        print(f"Parse error for address {address}: {e}")
        info.update({"balance": -1, "is_contract": False, "error": str(e)})

    return info


def get_block_info(block_number: int) -> dict:
    info = {}
    try:
        data = _get({"module": "block", "action": "getblockreward", "blockno": block_number})
        info["block_number"] = block_number
        # Wei to Ether conversion
        info["block_reward"] = int(data["result"]["blockReward"]) / 10**18
        ts = datetime.utcfromtimestamp(int(data["result"]["timeStamp"]))
        info["block_time"] = ts.strftime("%b-%d-%Y %I:%M:%S %p +UTC")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for block {block_number}: {e}")
        info["error"] = str(e)
    except requests.exceptions.RequestException as e:
        print(f"Request error for block {block_number}: {e}")
        info["error"] = str(e)
    except (KeyError, ValueError) as e:
        print(f"Parse error for block {block_number}: {e}")
        info["error"] = str(e)

    return info


def get_block_transactions(block_number: int) -> list:
    try:
        data = _get({
            "module": "proxy",
            "action": "eth_getBlockByNumber",
            "tag": hex(block_number),
            "boolean": "true",
        })
        if data and "result" in data and "transactions" in data["result"]:
            return data["result"]["transactions"]
        print(f"No transactions found in block {block_number}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for block {block_number} transactions: {e}")
    except Exception as e:
        print(f"Error fetching block {block_number} transactions: {e}")
    return []


def get_block_internal_transactions(block_number: int) -> list | None:
    # offset=9000 to fetch up to 9000 internal txs per block (Etherscan page limit)
    response = requests.get(ETHERSCAN_API_URL, params={
        "module": "account",
        "action": "txlistinternal",
        "startblock": block_number,
        "endblock": block_number,
        "page": 1,
        "offset": 9000,
        "sort": "asc",
        "apikey": API_KEY,
    })

    if response.status_code != 200:
        print(f"Failed to fetch internal transactions for block {block_number}: {response.status_code}")
        return None

    data = response.json()
    if data["status"] != "1":
        print(f"Etherscan error for block {block_number}: {data['message']}")
        return None

    tx_sequence_counters: dict[str, int] = {}
    result = []
    for tx in data["result"]:
        tx_sequence_counters[tx["hash"]] = tx_sequence_counters.get(tx["hash"], 0) + 1
        result.append({
            "from": tx["from"],
            "to": tx["to"],
            "parenttransactionhash": tx["hash"],
            "sequence_id": tx_sequence_counters[tx["hash"]],
            # Wei to Ether conversion
            "amount": int(tx["value"]) / 10**18,
            "isinternaltransaction": True,
        })

    return result


def _get(params: dict) -> dict:
    params["apikey"] = API_KEY
    response = requests.get(ETHERSCAN_API_URL, params=params)
    response.raise_for_status()
    return response.json()
