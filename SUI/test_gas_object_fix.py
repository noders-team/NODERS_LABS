#!/usr/bin/env python3
"""
Test script for gas object fix
"""

import claim_rewards
import os
from dotenv import load_dotenv

load_dotenv()

def test_gas_object_fix():
    print("Testing gas object fix...")
    print("=" * 50)
    
    # Check if SUI_ADDRESS is set
    address = os.getenv("SUI_ADDRESS")
    if not address:
        print("❌ SUI_ADDRESS not found in .env file.")
        print("Please set your SUI address in the .env file first.")
        return
    
    print(f"Testing with address: {address}")
    print("=" * 50)
    
    # Test finding suitable gas object
    print("\n1. Testing gas object detection...")
    gas_object = claim_rewards.get_suitable_gas_object()
    
    if gas_object:
        print(f"✅ Found suitable gas object: {gas_object}")
        print(f"   This object will be used for transactions")
    else:
        print("❌ No suitable gas object found")
        print("   Make sure you have SUI tokens with balance >= 0.1 SUI")
    
    print("\n" + "=" * 50)
    print("Testing completed!")

if __name__ == "__main__":
    test_gas_object_fix() 