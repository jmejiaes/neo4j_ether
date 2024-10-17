import requests
import datetime
from config import API_KEY, ETHERSCAN_API_URL

def get_address_info(address):
    info = {}

    try:
        # Fetch the code at the given address
        code_params = {
            'module': 'proxy',
            'action': 'eth_getCode',
            'address': address,
            'tag': 'latest',
            'apikey': API_KEY
        }
        response = requests.get(ETHERSCAN_API_URL, params=code_params)
        response.raise_for_status()
        code_data = response.json()

        # Check if the code is empty
        if code_data.get('result') == '0x':
            info['is_contract'] = False
        else:
            info['is_contract'] = True

        # Fetching the balance of the address
        balance_params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': API_KEY
        }
        balance_response = requests.get(ETHERSCAN_API_URL, params=balance_params)
        balance_response.raise_for_status()
        balance_data = balance_response.json()

        if 'result' in balance_data:
            info['balance'] = int(balance_data['result']) / 10**18
        else:
            info['balance'] = 0  # Handle unexpected response format

        info['address'] = address

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        info['address'] = address  # Keep the original address
        info['balance'] = -1  # Set balance to -1 in case of error
        info['is_contract'] = False
        info['error'] = "HTTP error occurred"
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        info['address'] = address
        info['balance'] = -1  # Set balance to -1 in case of error
        info['is_contract'] = False
        info['error'] = "Request error occurred"
    except KeyError as key_err:
        print(f"Key error: {key_err}")
        info['address'] = address
        info['balance'] = -1  # Set balance to -1 in case of error
        info['is_contract'] = False
        info['error'] = "Key error - unexpected response format"
    except Exception as e:
        print(f"An error occurred: {e}")
        info['address'] = address
        info['balance'] = -1  # Set balance to -1 in case of error
        info['is_contract'] = False
        info['error'] = "An unexpected error occurred"

    return info


def get_block_info(block_number):
    info = {}
    
    try:
        # Fetch the block info
        block_params = {
            'module': 'block',
            'action': 'getblockreward',
            'blockno': block_number,
            'apikey': API_KEY
        }
        response = requests.get(ETHERSCAN_API_URL, params=block_params)
        response.raise_for_status()
        block_data = response.json()

        # Extracting the required information
        info['block_number'] = block_number
        info['block_reward'] = int(block_data['result']['blockReward']) / 10**18

        # Convert UNIX timestamp to the desired datetime format
        block_time_unix = int(block_data['result']['timeStamp'])
        block_time = datetime.utcfromtimestamp(block_time_unix)
        info['block_time'] = block_time.strftime('%b-%d-%Y %I:%M:%S %p +UTC')

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        info['error'] = "HTTP error occurred"
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        info['error'] = "Request error occurred"
    except KeyError as key_err:
        print(f"Key error: {key_err}")
        info['error'] = "Key error - unexpected response format"
    except Exception as e:
        print(f"An error occurred: {e}")
        info['error'] = "An unexpected error occurred"

    return info

def get_block_transactions(block_number):

    # Parámetros de la consulta
    params = {
        'module': 'proxy',
        'action': 'eth_getBlockByNumber',
        'tag': hex(block_number),  # El número de bloque debe ser pasado como hexadecimal
        'boolean': 'true',  # Incluir las transacciones en la respuesta
        'apikey': API_KEY
    }

    try:
        # Realizar la solicitud GET
        response = requests.get(ETHERSCAN_API_URL, params=params)
        response.raise_for_status()  # Verifica si hubo errores en la solicitud

        # Obtener los datos en formato JSON
        data = response.json()

        # Verifica si 'result' está en la respuesta y contiene las transacciones
        if data and 'result' in data and 'transactions' in data['result']:
            return data['result']['transactions']
        else:
            print(f"Error: No se encontraron transacciones en el bloque {block_number}.")
            return []

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return []

def get_block_internal_transactions(block_number):
    params = {
        'module': 'account',
        'action': 'txlistinternal',
        'startblock': block_number,
        'endblock': block_number,
        'page': 1,
        'offset': 9000,
        'sort': 'asc',
        'apikey': API_KEY
    }
    
    response = requests.get(ETHERSCAN_API_URL, params=params)

    final_data = []
    sequences = {}

    if response.status_code == 200:
        data = response.json()
        if data['status'] == '1':  # '1' means success in the Etherscan API

            for tx in data['result']:

                if tx['hash'] in sequences:
                    sequences[tx['hash']] += 1
                else:
                    sequences[tx['hash']] = 1

                processed_tx = {
                    # Add parent hash
                    'from': tx['from'],
                    'to': tx['to'],
                    'parenttransactionhash': tx['hash'],
                    'sequence_id': sequences[tx['hash']],
                    'amount': int(tx['value']) / 10**18,  # Convert from wei to ether
                    'isinternaltransaction': True
                }

                final_data.append(processed_tx)

            return final_data

        else:
            print(f"Error: {data['message']}")
            return None
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None