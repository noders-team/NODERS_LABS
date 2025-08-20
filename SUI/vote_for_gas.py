import re
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

def vote_for_gas_price():
    print("\n=== VOTE FOR GAS PRICE ===")
    
    object_cap_id = os.getenv("OBJECT_CAP_ID")
    if not object_cap_id:
        print("❌ OBJECT_CAP_ID not found in .env file.")
        print("Please set your validator object capability ID in the .env file.")
        return

    print("Enter the gas price you want to vote for in the next epoch.")
    print("Gas price should be in MIST (1 SUI = 1,000,000,000 MIST)")
    print("-" * 40)
    
    gas_price = input("Enter gas price (in MIST): ").strip()
    if not gas_price.isdigit():
        print("❌ Invalid gas price. Please enter a number.")
        return
    
    gas_object = os.getenv("GAS_OBJECT", "0x0eaef11be6a00b414cac2de32ace7286162845a9d6d013fc2cd53d665c35a85e")

    command = f"sui client call --package 0x3 --module sui_system --function request_set_gas_price --args 0x5 {object_cap_id} {gas_price} --gas-budget 10000000 --gas {gas_object}"

    print(f"\nSubmitting gas price vote: {gas_price} MIST")
    print("Executing transaction...")

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, universal_newlines=True)
        print("✅ Successfully voted for gas price!")
        digest_line = re.search(r'Transaction Digest:\s+(\S+)', output)
        if digest_line:
            digest = digest_line.group(1)
            print(f"Transaction Digest: {digest}")

            with open("transaction_digest.txt", "w") as f:
                f.write(digest)
        else:
            print("❌ Error: Failed to retrieve transaction digest.")
    except subprocess.CalledProcessError:
        print("❌ Failed to vote for gas price.")
        print("Please check your gas object balance and try again.")
