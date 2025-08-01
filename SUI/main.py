import os
import requests
import json
import reward_information
import claim_rewards
import send_rewards
import vote_for_gas
import utils

# Пример вызова функции для вывода всех объектов с типом и балансом:
# send_rewards.print_all_objects_info(utils.os.getenv("SUI_ADDRESS"))

def show_current_status():
    """Display current network and balances"""
    print("=" * 50)
    print("Welcome to the SUI Node Utility CLI!\n")
    
    # Show current network
    network = os.getenv("SUI_NETWORK", "not selected")
    print(f"Current network: {network}")
    print("-" * 50)
    
    # Get total SUI balance
    address = os.getenv("SUI_ADDRESS")
    total_balance = 0
    gas_balance = 0
    
    if address:
        url = utils.get_network_rpc_url()
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
                for balance in balances:
                    coin_type = balance.get('coinType', '')
                    if coin_type == "0x2::sui::SUI":
                        total_balance = int(balance.get('totalBalance', 0)) / 1_000_000_000
                        break
        except:
            pass
    
    # Get gas object balance
    gas_object = os.getenv("GAS_OBJECT")
    if gas_object:
        url = utils.get_network_rpc_url()
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sui_getObject",
            "params": [gas_object, {
                "showType": True,
                "showOwner": True,
                "showPreviousTransaction": True,
                "showDisplay": False,
                "showContent": True,
                "showBcs": False,
                "showStorageRebate": True
            }]
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                data = response.json().get('result', {}).get('data', {})
                obj_type = data.get('type', '')
                if obj_type.startswith("0x2::coin::Coin<0x2::sui::SUI>"):
                    gas_balance = int(data.get('content', {}).get('fields', {}).get('balance', 0)) / 1_000_000_000
        except:
            pass
    
    print(f"Your current balances: {utils.format_number(total_balance)}")
    print("-" * 50)
    print(f"Gas Object Balance: {utils.format_number(gas_balance)}")
    print("=" * 50)

def rewards_menu():
    """Rewards submenu"""
    while True:
        print("\n=== REWARDS MENU ===")
        print("[1] Get reward list from wallet")
        print("[2] Show rewards on wallet")
        print("[3] Claim rewards")
        print("[4] Send rewards")
        print("[0] Back to main menu")
        print("-" * 20)
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            reward_information.get_reward_information()
        elif choice == "2":
            show_rewards_details()
        elif choice == "3":
            claim_rewards.claim_rewards()
        elif choice == "4":
            send_rewards_menu()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")

def send_rewards_menu():
    """Send rewards submenu with address options"""
    print("\n=== SEND REWARDS ===")
    print("[1] Use permanent withdrawal address")
    print("[2] Enter custom address")
    print("[0] Back to rewards menu")
    print("-" * 20)
    
    choice = input("Enter your choice: ").strip()
    
    if choice == "1":
        # Use permanent address from .env
        send_rewards.execute_send_rewards_process()
    elif choice == "2":
        # Enter custom address
        custom_address = input("Enter recipient address: ").strip()
        if custom_address:
            # Temporarily set custom address and send
            utils.set_key(".env", "RECIPIENT_ADDRESS", custom_address)
            send_rewards.execute_send_rewards_process()
        else:
            print("Invalid address.")
    elif choice == "0":
        return
    else:
        print("Invalid choice. Please try again.")

def gas_menu():
    """Gas submenu"""
    while True:
        print("\n=== GAS MENU ===")
        
        # Show current gas object and balance
        gas_object = os.getenv("GAS_OBJECT")
        if gas_object:
            print(f"Current gas object: {gas_object}")
            # Show gas object balance
            utils.check_gas_balance()
        else:
            print("No gas object set")
        
        print("-" * 40)
        print("[1] Vote for gas price")
        print("[2] Set gas object")
        print("[3] Show suitable tokens for gas object")
        print("[0] Back to main menu")
        print("-" * 20)
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            vote_for_gas.vote_for_gas_price()
        elif choice == "2":
            utils.replace_gas_object_cli()
        elif choice == "3":
            show_suitable_gas_tokens()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")

def show_suitable_gas_tokens():
    """Show suitable tokens that can be used as gas object"""
    address = os.getenv("SUI_ADDRESS")
    if not address:
        print("SUI_ADDRESS not found in .env file.")
        return
    
    current_gas_object = os.getenv("GAS_OBJECT")
    
    print("\n=== SUITABLE GAS TOKENS ===")
    if current_gas_object:
        print(f"Current gas object: {current_gas_object}")
        print("(marked with ⭐)")
    print("Showing SUI tokens that can be used as gas object:")
    print("-" * 40)
    
    # Get all objects and filter for SUI coins
    objects = send_rewards.get_all_objects_with_type_and_balance(address)
    sui_objects = [obj for obj in objects if obj['type'] == "0x2::coin::Coin<0x2::sui::SUI>" and obj['balance'] is not None]
    
    if sui_objects:
        # Sort by balance
        sui_objects.sort(key=lambda x: x['balance'], reverse=True)
        
        print(f"Found {len(sui_objects)} SUI coin objects:")
        print("-" * 80)
        
        for i, obj in enumerate(sui_objects, 1):
            obj_id = obj['objectId']
            balance = utils.format_number(obj['balance'] / 1_000_000_000)
            
            # Mark current gas object
            if obj_id == current_gas_object:
                print(f"{i:2d}. ⭐ {obj_id} - {balance} SUI (CURRENT)")
            else:
                print(f"{i:2d}.    {obj_id} - {balance} SUI")
    else:
        print("No SUI coin objects found.")

