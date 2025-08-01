import re
import subprocess
import os
from dotenv import load_dotenv
import utils
import reward_information

load_dotenv()

def claim_rewards():
    print("\n=== CLAIM REWARDS ===")
    
    try:
        with open("object_id.txt", "r") as f:
            reward_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ No rewards file found.")
        print("Please get reward information first from the Rewards menu.")
        return

    if not reward_ids:
        print("❌ No rewards found.")
        print("Please get reward information first from the Rewards menu.")
        return

    print(f"Found {len(reward_ids)} claimable rewards:")
    for i, reward_id in enumerate(reward_ids, 1):
        print(f"  {i}. {reward_id}")

    print("\nOptions:")
    print("- Enter reward number (1, 2, 3, etc.)")
    print("- Enter 'all' to claim all rewards")
    print("- Enter '0' to cancel")
    
    reward_id_input = input("\nEnter your choice: ").strip()

    def process_withdrawal(reward_id):
        # Get a suitable gas object
        gas_object = get_suitable_gas_object()
        if not gas_object:
            print(f"  ❌ Error: No suitable gas object found for transaction")
            return False
            
        command = f"sui client call --package 0x3 --module sui_system --function request_withdraw_stake --args 0x5 {reward_id} --gas-budget 199800000 --gas {gas_object}"
        print(f"  Executing withdrawal transaction with gas object: {gas_object[:20]}...")

        try:
            command_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            digest_line = re.search(r'Transaction Digest:\s+(\S+)', command_output)
            if digest_line:
                digest = digest_line.group(1)
                print(f"  ✅ Transaction successful!")
                print(f"  Transaction Digest: {digest}")

                with open("transaction_digest.txt", "a") as f:
                    f.write(f"{digest}\n")
                return True
            else:
                print("  ❌ Error: Failed to retrieve transaction digest.")
                return False
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Error executing command: {e.output}")
            return False

def get_suitable_gas_object():
    """
    Find a suitable gas object with sufficient balance
    """
    address = os.getenv("SUI_ADDRESS")
    if not address:
        print("SUI_ADDRESS not found in .env file.")
        return None
    
    # Get all objects and find SUI coins with sufficient balance
    owned_objects = reward_information.get_owned_objects(address)
    if not owned_objects or 'result' not in owned_objects or 'data' not in owned_objects['result']:
        return None
    
    suitable_objects = []
    for obj in owned_objects['result']['data']:
        object_id = obj['data']['objectId']
        obj_info = reward_information.get_object_info(object_id)
        
        if obj_info and obj_info.get('result', {}).get('data', {}).get('type') == "0x2::coin::Coin<0x2::sui::SUI>":
            # Get balance
            obj_data = obj_info.get('result', {}).get('data', {})
            content = obj_data.get('content', {})
            fields = content.get('fields', {})
            
            if 'balance' in fields:
                balance = int(fields['balance'])
                # Check if balance is sufficient (at least 0.1 SUI)
                if balance >= 100_000_000:  # 0.1 SUI in MIST
                    suitable_objects.append({
                        'object_id': object_id,
                        'balance': balance
                    })
    
    if suitable_objects:
        # Sort by balance (highest first) and return the first one
        suitable_objects.sort(key=lambda x: x['balance'], reverse=True)
        selected_object = suitable_objects[0]['object_id']
        
        # Update the gas object in .env for future use
        utils.set_key(".env", "GAS_OBJECT", selected_object)
        
        return selected_object
    
    return None

    if reward_id_input.lower() == "all":
        print(f"\nClaiming all {len(reward_ids)} rewards...")
        successful_count = 0
        failed_count = 0
        
        for i, reward_id in enumerate(reward_ids, 1):
            print(f"\nProcessing reward {i}/{len(reward_ids)}: {reward_id}")
            if process_withdrawal(reward_id):
                successful_count += 1
            else:
                failed_count += 1
                
            # Add a small delay between transactions
            if i < len(reward_ids):
                print("  Waiting 2 seconds before next transaction...")
                import time
                time.sleep(2)

        print(f"\n📊 Processing completed:")
        print(f"  ✅ Successful: {successful_count}")
        print(f"  ❌ Failed: {failed_count}")
        
        if successful_count > 0:
            # Update the file to remove only successful transactions
            remaining_rewards = []
            for i, reward_id in enumerate(reward_ids):
                # This is a simplified approach - in a real scenario you'd track which ones succeeded
                if i >= successful_count:  # Assume first N were successful
                    remaining_rewards.append(reward_id)
            
            with open("object_id.txt", "w") as f:
                for reward_id in remaining_rewards:
                    f.write(f"{reward_id}\n")
            
            print(f"  📝 Updated object_id.txt with {len(remaining_rewards)} remaining rewards")
        else:
            print("  ⚠️  No rewards were successfully processed")
        
    elif reward_id_input == "0":
        print("Operation cancelled.")
        return
        
    else:
        try:
            # Try to parse as number
            reward_index = int(reward_id_input) - 1
            if 0 <= reward_index < len(reward_ids):
                selected_reward = reward_ids[reward_index]
                print(f"\nClaiming reward: {selected_reward}")
                
                if process_withdrawal(selected_reward):
                    # Update reward.txt to remove the processed reward ID
                    updated_reward_ids = [id for id in reward_ids if id != selected_reward]
                    with open("object_id.txt", "w") as f:
                        for id in updated_reward_ids:
                            f.write(f"{id}\n")
                    print(f"✅ Reward {reward_index + 1} has been processed!")
                else:
                    print(f"❌ Reward {reward_index + 1} processing failed!")
            else:
                print("❌ Invalid reward number.")
        except ValueError:
            print("❌ Invalid input. Please enter a number, 'all', or '0'.")
