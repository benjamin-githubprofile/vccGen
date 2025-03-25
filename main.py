import asyncio
from capOne.capOne import CapitalOneAutomation
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

async def main():
    # Get credentials from environment variables
    username = os.getenv('CAPITAL_ONE_USERNAME')
    password = os.getenv('CAPITAL_ONE_PASSWORD')
    
    if not username or not password:
        print("Error: Missing credentials in .env file")
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
    
    print(f"Starting automation to generate {num_cards} virtual cards...")
    
    # Create instance of CapitalOneAutomation
    automation = CapitalOneAutomation(
        username=username,
        password=password,
        headless=False,  # Set to True to run in headless mode
        num_cards=num_cards
    )
    
    # Run the automation
    await automation.login()
    
    print(f"Successfully completed automation. Generated {num_cards} virtual cards.")

if __name__ == '__main__':
    asyncio.run(main())