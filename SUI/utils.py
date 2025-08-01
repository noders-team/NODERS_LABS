import re
import subprocess
import requests
import json
from dotenv import load_dotenv, set_key
import os
from tabulate import tabulate

load_dotenv()

# Глобальная переменная для хранения выбранной сети в памяти
_selected_network = None

def get_network_rpc_url():
    """
    Получает RPC URL для выбранной сети из переменной окружения или запрашивает выбор сети
    """
    global _selected_network
    
    # Если сеть уже выбрана в памяти, используем её
    if _selected_network:
        if _selected_network.lower() == "testnet":
            return "https://fullnode.testnet.sui.io:443"
        elif _selected_network.lower() == "mainnet":
            return "https://fullnode.mainnet.sui.io:443"
        else:
            return "https://fullnode.mainnet.sui.io:443"
    
    # Проверяем переменную окружения
    network = os.getenv("SUI_NETWORK")
    if not network:
        network = select_network()
        set_key(".env", "SUI_NETWORK", network)
    
    # Сохраняем в памяти
    _selected_network = network
    
    if network.lower() == "testnet":
        return "https://fullnode.testnet.sui.io:443"
    elif network.lower() == "mainnet":
        return "https://fullnode.mainnet.sui.io:443"
    else:
        print(f"Неизвестная сеть: {network}. Используется mainnet по умолчанию.")
        return "https://fullnode.mainnet.sui.io:443"

def select_network():
    """
    Requests network selection from user
    """
    print("\nSelect network:")
    print("[1] Mainnet")
    print("[2] Testnet")
    
    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == "1":
            return "mainnet"
        elif choice == "2":
            return "testnet"
        else:
            print("Invalid choice. Please enter 1 or 2.")

def change_network():
    """
    Change network with update both in .env and memory
    """
    global _selected_network
    new_network = select_network()
    set_key(".env", "SUI_NETWORK", new_network)
    _selected_network = new_network
    return new_network

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

def replace_gas_object_cli():
    """
    Replace GAS_OBJECT in .env via CLI
    """
    print("\n=== SET GAS OBJECT ===")
    print("Enter the gas object ID that will be used for transactions.")
    print("This object must be a SUI coin with sufficient balance.")
    print("-" * 40)
    
    new_gas_object = input("Enter gas object ID: ").strip()
    if not (new_gas_object.startswith("0x") and len(new_gas_object) >= 10):
        print("Invalid object ID format. Must start with 0x and be a valid SUI object ID.")
        return
    
    set_key(".env", "GAS_OBJECT", new_gas_object)
    print(f"Gas object successfully updated to: {new_gas_object}")
    print("You can verify the gas object balance in the Balance menu.")

def check_gas_balance():
    """
    Checks the balance of the gas object from .env file via RPC and displays it in a nice format (English output)
    If balance < 0.1 SUI, offers to replace GAS_OBJECT automatically.
    """
    gas_object = os.getenv("GAS_OBJECT")
    if not gas_object:
        print("GAS_OBJECT not found in .env file.")
        return

    url = get_network_rpc_url()
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
                table = [[gas_object, formatted_balance]]
                print("Gas Object Balance:")
                print(tabulate(table, headers=["Gas Object ID", "Balance (SUI)"], tablefmt="grid", numalign="right", stralign="left"))
                # Check if balance is less than 0.1 SUI
                if (balance / 1_000_000_000) < 0.1:
                    print("\n⚠️  Warning: Your gas object balance is less than 0.1 SUI!")
                    print("This may cause transaction failures.")
                    answer = input("Would you like to set a new gas object now? (y/n): ").strip().lower()
                    if answer == 'y':
                        replace_gas_object_cli()
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

    url = get_network_rpc_url()
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

            table = []
            for balance in balances:
                coin_type = balance.get('coinType', 'Unknown')
                total_balance = int(balance.get('totalBalance', 0))
                if coin_type == "0x2::sui::SUI":
                    formatted_balance = format_number(total_balance / 1_000_000_000)
                    table.append(["SUI", coin_type, formatted_balance])
            if table:
                print("SUI Token Balance:")
                print(tabulate(table, headers=["Token", "Type", "Balance (SUI)"], tablefmt="grid", numalign="right", stralign="left"))
            else:
                print("No SUI tokens found for this address.")
        else:
            print("Error fetching balances from the API.")
    except Exception as e:
        print(f"Error: {str(e)}")
