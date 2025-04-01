import asyncio
from capOne.capOne import CapitalOneAutomation
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

async def main():
    # Get credentials from environment variables
    cap_one_username = os.getenv('CAPITAL_ONE_USERNAME')
    cap_one_password = os.getenv('CAPITAL_ONE_PASSWORD')
    cap_one_username_2 = os.getenv('CAPITAL_ONE_USERNAME_2')
    cap_one_password_2 = os.getenv('CAPITAL_ONE_PASSWORD_2')
    relay_username = os.getenv('RELAY_USERNAME')
    relay_password = os.getenv('RELAY_PASSWORD')
    
    # Ask user to choose a bank
    while True:
        print("\nWhich bank would you like to use?")
        print("1. Capital One")
        print("2. Relay")
        choice = input("Enter your choice (1 or 2): ")
        
        if choice == '1':
            # Capital One flow
            # Added profile selection
            while True:
                print("\nWhich Capital One profile would you like to use?")
                print("1. Profile 1")
                print("2. Profile 2")
                profile_choice = input("Enter your choice (1 or 2): ")
                
                if profile_choice == '1':
                    if not cap_one_username or not cap_one_password:
                        print("Error: Missing Capital One profile 1 credentials in .env file")
                        print("Please ensure CAPITAL_ONE_USERNAME and CAPITAL_ONE_PASSWORD are set")
                        return
                    active_username = cap_one_username
                    active_password = cap_one_password
                    break
                elif profile_choice == '2':
                    if not cap_one_username_2 or not cap_one_password_2:
                        print("Error: Missing Capital One profile 2 credentials in .env file")
                        print("Please ensure CAPITAL_ONE_USERNAME_2 and CAPITAL_ONE_PASSWORD_2 are set")
                        return
                    active_username = cap_one_username_2
                    active_password = cap_one_password_2
                    break
                else:
                    print("Invalid choice. Please enter 1 for Profile 1 or 2 for Profile 2.")
            
            # Add new selection for create or delete cards
            print("\nWhat would you like to do?")
            print("1. Create virtual cards")
            print("2. Delete cards")
            cap_one_action = input("Enter your choice (1 or 2): ")
            
            if cap_one_action == '1':
                # Create cards flow
                # Ask user for the number of cards to generate
                while True:
                    try:
                        num_cards = int(input("How many virtual cards would you like to generate? "))
                        if num_cards > 0:
                            break
                        else:
                            print("Please enter a positive number.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                print(f"Starting automation to generate {num_cards} Capital One virtual cards...")
                
                # Create instance of CapitalOneAutomation
                automation = CapitalOneAutomation(
                    username=active_username,
                    password=active_password,
                    headless=False,  # Set to True to run in headless mode
                    num_cards=num_cards
                )
                
                # Run the automation
                await automation.login()
                
                print(f"Successfully completed automation. Generated {num_cards} Capital One virtual cards.")
            
            elif cap_one_action == '2':
                # Delete cards flow
                # Ask user for the number of cards to delete
                while True:
                    try:
                        num_cards = int(input("How many cards would you like to delete? "))
                        if num_cards > 0:
                            break
                        else:
                            print("Please enter a positive number.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                # Card selection only for Profile 1
                card_choice = None
                if profile_choice == '1':
                    # Ask user which card they want to use for Profile 1
                    print("\nWhich card would you like to use?")
                    print("1. Card ending in 8060 (Savor)")
                    print("2. Card ending in 2653 (Platinum)")
                    
                    while True:
                        card_choice = input("Enter your choice (1 or 2): ")
                        if card_choice in ['1', '2']:
                            break
                        else:
                            print("Invalid choice. Please enter 1 for 8060 or 2 for 2653.")
                    
                    print(f"Starting automation to delete {num_cards} Capital One virtual cards from card ending in {card_choice=='1' and '8060' or '2653'}...")
                else:
                    # Profile 2 doesn't need card selection
                    print(f"Starting automation to delete {num_cards} Capital One virtual cards from Profile 2...")
                
                # Create instance of CapitalOneAutomation
                automation = CapitalOneAutomation(
                    username=active_username,
                    password=active_password,
                    headless=False,
                    num_cards=num_cards,
                    card_choice=card_choice,  # This will be None for Profile 2
                    profile=profile_choice  # Pass the profile choice to the class
                )
                
                # Run the automation for card deletion
                await automation.delete_cards()
                
                print(f"Successfully completed automation. Deleted {num_cards} Capital One virtual cards.")
            
            else:
                print("Invalid choice. Please enter 1 for creating cards or 2 for deleting cards.")
                continue
            
            break
            
        elif choice == '2':
            # Relay flow
            from relay.relay import RelayAutomation
            
            if not relay_username or not relay_password:
                print("Error: Missing Relay credentials in .env file")
                print("Please ensure RELAY_USERNAME and RELAY_PASSWORD are set")
                return
            
            # Add new selection for create or delete cards
            print("\nWhat would you like to do?")
            print("1. Create virtual cards")
            print("2. Delete cards")
            relay_action = input("Enter your choice (1 or 2): ")
            
            if relay_action == '1':
                # Create cards flow
                # Ask user for the number of cards to generate
                while True:
                    try:
                        num_cards = int(input("How many virtual cards would you like to generate? "))
                        if num_cards > 0:
                            break
                        else:
                            print("Please enter a positive number.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                print(f"Starting automation to generate {num_cards} Relay virtual cards...")
                
                # Create instance of RelayAutomation
                automation = RelayAutomation(
                    username=relay_username,
                    password=relay_password,
                    headless=False,  # Set to True to run in headless mode
                    num_cards=num_cards
                )
                
                # Run the automation for card creation
                await automation.login()
                
                print(f"Successfully completed automation. Generated {num_cards} Relay virtual cards.")
                
            elif relay_action == '2':
                # Delete cards flow
                # Ask user for the number of cards to delete
                while True:
                    try:
                        num_cards = int(input("How many cards would you like to delete? "))
                        if num_cards > 0:
                            break
                        else:
                            print("Please enter a positive number.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                print(f"Starting automation to delete {num_cards} Relay virtual cards...")
                
                # Create instance of RelayAutomation
                automation = RelayAutomation(
                    username=relay_username,
                    password=relay_password,
                    headless=False,
                    num_cards=num_cards
                )
                
                # Run the automation for card deletion
                await automation.delete_cards()
                
                print(f"Successfully completed automation. Deleted {num_cards} Relay virtual cards.")
            
            else:
                print("Invalid choice. Please enter 1 for creating cards or 2 for deleting cards.")
                continue
            
            break
            
        else:
            print("Invalid choice. Please enter 1 for Capital One or 2 for Relay.")

if __name__ == '__main__':
    asyncio.run(main())