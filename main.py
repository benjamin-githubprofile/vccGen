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
            if not cap_one_username or not cap_one_password:
                print("Error: Missing Capital One credentials in .env file")
                print("Please ensure CAPITAL_ONE_USERNAME and CAPITAL_ONE_PASSWORD are set")
                return
                
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
                username=cap_one_username,
                password=cap_one_password,
                headless=False,  # Set to True to run in headless mode
                num_cards=num_cards
            )
            
            # Run the automation
            await automation.login()
            
            print(f"Successfully completed automation. Generated {num_cards} Capital One virtual cards.")
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