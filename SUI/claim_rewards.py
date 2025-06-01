import re
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

def claim_rewards():
    try:
        with open("object_id.txt", "r") as f:
            reward_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("No rewards file found.")
        return

    if not reward_ids:
        print("No rewards found.")
        return

    print("Rewards:")
    for reward_id in reward_ids:
        print(reward_id)

    reward_id_input = input("Enter the reward ID to withdraw (or 'all' to withdraw all rewards): ")

    def process_withdrawal(reward_id):
        gas_object = os.getenv("GAS_OBJECT", "0x0eaef11be6a00b414cac2de32ace7286162845a9d6d013fc2cd53d665c35a85e")
        command = f"sui client call --package 0x3 --module sui_system --function request_withdraw_stake --args 0x5 {reward_id} --gas-budget 199800000 --gas {gas_object}"
        print(f"Withdrawing reward with ID: {reward_id}...")

        try:
            command_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            digest_line = re.search(r'Transaction Digest:\s+(\S+)', command_output)
            if digest_line:
                digest = digest_line.group(1)
                print(f"Transaction Digest: {digest}")

                with open("transaction_digest.txt", "a") as f:
                    f.write(f"{digest}\n")
            else:
                print("Error: Failed to retrieve transaction digest.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e.output}")

    if reward_id_input.lower() == "all":
        for reward_id in reward_ids:
            process_withdrawal(reward_id)

        # Clear the reward.txt file after processing all rewards
        with open("object_id.txt", "w") as f:
            pass
    else:
        if reward_id_input in reward_ids:
            process_withdrawal(reward_id_input)

            # Update reward.txt to remove the processed reward ID
            updated_reward_ids = [id for id in reward_ids if id != reward_id_input]
            with open("object_id.txt", "w") as f:
                for id in updated_reward_ids:
                    f.write(f"{id}\n")
        else:
            print("Invalid reward ID entered.")
