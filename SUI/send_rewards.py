import json
import os
import re
import subprocess
import requests
import time
from dotenv import load_dotenv, set_key
import utils
from utils import format_number
from tabulate import tabulate

load_dotenv()

def execute_send_rewards_process():
    # Получение информации о наградах больше не нужна, убираем вызов get_reward_information()
    # Отправка наград
    send_rewards_to_address()

def get_owned_objects(address):
    """
    Fetches all objects owned by a given address from the Sui network.
    """
    url = utils.get_network_rpc_url()
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "suix_getOwnedObjects",
        "params": [address]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data from the API")
        return None

def request_address():
    """
    Requests the Sui address from the user and saves it to the .env file.
    """
    address = input("Please enter the Sui address: ")
    set_key(".env", "RECIPIENT_ADDRESS", address)
    return address

def get_object_info(object_id):
    """
    Fetches detailed information about a specific object from the Sui network using sui_getObject.
    Includes additional parameters to retrieve more details about the object.
    """
    url = utils.get_network_rpc_url()
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
        "params": [object_id, additional_params]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        object_data = response.json().get('result', {}).get('data', {})
        balance = int(object_data.get('content', {}).get('fields', {}).get('balance', 0))
        return object_data, balance
    else:
        print(f"Error fetching data for object ID {object_id} from the API")
        return None, 0

def get_reward_information():
    """
    Gets reward information for a given Sui address and processes each object ID.
    """
    address = os.getenv("RECIPIENT_ADDRESS") or request_address()
    owned_objects = get_owned_objects(address)
    if owned_objects:
        object_ids = [obj['data']['objectId'] for obj in owned_objects['result']['data']]
        print("Filtered object IDs saved to reward_for_send.txt")
    else:
        print("No data to save")

def send_rewards_to_address():
    recipient_address = os.getenv("RECIPIENT_ADDRESS")
    if not recipient_address:
        print("RECIPIENT_ADDRESS not found in .env file.")
        return

    address = os.getenv("SUI_ADDRESS")
    if not address:
        print("SUI_ADDRESS not found in .env file.")
        return

    # Получаем все объекты с типом и балансом
    objects = get_all_objects_with_type_and_balance(address)
    
    # Получаем газовый объект для исключения
    gas_object = os.getenv("GAS_OBJECT")
    
    # Фильтруем только SUI Coin с балансом > 5 SUI, исключая газовый объект
    filtered = []
    for obj in objects:
        if (obj['type'] == "0x2::coin::Coin<0x2::sui::SUI>" and 
            obj['balance'] is not None and 
            obj['balance'] > 5_000_000_000 and
            obj['objectId'] != gas_object):
            filtered.append(obj)

    if not filtered:
        print("No suitable SUI Coin objects with balance > 5 SUI to send.")
        return

    total_balance = sum(obj['balance'] for obj in filtered) / 1_000_000_000
    print(f"\nReady to send {len(filtered)} SUI Coin objects.")
    print(f"Total balance to send: {format_number(total_balance)} SUI")
    print(f"Recipient address: {recipient_address}")
    confirm = input("Proceed with sending? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled by user.")
        return

    sent_objects = []
    for obj in filtered:
        object_id = obj['objectId']
        time.sleep(5)
        gas_object = os.getenv("GAS_OBJECT", "0x0eaef11be6a00b414cac2de32ace7286162845a9d6d013fc2cd53d665c35a85e")
        command = f"sui client transfer --to {recipient_address} --object-id {object_id} --gas-budget 199800000 --gas {gas_object}"
        print(f"Sending object {object_id} to {recipient_address}...")
        try:
            command_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            digest_line = re.search(r'Transaction Digest:\s+(\S+)', command_output)
            if digest_line:
                digest = digest_line.group(1)
                print(f"Transaction Digest: {digest}")
                with open("transaction_digest.txt", "a") as f:
                    f.write(f"{digest}\n")
                sent_objects.append(object_id)
            else:
                print(f"Error: Failed to retrieve transaction digest for object ID {object_id}.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing command for object ID {object_id}: {e.output}")

    if sent_objects:
        print(f"All rewards have been sent. Total sent: {len(sent_objects)}")
        print("Sent object IDs:")
        for obj in sent_objects:
            print(f"- {obj}")
    else:
        print("No objects were sent.")

def get_all_objects_with_type_and_balance(address):
    """
    Получает все объекты на адресе и определяет их type и balance (если есть).
    Возвращает список словарей: {'objectId', 'type', 'balance'}
    """
    url = utils.get_network_rpc_url()
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "suix_getOwnedObjects",
        "params": [address]
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print("Error fetching data from the API")
        return []
    owned_objects = response.json().get('result', {}).get('data', [])
    result = []
    for obj in owned_objects:
        object_id = obj['data']['objectId']
        # Получаем подробную инфу по объекту
        obj_info_url = utils.get_network_rpc_url()
        obj_info_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sui_getObject",
            "params": [object_id, {
                "showType": True,
                "showOwner": True,
                "showPreviousTransaction": True,
                "showDisplay": False,
                "showContent": True,
                "showBcs": False,
                "showStorageRebate": True
            }]
        }
        obj_info_resp = requests.post(obj_info_url, headers=headers, data=json.dumps(obj_info_payload))
        if obj_info_resp.status_code == 200:
            data = obj_info_resp.json().get('result', {}).get('data', {})
            obj_type = data.get('type', None)
            balance = None
            if obj_type and obj_type.startswith("0x2::coin::Coin<0x2::sui::SUI>"):
                balance = int(data.get('content', {}).get('fields', {}).get('balance', 0))
            result.append({
                'objectId': object_id,
                'type': obj_type,
                'balance': balance
            })
        else:
            result.append({
                'objectId': object_id,
                'type': None,
                'balance': None
            })
    return result

def print_all_objects_info(address):
    objects = get_all_objects_with_type_and_balance(address)
    # Оставляем только объекты с балансом (Coin<SUI>)
    filtered = [obj for obj in objects if obj['balance'] is not None]
    # Сортируем по балансу по убыванию
    filtered.sort(key=lambda x: x['balance'], reverse=True)
    table = []
    for obj in filtered:
        obj_id = obj['objectId']
        obj_type = obj['type'] if obj['type'] else "Unknown"
        if obj_type and len(obj_type) > 40:
            obj_type = obj_type[:37] + "..."
        balance = format_number(obj['balance'] / 1_000_000_000)
        table.append([obj_id, obj_type, balance])
    print("\nAll SUI Coin objects on address (sorted by balance):")
    print(tabulate(
        table,
        headers=["Object ID", "Type", "Balance (SUI)"],
        tablefmt="grid",
        numalign="right",
        stralign="left"
    ))
