#!/usr/bin/env python3
"""
Test script for the new menu structure
"""

import main

def test_menu_structure():
    print("Testing new menu structure...")
    print("=" * 50)
    
    # Test the main menu
    print("Starting main menu test...")
    print("Note: This will start the interactive menu.")
    print("You can test the navigation and functionality.")
    print("=" * 50)
    
    # Start the main menu
    main.main_menu()

if __name__ == "__main__":
    test_menu_structure() 