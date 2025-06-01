import re
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

def vote_for_gas_price():
    object_cap_id = os.getenv("OBJECT_CAP_ID")
    if not object_cap_id:
        print("OBJECT_CAP_ID not found in .env file.")
        return

    gas_price = input("Enter the gas price for the next epoch: ")
    gas_object = os.getenv("GAS_OBJECT", "0x0eaef11be6a00b414cac2de32ace7286162845a9d6d013fc2cd53d665c35a85e")

    command = f"sui client call --package 0x3 --module sui_system --function request_set_gas_price --args 0x5 {object_cap_id} {gas_price} --gas-budget 199800000 --gas {gas_object}"

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, universal_newlines=True)
        print("Successfully voted for gas price.")
        digest_line = re.search(r'Transaction Digest:\s+(\S+)', output)
        if digest_line:
            digest = digest_line.group(1)
            print(f"Transaction Digest: {digest}")

            with open("transaction_digest.txt", "w") as f:
                f.write(digest)
        else:
            print("Error: Failed to retrieve transaction digest.")
    except subprocess.CalledProcessError:
        print("Failed to vote for gas price.")
