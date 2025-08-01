import os
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
    
    print("Your current balances:")
    print("-" * 50)
    utils.get_token_balances()
    utils.check_gas_balance()
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
            # Show rewards on wallet (same as option 1 for now)
            reward_information.get_reward_information()
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
    
    print("\n=== SUITABLE GAS TOKENS ===")
    print("Showing SUI tokens that can be used as gas object:")
    print("-" * 40)
    
    # Use the existing function to show all objects
    send_rewards.print_all_objects_info(address)

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

def show_claimable_rewards():
    """Show amount of rewards that can be claimed"""
    address = os.getenv("SUI_ADDRESS")
    if not address:
        print("SUI_ADDRESS not found in .env file.")
        return
    
    print("\n=== CLAIMABLE REWARDS ===")
    print("Checking for claimable rewards...")
    
    # Get owned objects and filter for StakedSui
    owned_objects = reward_information.get_owned_objects(address)
    if owned_objects and 'result' in owned_objects and 'data' in owned_objects['result']:
        staked_objects = []
        for obj in owned_objects['result']['data']:
            object_id = obj['data']['objectId']
            obj_info = reward_information.get_object_info(object_id)
            if obj_info and obj_info.get('result', {}).get('data', {}).get('type') == "0x3::staking_pool::StakedSui":
                staked_objects.append(object_id)
        
        if staked_objects:
            print(f"Found {len(staked_objects)} claimable reward objects:")
            for obj_id in staked_objects:
                print(f"  - {obj_id}")
        else:
            print("No claimable rewards found.")
    else:
        print("Error fetching objects or no objects found.")

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
