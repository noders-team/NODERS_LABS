import reward_information
import claim_rewards
import send_rewards
import vote_for_gas
import utils

# Пример вызова функции для вывода всех объектов с типом и балансом:
# send_rewards.print_all_objects_info(utils.os.getenv("SUI_ADDRESS"))

def main_menu():
    print("=" * 50)
    print("Welcome to the SUI Node Utility CLI!\n")
    print("Your current balances:")
    print("-" * 50)
    utils.get_token_balances()
    utils.check_gas_balance()
    print("=" * 50)
    while True:
        print("\nMain Menu:")
        print("[1] Get Reward Information")
        print("[2] Claim Rewards")
        print("[3] Send Rewards to Address")
        print("[4] Vote for Gas Price")
        print("[5] Show SUI Token Balance")
        print("[6] Show Gas Object Balance")
        print("[7] Show All Objects (type & balance)")
        print("[0] Exit")
        print("-" * 50)
        choice = input("Please enter your choice: ")

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
        elif choice == "7":
            send_rewards.print_all_objects_info(utils.os.getenv("SUI_ADDRESS"))
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the main menu
if __name__ == "__main__":
    main_menu()
