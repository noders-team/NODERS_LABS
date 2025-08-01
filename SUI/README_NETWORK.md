# SUI Node Utility CLI - Network Selection & Menu Structure

## Overview

The SUI Node Utility CLI now supports network selection between **Mainnet** and **Testnet**, and features a new organized menu structure with main menus and submenus.

## Network Selection

### Automatic Network Selection
When you first run any script that uses RPC calls, the system will automatically request network selection:

```
Select network:
[1] Mainnet
[2] Testnet
Enter your choice (1 or 2):
```

### Saving Selection
The selected network is saved in the `.env` file in the `SUI_NETWORK` variable:
- `mainnet` - for main network
- `testnet` - for test network

### RPC URL
Depending on the selected network, the following RPC URLs are used:
- **Mainnet**: `https://fullnode.mainnet.sui.io:443`
- **Testnet**: `https://fullnode.testnet.sui.io:443`

## Menu Structure

### Main Menu
```
=== MAIN MENU ===
[1] Rewards
[2] Gas
[3] Balance
[4] Change Network
[0] Exit
```

### Rewards Submenu
```
=== REWARDS MENU ===
[1] Get reward list from wallet
[2] Show rewards on wallet
[3] Claim rewards
[4] Send rewards
[0] Back to main menu
```

#### Send Rewards Options
```
=== SEND REWARDS ===
[1] Use permanent withdrawal address
[2] Enter custom address
[0] Back to rewards menu
```

### Gas Submenu
```
=== GAS MENU ===
[1] Vote for gas price
[2] Set gas object
[3] Show suitable tokens for gas object
[0] Back to main menu
```

### Balance Submenu
```
=== BALANCE MENU ===
[1] Show tokens on address
[2] Show claimable rewards amount
[0] Back to main menu
```

## Features

### Rewards Management
- **Get reward list**: Fetches and filters staking rewards from your wallet, saves to file
- **Show rewards**: Displays detailed information about all staking rewards on your wallet
- **Claim rewards**: Withdraw individual or all available rewards (with automatic gas object detection)
- **Send rewards**: Transfer rewards to permanent or custom addresses

### Gas Management
- **Vote for gas price**: Submit gas price votes for the next epoch
- **Set gas object**: Configure which SUI token to use for gas fees
- **Show suitable tokens**: Display all SUI tokens that can be used as gas objects

### Balance Information
- **Show tokens**: Display all token balances on your address
- **Show claimable rewards**: Count and display summary of available rewards for withdrawal

## Usage

### Starting the Application
```bash
python main.py
```

### Testing Network Selection
```bash
python test_fix.py
```

### Testing Menu Structure
```bash
python test_menu.py
```

### Testing Rewards Display
```bash
python test_rewards_display.py
```

### Testing Gas Object Fix
```bash
python test_gas_object_fix.py
```

## Environment Variables

The following variables are used in the `.env` file:
- `SUI_NETWORK` - selected network (`mainnet` or `testnet`)
- `SUI_ADDRESS` - your SUI wallet address
- `RECIPIENT_ADDRESS` - permanent withdrawal address
- `GAS_OBJECT` - gas object ID for transactions
- `OBJECT_CAP_ID` - validator object capability ID for gas voting

## Updated Files

The following files have been updated for network support and new menu structure:

- `utils.py` - added network selection functions and improved gas object management
- `main.py` - completely restructured with new menu system
- `send_rewards.py` - updated to use selected network
- `reward_information.py` - updated to use selected network and improved display
- `claim_rewards.py` - improved user interface, error handling, and automatic gas object detection
- `vote_for_gas.py` - enhanced user interface and validation

## Notes

- Network selection is requested only once per session
- Network choice is saved between program runs
- If `SUI_NETWORK` variable is not set, the system will request network selection
- Invalid network values default to mainnet
- All menus and messages are now in English
- Improved error handling and user feedback throughout the application 