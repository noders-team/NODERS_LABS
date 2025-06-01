import re
import subprocess
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def format_number(number):
    return "{:,.2f}".format(number)

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
    Проверяет баланс gas object из .env файла
    """
    gas_object = os.getenv("GAS_OBJECT")
    if not gas_object:
        print("GAS_OBJECT not found in .env file.")
        return

    try:
        balance = check_object_balance(gas_object)
        if balance > 0:
            formatted_balance = balance / 1_000_000_000  # SUI has 9 decimals
            print("\nGas Object Balance:")
            print("-" * 50)
            print(f"Object ID: {gas_object}")
            print(f"Balance: {format_number(formatted_balance)} SUI")
            print("-" * 50)
        else:
            print(f"Error: Could not get balance for gas object {gas_object}")
    except Exception as e:
        print(f"Error checking gas balance: {str(e)}")

def get_token_balances():
    """
    Получает и отображает баланс SUI токенов на адресе в удобном формате
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
                print("No tokens found on this address.")
                return

            print("\nToken Balances:")
            print("-" * 50)
            
            for balance in balances:
                coin_type = balance.get('coinType', 'Unknown')
                total_balance = int(balance.get('totalBalance', 0))
                
                # Показываем только токены типа 0x2::sui::SUI
                if coin_type == "0x2::sui::SUI":
                    formatted_balance = total_balance / 1_000_000_000  # SUI has 9 decimals
                    print(f"Token: SUI")
                    print(f"Type: {coin_type}")
                    print(f"Balance: {format_number(formatted_balance)}")
                    print("-" * 50)

        else:
            print("Error fetching balances from the API")
    except Exception as e:
        print(f"Error: {str(e)}")
