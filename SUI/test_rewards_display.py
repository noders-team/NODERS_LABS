#!/usr/bin/env python3
"""
Test script for rewards display functionality
"""

import main
import os
from dotenv import load_dotenv

load_dotenv()

def test_rewards_display():
    print("Testing rewards display functionality...")
    print("=" * 50)
    
    # Check if SUI_ADDRESS is set
    address = os.getenv("SUI_ADDRESS")
    if not address:
        print("❌ SUI_ADDRESS not found in .env file.")
        print("Please set your SUI address in the .env file first.")
        return
    
    print(f"Testing with address: {address}")
    print("=" * 50)
    
    # Test detailed rewards display
    print("\n1. Testing detailed rewards display...")
    main.show_rewards_details()
    
    print("\n" + "=" * 50)
    
    # Test claimable rewards summary
    print("\n2. Testing claimable rewards summary...")
    main.show_claimable_rewards()
    
    print("\n" + "=" * 50)
    print("Testing completed!")

if __name__ == "__main__":
    test_rewards_display() 