def balance_menu():
    """Balance submenu"""
    while True:
        print("\n=== BALANCE MENU ===")
        print("[1] Show tokens on address")
        print("[2] Show claimable rewards amount")
        print("[0] Back to main menu")
        print("-" * 20)
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            utils.get_token_balances()
        elif choice == "2":
            show_claimable_rewards()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")

def show_rewards_details():
    """Show detailed information about rewards on wallet"""
    address = os.getenv("SUI_ADDRESS")
    if not address:
        print("SUI_ADDRESS not found in .env file.")
        return
    
    print("\n=== REWARDS ON WALLET ===")
    print("Fetching detailed reward information...")
    
    # Get owned objects and filter for StakedSui
    owned_objects = reward_information.get_owned_objects(address)
    if owned_objects and 'result' in owned_objects and 'data' in owned_objects['result']:
        staked_objects = []
        print(f"\nAnalyzing {len(owned_objects['result']['data'])} objects...")
        
        for i, obj in enumerate(owned_objects['result']['data'], 1):
            object_id = obj['data']['objectId']
            print(f"  Checking object {i}/{len(owned_objects['result']['data'])}: {object_id[:20]}...")
            
            obj_info = reward_information.get_object_info(object_id)
            if obj_info and obj_info.get('result', {}).get('data', {}).get('type') == "0x3::staking_pool::StakedSui":
                staked_objects.append({
                    'object_id': object_id,
                    'info': obj_info
                })
        
        if staked_objects:
            print(f"\n✅ Found {len(staked_objects)} staking reward objects:")
            print("-" * 80)
            
            for i, reward in enumerate(staked_objects, 1):
                obj_id = reward['object_id']
                obj_data = reward['info'].get('result', {}).get('data', {})
                
                print(f"\n{i}. Reward Object ID: {obj_id}")
                print(f"   Type: {obj_data.get('type', 'Unknown')}")
                
                # Try to get additional details if available
                content = obj_data.get('content', {})
                fields = content.get('fields', {})
                
                if 'principal' in fields:
                    principal = int(fields['principal']) / 1_000_000_000
                    print(f"   Principal: {utils.format_number(principal)} SUI")
                
                if 'sui_token_lock' in fields:
                    lock = fields['sui_token_lock']
                    print(f"   Token Lock: {lock}")
                
                if 'validator_address' in fields:
                    validator = fields['validator_address']
                    print(f"   Validator: {validator}")
                
                print(f"   Owner: {obj_data.get('owner', 'Unknown')}")
                
        else:
            print("\n❌ No staking rewards found on this wallet.")
            print("This wallet doesn't have any staked SUI tokens.")
    else:
        print("❌ Error fetching objects or no objects found.")

def show_claimable_rewards():
    """Show amount of rewards that can be claimed"""
    address = os.getenv("SUI_ADDRESS")
    if not address:
        print("SUI_ADDRESS not found in .env file.")
        return
    
    print("\n=== CLAIMABLE REWARDS SUMMARY ===")
    print("Checking for claimable rewards...")
    
    # Get owned objects and filter for StakedSui
    owned_objects = reward_information.get_owned_objects(address)
    if owned_objects and 'result' in owned_objects and 'data' in owned_objects['result']:
        staked_objects = []
        total_principal = 0
        
        print(f"\nAnalyzing {len(owned_objects['result']['data'])} objects for staking rewards...")
        
        for obj in owned_objects['result']['data']:
            object_id = obj['data']['objectId']
            obj_info = reward_information.get_object_info(object_id)
            if obj_info and obj_info.get('result', {}).get('data', {}).get('type') == "0x3::staking_pool::StakedSui":
                staked_objects.append(object_id)
                
                # Calculate total principal
                obj_data = obj_info.get('result', {}).get('data', {})
                content = obj_data.get('content', {})
                fields = content.get('fields', {})
                
                if 'principal' in fields:
                    principal = int(fields['principal'])
                    total_principal += principal
        
        if staked_objects:
            total_sui = total_principal / 1_000_000_000
            print(f"\n✅ Found {len(staked_objects)} claimable reward objects")
            print(f"📊 Total staked amount: {utils.format_number(total_sui)} SUI")
            print(f"💰 Estimated rewards: Available for withdrawal")
            print("\nReward object IDs:")
            for i, obj_id in enumerate(staked_objects, 1):
                print(f"  {i}. {obj_id}")
            
            print(f"\n💡 Use 'Claim rewards' option to withdraw these rewards")
        else:
            print("\n❌ No claimable rewards found.")
            print("This wallet doesn't have any staked SUI tokens.")
    else:
        print("❌ Error fetching objects or no objects found.")

def main_menu():
    """Main menu with submenus"""
    show_current_status()
    
    while True:
        print("\n=== MAIN MENU ===")
        print("[1] Rewards")
        print("[2] Gas")
        print("[3] Balance")
        print("[4] Change Network")
        print("[0] Exit")
        print("-" * 20)
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            rewards_menu()
        elif choice == "2":
            gas_menu()
        elif choice == "3":
            balance_menu()
        elif choice == "4":
            new_network = utils.change_network()
            print(f"Network changed to: {new_network}")
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the main menu
if __name__ == "__main__":
    main_menu()
