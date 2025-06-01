import reward_information
import claim_rewards
import send_rewards
import vote_for_gas
import utils

def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Get Reward Information")
        print("2. Claim Rewards")
        print("3. Send Rewards to Address")
        print("4. Vote for Gas Price")
        print("5. Show Token Balances")
        print("6. Check Gas Object Balance")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            reward_information.get_reward_information()
        elif choice == "2":
            claim_rewards.claim_rewards()
        elif choice == "3":
            send_rewards.execute_send_rewards_process()
        elif choice == "4":
            vote_for_gas.vote_for_gas_price()
        elif choice == "5":
            utils.get_token_balances()
        elif choice == "6":
            utils.check_gas_balance()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")

# Run the main menu
if __name__ == "__main__":
    main_menu()
