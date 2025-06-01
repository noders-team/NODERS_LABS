import re
import subprocess
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def format_number(number):
    return "{:,.4f}".format(number)

def check_object_balance(object_id):
    command_output = subprocess.check_output(f"sui client object {object_id}", shell=True, stderr=subprocess.DEVNULL, universal_newlines=True)
    balance_line = re.search(r'balance:\s*(\d+)', command_output)
    if balance_line:
        balance = int(balance_line.group(1))
        return balance
    else:
        return 0

def is_valid_address(address):
    # Add address validation logic here
    # For now, let's just check if the address starts with "0x" and has the correct length for a hexadecimal Ethereum address.
    if address.startswith("0x") and len(address) == 42:
        return True
    return False

def check_gas_balance():
    """
    Checks the balance of the gas object from .env file via RPC and displays it in a nice format (English output)
    """
    gas_object = os.getenv("GAS_OBJECT")
    if not gas_object:
        print("GAS_OBJECT not found in .env file.")
        return

    url = "https://fullnode.mainnet.sui.io:443"
    headers = {"Content-Type": "application/json"}
    additional_params = {
        "showType": True,
        "showOwner": True,
        "showPreviousTransaction": True,
        "showDisplay": False,
        "showContent": True,
        "showBcs": False,
        "showStorageRebate": True
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sui_getObject",
        "params": [gas_object, additional_params]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            data = response.json().get('result', {}).get('data', {})
            obj_type = data.get('type', '')
            if obj_type.startswith("0x2::coin::Coin<0x2::sui::SUI>"):
                balance = int(data.get('content', {}).get('fields', {}).get('balance', 0))
                formatted_balance = format_number(balance / 1_000_000_000)
                # Table formatting
                id_col = 66
                balance_col = 18
                sep = f"+{'-'*id_col}+{'-'*balance_col}+"
                print("Gas Object Balance:")
                print(sep)
                print(f"| {'Gas Object ID':<{id_col}}| {'Balance (SUI)':>{balance_col}}|")
                print(sep)
                print(f"| {gas_object:<{id_col}}| {formatted_balance:>{balance_col}}|")
                print(sep)
            else:
                print(f"Object {gas_object} is not a SUI Coin object.")
        else:
            print(f"Error fetching object info from the API. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error checking gas balance: {str(e)}")

def get_token_balances():
    """
    Gets and displays the SUI token balance for the address in a nice table format (English output)
    """
    address = os.getenv("SUI_ADDRESS")
    if not address:
        print("SUI_ADDRESS not found in .env file.")
        return

    url = "https://fullnode.mainnet.sui.io:443"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "suix_getAllBalances",
        "params": [address]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            balances = response.json().get('result', [])
            if not balances:
                print("No tokens found for this address.")
                return

            # Table formatting
            token_col = 10
            type_col = 40
            balance_col = 18
            sep = f"+{'-'*token_col}+{'-'*type_col}+{'-'*balance_col}+"
            print("SUI Token Balance:")
            print(sep)
            print(f"| {'Token':<{token_col}}| {'Type':<{type_col}}| {'Balance (SUI)':>{balance_col}}|")
            print(sep)
            for balance in balances:
                coin_type = balance.get('coinType', 'Unknown')
                total_balance = int(balance.get('totalBalance', 0))
                if coin_type == "0x2::sui::SUI":
                    formatted_balance = format_number(total_balance / 1_000_000_000)
                    print(f"| {'SUI':<{token_col}}| {coin_type:<{type_col}}| {formatted_balance:>{balance_col}}|")
            print(sep)
        else:
            print("Error fetching balances from the API.")
    except Exception as e:
        print(f"Error: {str(e)}")
