import asyncio
import os
from playwright.async_api import async_playwright

class CapitalOneAutomation:
    def __init__(self, username, password, headless=False, num_cards=1, card_choice=None, profile='1'):
        self.username = username
        self.password = password
        self.headless = headless
        self.num_cards = num_cards  # Store the number of cards to generate
        self.card_choice = card_choice  # Store the card choice (1 for 8060, 2 for 2653)
        self.profile = profile  # Store which profile is being used (1 or 2)
        
    async def login(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Set a smaller zoom level to ensure more content is visible
            await page.evaluate('() => { document.body.style.zoom = "80%"; }')
            print("Set page zoom to 80% to ensure buttons are visible")
            
            # Navigate to Capital One login page
            await page.goto("https://verified.capitalone.com/auth/signin")
            
            # Wait for the page to load completely
            await page.wait_for_load_state("networkidle")
            
            # Find and fill username field
            username_field = await page.wait_for_selector('input[name="username"], input#username, input[id*="username"]', state="visible")
            await username_field.fill(self.username)
            
            # Find and fill password field
            password_field = await page.wait_for_selector('input[name="password"], input#password, input[type="password"]', state="visible")
            await password_field.fill(self.password)
            
            # Find and click sign in button
            sign_in_button = await page.wait_for_selector('button[type="submit"], button:has-text("Sign In"), button:has-text("Sign in")', state="visible")
            await sign_in_button.click()
            
            # Wait to see results
            await page.wait_for_load_state("networkidle")
            
            # Wait for authentication to complete
            await asyncio.sleep(10)
            
            # Navigate to Virtual Cards Manager
            print("Navigating to Virtual Cards Manager...")
            await page.goto("https://myaccounts.capitalone.com/VirtualCards/Manager")
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(5)  # Extra wait to ensure page is fully loaded
            
            # Find and click "Create virtual card" button
            print("Looking for 'Create virtual card' button...")
            try:
                create_card_button = await page.wait_for_selector('button:has-text("Create virtual card")', 
                                                                 state="visible", 
                                                                 timeout=30000)
                await create_card_button.click()
                print("Clicked 'Create virtual card' button")
                
                # Wait for verification options to appear
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(3)
                
                # Skip the automatic selection and let the user handle it
                print("\n*************************************************************")
                print("MANUAL ACTION REQUIRED: Please complete the verification process")
                print("1. Select 'Text me a temporary code' (first box)")
                print("2. Click 'Send me the code'")
                print("3. Enter the verification code you receive")
                print("*************************************************************\n")
                
                # Wait for the user to complete verification by checking for the card creation form
                print("Waiting for verification to complete and card creation form to appear...")
                
                # Loop to check for the card creation form
                max_wait_time = 300  # 5 minutes maximum wait time
                start_time = asyncio.get_event_loop().time()
                verified = False
                
                while (asyncio.get_event_loop().time() - start_time) < max_wait_time:
                    # Check for elements that indicate the card creation form is visible
                    try:
                        # Look for the card nickname field and limit to single use checkbox
                        nickname_field = await page.query_selector('input[placeholder*="Example"], input[aria-label*="nickname"]')
                        single_use_checkbox = await page.query_selector('input[type="checkbox"], label:has-text("Limit to a single use")')
                        
                        if nickname_field and single_use_checkbox:
                            print("\n✅ SUCCESS: Verification completed successfully!")
                            print("Card creation form is now visible.")
                            verified = True
                            break
                    except Exception:
                        pass  # Ignore any errors during checking
                    
                    # Check every 5 seconds
                    await asyncio.sleep(5)
                
                if verified:
                    print("Waiting at the card creation page as requested.")
                    
                    # Click the "Create virtual card" button in the form
                    print("Clicking 'Create virtual card' button to generate a new card...")
                    try:
                        # Use the specific button selector from the provided HTML
                        create_button = await page.wait_for_selector('button[data-e2e="create-virtual-card-create-submit-button"]', 
                                                                   state="visible", 
                                                                   timeout=15000)
                        
                        if create_button:
                            # Try direct click first
                            await create_button.click()
                            print("Clicked the create virtual card button directly")
                        else:
                            # Fallback to previous approaches if specific selector not found
                            print("Specific button not found, trying alternative approaches")
                            
                            # Try using the class from the provided HTML
                            class_button = await page.wait_for_selector('button.c1-ease-commerce-create-virtual-card-create__submit', 
                                                                     state="visible", 
                                                                     timeout=5000)
                            if class_button:
                                await class_button.click()
                                print("Clicked the button using class selector")
                            else:
                                # Use JavaScript with the exact attributes from the provided HTML
                                await page.evaluate('''() => {
                                    const button = document.querySelector('button[data-e2e="create-virtual-card-create-submit-button"]');
                                    if (button) button.click();
                                }''')
                                print("Attempted to click using JavaScript with exact selector")
                        
                        # Wait for the card details to appear
                        await page.wait_for_load_state("networkidle")
                        await asyncio.sleep(10)  # Longer wait for card generation
                                                
                        # Check if we have the card created confirmation
                        confirmation = await page.query_selector('text="Virtual card created"')
                        if confirmation:
                            print("✅ Virtual card successfully created!")
                        
                        # Extract card details
                        print("Extracting card details...")
                        
                        try:
                            # Use the specific elements provided in the HTML
                            # Extract card number from <div class="vcNumber _TLPRIVATE">
                            card_number = await page.evaluate('''() => {
                                const cardNumberElement = document.querySelector('div.vcNumber._TLPRIVATE');
                                if (cardNumberElement) {
                                    return cardNumberElement.textContent.replace(/\\s+/g, '');
                                }
                                return '';
                            }''')
                            
                            # Extract expiration date from <span> element
                            exp_data = await page.evaluate('''() => {
                                const expElements = Array.from(document.querySelectorAll('span'));
                                const expElement = expElements.find(span => /\\d{2}\\/\\d{2}/.test(span.textContent));
                                if (expElement) {
                                    const match = expElement.textContent.match(/(\\d{2})\\/(\\d{2})/);
                                    if (match) {
                                        return {
                                            month: match[1],
                                            year: match[2]
                                        };
                                    }
                                }
                                return { month: '', year: '' };
                            }''')
                            
                            # Extract CVV from <div class="_TLPRIVATE vcCVV">
                            cvv = await page.evaluate('''() => {
                                const cvvElement = document.querySelector('div._TLPRIVATE.vcCVV');
                                if (cvvElement) {
                                    const match = cvvElement.textContent.match(/Security\\s*Code:\\s*(\\d+)/);
                                    if (match) {
                                        return match[1];
                                    }
                                }
                                return '';
                            }''')
                            
                            print(f"Extracted card number: {card_number}")
                            print(f"Extracted expiration: {exp_data['month']}/{exp_data['year']}")
                            print(f"Extracted CVV: {cvv}")
                            
                            # Check if all data was extracted successfully
                            if card_number and exp_data['month'] and exp_data['year'] and cvv:
                                # Format the card details
                                card_details = f"{card_number},{exp_data['month']},{exp_data['year']},{cvv}"
                                print(f"Card details extracted: {card_details}")
                                
                                # Save to cap_genned.txt
                                with open("cap_genned.txt", "a") as f:
                                    f.write(card_details + "\n")
                                
                                print(f"✅ Card details saved to cap_genned.txt")
                                
                                # Scroll down before looking for the "Got it" button to ensure it's visible
                                await page.evaluate('() => { window.scrollBy(0, 300); }')
                                print("Scrolled down to ensure 'Got it' button is visible")
                                
                                print("Looking for 'Got it' button to complete the process...")
                                try:
                                    # Try to find and click the "Got it" button using the specific selector
                                    got_it_button = await page.wait_for_selector('button[data-e2e="c1-ease-commerce-create-virtual-card-create-success__button-confirm"]', 
                                                                             state="visible", 
                                                                             timeout=10000)
                                    if got_it_button:
                                        await got_it_button.click()
                                        print("✅ Clicked 'Got it' button")
                                    else:
                                        # Try alternative selector approaches
                                        # Try by button text
                                        text_button = await page.wait_for_selector('button:has-text("Got it")', 
                                                                               state="visible", 
                                                                               timeout=5000)
                                        if text_button:
                                            await text_button.click()
                                            print("✅ Clicked 'Got it' button by text")
                                        else:
                                            # Try by class name
                                            class_button = await page.wait_for_selector('button.c1-ease-commerce-create-virtual-card-create-success__button-confirm', 
                                                                                   state="visible", 
                                                                                   timeout=5000)
                                            if class_button:
                                                await class_button.click()
                                                print("✅ Clicked 'Got it' button by class")
                                            else:
                                                # Try using JavaScript as a last resort
                                                await page.evaluate('''() => {
                                                    // Look for the button by text content
                                                    const buttons = Array.from(document.querySelectorAll('button'));
                                                    const gotItButton = buttons.find(btn => btn.textContent.trim() === 'Got it');
                                                    if (gotItButton) {
                                                        gotItButton.click();
                                                        return true;
                                                    }
                                                    
                                                    // Try by data-e2e attribute
                                                    const attrButton = document.querySelector('button[data-e2e="c1-ease-commerce-create-virtual-card-create-success__button-confirm"]');
                                                    if (attrButton) {
                                                        attrButton.click();
                                                        return true;
                                                    }
                                                    
                                                    return false;
                                                }''')
                                                print("Attempted to click 'Got it' button using JavaScript")
                                
                                    # Wait a moment for any navigation or UI updates after clicking
                                    await asyncio.sleep(3)
                                    
                                    # Wait 2 seconds as requested before restarting the process
                                    print("Waiting 2 seconds before starting a new card creation process...")
                                    await asyncio.sleep(2)
                                    
                                    # Generate the remaining cards
                                    cards_generated = 1  # We've already generated one card
                                    while cards_generated < self.num_cards:
                                        print(f"\n*************************************************************")
                                        print(f"GENERATING CARD {cards_generated+1} OF {self.num_cards}")
                                        print(f"Looking for 'Create virtual card' button to create another card...")
                                        print(f"*************************************************************\n")
                                        
                                        try:
                                            # Find and click the first level "Create virtual card" button again
                                            create_card_button = await page.wait_for_selector('button:has-text("Create virtual card")', 
                                                                                           state="visible", 
                                                                                           timeout=15000)
                                            await create_card_button.click()
                                            print(f"Clicked 'Create virtual card' button to start card {cards_generated+1} creation")
                                            
                                            # Wait for the form to appear - no verification needed after the first time
                                            await page.wait_for_load_state("networkidle")
                                            await asyncio.sleep(3)
                                                                                        
                                            # Check if we're seeing the card creation form directly
                                            nickname_field = await page.query_selector('input[placeholder*="Example"], input[aria-label*="nickname"]')
                                            single_use_checkbox = await page.query_selector('input[type="checkbox"], label:has-text("Limit to a single use")')
                                            
                                            if nickname_field and single_use_checkbox:
                                                print("✅ Card creation form appeared directly without verification")
                                                
                                                # Click the second level "Create virtual card" button
                                                print(f"Clicking 'Create virtual card' button to generate card {cards_generated+1}...")
                                                
                                                create_button = await page.wait_for_selector('button[data-e2e="create-virtual-card-create-submit-button"]', 
                                                                                           state="visible", 
                                                                                           timeout=15000)
                                                
                                                if create_button:
                                                    await create_button.click()
                                                    print(f"Clicked the button to create virtual card {cards_generated+1}")
                                                    
                                                    # Wait for the card details to appear
                                                    await page.wait_for_load_state("networkidle")
                                                    await asyncio.sleep(10)
                                                    
                                                    # Extract card details using the same methods as before
                                                    print(f"Extracting details for card {cards_generated+1}...")
                                                    
                                                    # Extract card number from <div class="vcNumber _TLPRIVATE">
                                                    card_number = await page.evaluate('''() => {
                                                        const cardNumberElement = document.querySelector('div.vcNumber._TLPRIVATE');
                                                        if (cardNumberElement) {
                                                            return cardNumberElement.textContent.replace(/\\s+/g, '');
                                                        }
                                                        return '';
                                                    }''')
                                                    
                                                    # Extract expiration date from <span> element
                                                    exp_data = await page.evaluate('''() => {
                                                        const expElements = Array.from(document.querySelectorAll('span'));
                                                        const expElement = expElements.find(span => /\\d{2}\\/\\d{2}/.test(span.textContent));
                                                        if (expElement) {
                                                            const match = expElement.textContent.match(/(\\d{2})\\/(\\d{2})/);
                                                            if (match) {
                                                                return {
                                                                    month: match[1],
                                                                    year: match[2]
                                                                };
                                                            }
                                                        }
                                                        return { month: '', year: '' };
                                                    }''')
                                                    
                                                    # Extract CVV from <div class="_TLPRIVATE vcCVV">
                                                    cvv = await page.evaluate('''() => {
                                                        const cvvElement = document.querySelector('div._TLPRIVATE.vcCVV');
                                                        if (cvvElement) {
                                                            const match = cvvElement.textContent.match(/Security\\s*Code:\\s*(\\d+)/);
                                                            if (match) {
                                                                return match[1];
                                                            }
                                                        }
                                                        return '';
                                                    }''')
                                                    
                                                    print(f"Extracted card number: {card_number}")
                                                    print(f"Extracted expiration: {exp_data['month']}/{exp_data['year']}")
                                                    print(f"Extracted CVV: {cvv}")
                                                    
                                                    if card_number and exp_data['month'] and exp_data['year'] and cvv:
                                                        # Format the card details
                                                        card_details = f"{card_number},{exp_data['month']},{exp_data['year']},{cvv}"
                                                        print(f"Card details extracted: {card_details}")
                                                        
                                                        # Save to cap_genned.txt
                                                        with open("cap_genned.txt", "a") as f:
                                                            f.write(card_details + "\n")
                                                        
                                                        print(f"✅ Card details saved to cap_genned.txt")
                                                        
                                                        # Scroll and click "Got it" button
                                                        await page.evaluate('() => { window.scrollBy(0, 300); }')
                                                        print(f"Scrolled down to ensure 'Got it' button is visible for card {cards_generated+1}")
                                                        
                                                        # Click "Got it" button for the card
                                                        print(f"Looking for 'Got it' button to complete card {cards_generated+1} process...")
                                                        
                                                        got_it_button = await page.wait_for_selector('button[data-e2e="c1-ease-commerce-create-virtual-card-create-success__button-confirm"], button:has-text("Got it")', 
                                                                                                  state="visible", 
                                                                                                  timeout=10000)
                                                        if got_it_button:
                                                            await got_it_button.click()
                                                            print(f"✅ Clicked 'Got it' button for card {cards_generated+1}")
                                                        else:
                                                            # Try JavaScript as fallback
                                                            await page.evaluate('''() => {
                                                                const buttons = Array.from(document.querySelectorAll('button'));
                                                                const gotItButton = buttons.find(btn => btn.textContent.trim() === 'Got it');
                                                                if (gotItButton) {
                                                                    gotItButton.click();
                                                                }
                                                            }''')
                                                            print(f"Attempted to click 'Got it' button using JavaScript for card {cards_generated+1}")
                                                    
                                                        await asyncio.sleep(3)
                                                        
                                                        # Increment the counter
                                                        cards_generated += 1
                                                        
                                                        # Wait 2 seconds before the next card
                                                        await asyncio.sleep(2)
                                                    else:
                                                        print(f"Failed to extract all card {cards_generated+1} details automatically.")
                                                        # Fallback to manual input for card
                                                        # ... (similar to previous manual input code)
                                                else:
                                                    print(f"Could not find the 'Create virtual card' button for card {cards_generated+1}")
                                                # Remove this break statement that was causing premature loop exit
                                                # break  
                                            else:
                                                print(f"Card creation form for card {cards_generated+1} not found or incomplete")
                                        except Exception as card_error:
                                            print(f"Error during card {cards_generated+1} creation process: {card_error}")
                                            # Remove this break statement that was causing premature loop exit
                                            # break  
                                
                                except Exception as extract_error:
                                    print(f"Error extracting card details: {extract_error}")
                                    
                                    # Fallback to manual input if any exception occurs
                                    print("Exception occurred during extraction. Manual input required.")
                                    
                                    card_number = input("Please enter the card number (16 digits): ")
                                    exp_month = input("Please enter the expiration month (MM): ")
                                    exp_year = input("Please enter the expiration year (YY): ")
                                    cvv = input("Please enter the CVV (3 digits): ")
                                    
                                    # Format and save the manual input
                                    card_details = f"{card_number},{exp_month},{exp_year},{cvv}"
                                    with open("cap_genned.txt", "a") as f:
                                        f.write(card_details + "\n")
                                    
                                    print(f"✅ Manually entered card details saved to cap_genned.txt")
                        except Exception as e:
                            print(f"Error while creating or extracting card details: {e}")
                            
                    except Exception as e:
                        print(f"Error while creating or extracting card details: {e}")
                                                    
                        # Let user manually create a card if automated click failed
                        print("\n*************************************************************")
                        print("MANUAL ACTION REQUIRED: Please click the 'Create virtual card' button")
                        print("Wait for the card to be created, then enter the details manually:")
                        print("*************************************************************\n")
                        
                        # Wait for user to create card and then manually input details
                        input("Press Enter after you have clicked the button and the card is created...")
                        
                        card_number = input("Please enter the card number (16 digits): ")
                        exp_month = input("Please enter the expiration month (MM): ")
                        exp_year = input("Please enter the expiration year (YY): ")
                        cvv = input("Please enter the CVV (3 digits): ")
                        
                        # Format and save the manual input
                        card_details = f"{card_number},{exp_month},{exp_year},{cvv}"
                        with open("cap_genned.txt", "a") as f:
                            f.write(card_details + "\n")
                        
                        print(f"✅ Manually entered card details saved to cap_genned.txt")
                else:
                    print("Timed out waiting for verification. The verification process may not have completed successfully.")
                
            except Exception as e:
                print(f"Error during process: {e}")
            # Instead of closing, wait for user input to close
            input("Process complete. Press Enter to close the browser...")
            try:
                await browser.close()
            except:
                print("Browser may already be closed")

    async def delete_cards(self):
        async with async_playwright() as p:
            try:
                # Launch browser and create page, similar to login method
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                )
                
                page = await context.new_page()
                
                # Explicitly set the zoom level to 80% to ensure all buttons are visible
                try:
                    # Set zoom using CSS transform
                    await page.evaluate('''() => { 
                        document.body.style.zoom = "80%";
                        document.body.style.transform = "scale(0.8)";
                        document.body.style.transformOrigin = "0 0";
                    }''')
                    print("Set page zoom to 80% to ensure all buttons are visible")
                except Exception as zoom_error:
                    print(f"Warning: Could not set zoom level: {zoom_error}")
                
                # Navigate to Capital One login page and authenticate
                await page.goto("https://verified.capitalone.com/auth/signin")
                
                # Set zoom again after page load
                await page.evaluate('() => { document.body.style.zoom = "80%"; }')
                print("Applied zoom level again after page load")
                
                await page.wait_for_load_state("networkidle")
                
                # Find and fill username field
                username_field = await page.wait_for_selector('input[name="username"], input#username, input[id*="username"]', state="visible")
                await username_field.fill(self.username)
                
                # Find and fill password field
                password_field = await page.wait_for_selector('input[name="password"], input#password, input[type="password"]', state="visible")
                await password_field.fill(self.password)
                
                # Find and click sign in button
                sign_in_button = await page.wait_for_selector('button[type="submit"], button:has-text("Sign In"), button:has-text("Sign in")', state="visible")
                await sign_in_button.click()
                
                # Wait for authentication to complete
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(10)
                
                # Apply zoom level again after authentication
                await page.evaluate('() => { document.body.style.zoom = "80%"; }')
                
                # Navigate to Virtual Cards Manager
                print("Navigating to Virtual Cards Manager...")
                await page.goto("https://myaccounts.capitalone.com/VirtualCards/Manager")
                
                # Wait for page to load
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(5)  # Extra wait to ensure page is fully loaded
                
                # Apply zoom level one more time after loading the cards page
                await page.evaluate('() => { document.body.style.zoom = "80%"; }')
                print("Applied zoom level again after loading the cards page")
                
                # Wait for the virtual cards page to load
                await page.wait_for_selector("c1-ease-commerce-virtual-cards-table-nickname-column", timeout=30000)
                print("Virtual cards page loaded")
                
                # Extract the HTML content to check the number of existing cards
                html_content = await page.content()
                
                # Check how many cards exist by counting "Unnamed Virtual Card" instances
                card_count = html_content.count('Unnamed Virtual Card')
                print(f"Found {card_count} virtual cards")
                
                # If there are no cards, log and return early
                if card_count == 0:
                    print("No cards found to delete")
                    return
                
                # Continue with deletion only if cards exist
                cards_to_delete = min(self.num_cards, card_count)
                print(f"Will delete {cards_to_delete} cards")
                
                # Save HTML content to file for debugging/analysis
                with open("cards.txt", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("Saved HTML content to cards.txt for analysis")
                
                # Now proceed with deletion of the specified number of cards
                for i in range(cards_to_delete):
                    try:
                        # Wait for the manage button to be visible and click it
                        manage_button = await page.wait_for_selector(
                            "button.c1-ease-commerce-virtual-cards-manager__manage-token-button", 
                            timeout=10000
                        )
                        
                        if manage_button:
                            await manage_button.click()
                            print(f"Clicked manage button for card {i+1}")
                        else:
                            # Try alternative selector if first one fails
                            alt_button = await page.wait_for_selector(
                                "button[aria-label^='Manage virtual card Unnamed Virtual Card']", 
                                timeout=5000
                            )
                            if alt_button:
                                await alt_button.click()
                                print(f"Clicked manage button (alt selector) for card {i+1}")
                            else:
                                # Use JavaScript as last resort
                                clicked = await page.evaluate('''() => {
                                    const buttons = document.querySelectorAll('button.c1-ease-commerce-virtual-cards-manager__manage-token-button');
                                    if (buttons && buttons.length > 0) {
                                        buttons[0].click();
                                        return true;
                                    }
                                    return false;
                                }''')
                                
                                if clicked:
                                    print(f"Clicked manage button via JavaScript for card {i+1}")
                                else:
                                    print(f"Failed to find manage button for card {i+1}")
                                    continue
                        
                        # Wait for the manage modal to appear
                        await asyncio.sleep(2)
                        
                        # Wait for the delete button to be visible and click it
                        try:
                            # First try with the exact selector
                            delete_button = await page.wait_for_selector(
                                "button[data-e2e='manage-virtual-number-delete-button']", 
                                timeout=5000
                            )
                            if delete_button:
                                await delete_button.click()
                                print(f"Clicked delete button (exact selector) for card {i+1}")
                            else:
                                # Try by button text content
                                text_delete_button = await page.wait_for_selector(
                                    "button:has-text('Delete Virtual Card')", 
                                    timeout=5000
                                )
                                if text_delete_button:
                                    await text_delete_button.click()
                                    print(f"Clicked delete button (text selector) for card {i+1}")
                                else:
                                    # Try by class
                                    class_delete_button = await page.wait_for_selector(
                                        "button.grv-button-tertiary--danger", 
                                        timeout=5000
                                    )
                                    if class_delete_button:
                                        await class_delete_button.click()
                                        print(f"Clicked delete button (class selector) for card {i+1}")
                                    else:
                                        # Use JavaScript as last resort
                                        deleted = await page.evaluate('''() => {
                                            // First try data-e2e attribute
                                            let button = document.querySelector("button[data-e2e='manage-virtual-number-delete-button']");
                                            
                                            // Then try by text content
                                            if (!button) {
                                                const buttons = Array.from(document.querySelectorAll('button'));
                                                button = buttons.find(btn => btn.textContent.includes('Delete Virtual Card'));
                                            }
                                            
                                            if (button) {
                                                button.click();
                                                return true;
                                            }
                                            return false;
                                        }''')
                                        
                                        if deleted:
                                            print(f"Clicked delete button via JavaScript for card {i+1}")
                                        else:
                                            print(f"Failed to find delete button for card {i+1}")
                                            continue
                        except Exception as delete_error:
                            print(f"Error finding/clicking delete button for card {i+1}: {delete_error}")
                            continue
                        
                        # Wait for the confirmation dialog
                        await asyncio.sleep(2)
                        
                        # Wait for and click the confirm delete button
                        try:
                            # First try with the exact selector
                            confirm_delete = await page.wait_for_selector(
                                "button[data-e2e='manage-virtual-number-delete-confirm']", 
                                timeout=5000
                            )
                            if confirm_delete:
                                await confirm_delete.click()
                                print(f"Confirmed deletion (exact selector) for card {i+1}")
                            else:
                                # Try by direct aria-label
                                aria_confirm = await page.wait_for_selector("button[aria-label='Delete']", timeout=5000)
                                if aria_confirm:
                                    await aria_confirm.click()
                                    print(f"Confirmed deletion (aria-label) for card {i+1}")
                                else:
                                    # Try by button text
                                    text_confirm = await page.wait_for_selector("button:has-text('Delete')", timeout=5000)
                                    if text_confirm:
                                        await text_confirm.click()
                                        print(f"Confirmed deletion (text) for card {i+1}")
                                    else:
                                        # Try by class
                                        class_confirm = await page.wait_for_selector("button.deleteButton.grv-button-primary--danger", timeout=5000)
                                        if class_confirm:
                                            await class_confirm.click() 
                                            print(f"Confirmed deletion (class selector) for card {i+1}")
                                        else:
                                            # Try JavaScript as last resort
                                            confirmed = await page.evaluate('''() => {
                                                // Try all possible selectors
                                                let button = document.querySelector("button[data-e2e='manage-virtual-number-delete-confirm']");
                                                
                                                if (!button) {
                                                    button = document.querySelector("button.deleteButton");
                                                }
                                                
                                                if (!button) {
                                                    button = document.querySelector("button.grv-button-primary--danger");
                                                }
                                                
                                                if (!button) {
                                                    const buttons = Array.from(document.querySelectorAll('button'));
                                                    button = buttons.find(btn => btn.textContent.trim() === 'Delete');
                                                }
                                                
                                                if (button) {
                                                    button.click();
                                                    return true;
                                                }
                                                return false;
                                            }''')
                                            
                                            if confirmed:
                                                print(f"Confirmed deletion via JavaScript for card {i+1}")
                                            else:
                                                print(f"Failed to find confirm button for card {i+1}")
                                                continue
                        except Exception as confirm_error:
                            print(f"Error confirming deletion for card {i+1}: {confirm_error}")
                            continue
                        
                        # Wait for the deletion to complete with enough time to see the success message
                        await page.wait_for_timeout(2000)

                        # Check for success message
                        try:
                            # Look for the specific success header
                            success_message = await page.wait_for_selector(
                                "h1#title:has-text('Success')", 
                                timeout=5000
                            )
                            
                            if success_message:
                                print(f"✅ Confirmed successful deletion of card {i+1} - Success message found")
                            else:
                                # Try alternative selectors for the success message
                                alt_success = await page.wait_for_selector(
                                    "h1.c1-ease-dialog-title:has-text('Success')", 
                                    timeout=2000
                                )
                                
                                if alt_success:
                                    print(f"✅ Confirmed successful deletion of card {i+1} - Success title found")
                                else:
                                    # Try with JavaScript to find any success message
                                    success_found = await page.evaluate('''() => {
                                        // Check for the specific h1
                                        const successTitle = document.querySelector("h1#title.c1-ease-dialog-title");
                                        if (successTitle && successTitle.textContent.trim() === "Success") {
                                            return true;
                                        }
                                        
                                        // Check for any element containing "Success" text
                                        const elements = document.querySelectorAll("*");
                                        for (const el of elements) {
                                            if (el.textContent && el.textContent.trim() === "Success") {
                                                return true;
                                            }
                                        }
                                        
                                        return false;
                                    }''')
                                    
                                    if success_found:
                                        print(f"✅ Confirmed successful deletion of card {i+1} - Success text found via JavaScript")
                                    else:
                                        print(f"⚠️ Warning: Could not verify successful deletion of card {i+1} - No success message found")
                                        print(f"Continuing to next card anyway...")
                                
                        except Exception as success_error:
                            print(f"Error checking for success message for card {i+1}: {success_error}")

                        # Wait for any dismiss button or wait for the success message to disappear naturally
                        try:
                            dismiss_button = await page.wait_for_selector(
                                "button:has-text('OK'), button:has-text('Done'), button:has-text('Close')", 
                                timeout=3000
                            )
                            if dismiss_button:
                                await dismiss_button.click()
                                print(f"Clicked dismiss button after successful deletion of card {i+1}")
                        except:
                            # If no dismiss button found, wait a moment for any auto-dismissal
                            print(f"No dismiss button found, waiting for success message to disappear")
                            await page.wait_for_timeout(2000)

                        # Additional wait to ensure the UI is ready for the next card deletion
                        await page.wait_for_timeout(2000)
                        
                        # Look for and click the "Next" button before moving to the next card
                        try:
                            # Wait a bit longer for any animations to complete
                            await asyncio.sleep(1)
                            
                            # Try clicking on the overlay first to ensure dialog is active
                            try:
                                await page.click('.cdk-overlay-container')
                                print(f"Clicked on overlay to ensure dialog is active")
                            except:
                                pass
                            
                            # Use multiple approaches to find and click the Next button
                            next_clicked = False
                            
                            # 1. Try with exact data-aut attribute and class (using the HTML you provided)
                            try:
                                next_button = await page.wait_for_selector(
                                    "button[data-aut='button-next']._1De-hWu2XrYnO5hnFIWYwJ.surveyBtn.surveyBtn_next", 
                                    timeout=3000
                                )
                                if next_button:
                                    await next_button.click()
                                    print(f"Clicked 'Next' button with exact selector for card {i+1}")
                                    next_clicked = True
                            except:
                                print(f"Could not find 'Next' button with exact selector")
                            
                            # 2. Try with just the data-aut attribute if not clicked yet
                            if not next_clicked:
                                try:
                                    next_button = await page.wait_for_selector(
                                        "button[data-aut='button-next']", 
                                        timeout=3000
                                    )
                                    if next_button:
                                        await next_button.click()
                                        print(f"Clicked 'Next' button using data-aut attribute for card {i+1}")
                                        next_clicked = True
                                except:
                                    print(f"Could not find 'Next' button with data-aut attribute")
                            
                            # 3. Try with JavaScript using the exact button structure from your HTML
                            if not next_clicked:
                                try:
                                    next_clicked = await page.evaluate('''() => {
                                        const button = document.querySelector('button[data-aut="button-next"][class*="surveyBtn_next"]');
                                        if (button) {
                                            button.click();
                                            return true;
                                        }
                                        return false;
                                    }''')
                                    
                                    if next_clicked:
                                        print(f"Clicked 'Next' button via JavaScript with exact attributes for card {i+1}")
                                except:
                                    print(f"JavaScript click attempt failed")
                            
                            # 4. Try with text content as a fallback
                            if not next_clicked:
                                try:
                                    text_next_button = await page.wait_for_selector(
                                        "button:has-text('Next')", 
                                        timeout=3000
                                    )
                                    if text_next_button:
                                        await text_next_button.click()
                                        print(f"Clicked 'Next' button by text content for card {i+1}")
                                        next_clicked = True
                                except:
                                    print(f"Could not find 'Next' button by text content")
                            
                            # 5. Use a more aggressive approach with evaluate if still not clicked
                            if not next_clicked:
                                try:
                                    force_clicked = await page.evaluate('''() => {
                                        // Try all possible variations to find the Next button
                                        let buttons = Array.from(document.querySelectorAll('button'));
                                        
                                        // First by exact match
                                        let nextButton = buttons.find(b => 
                                            b.getAttribute('data-aut') === 'button-next' || 
                                            b.textContent.trim() === 'Next' ||
                                            (b.className && b.className.includes('surveyBtn_next'))
                                        );
                                        
                                        if (nextButton) {
                                            // Try several click methods
                                            try {
                                                nextButton.click();
                                                return true;
                                            } catch(e) {
                                                // Try with mouse event
                                                try {
                                                    const evt = new MouseEvent('click', {
                                                        bubbles: true,
                                                        cancelable: true,
                                                        view: window
                                                    });
                                                    nextButton.dispatchEvent(evt);
                                                    return true;
                                                } catch(e2) {
                                                    return false;
                                                }
                                            }
                                        }
                                        return false;
                                    }''')
                                    
                                    if force_clicked:
                                        print(f"Force-clicked 'Next' button via JavaScript for card {i+1}")
                                        next_clicked = True
                                except:
                                    print(f"Force-click attempt failed")
                            
                            if not next_clicked:
                                print(f"⚠️ Warning: Could not find or click 'Next' button after deletion of card {i+1}")
                                # Continue anyway since we've deleted the card successfully
                                
                        except Exception as next_button_error:
                            print(f"Error finding/clicking 'Next' button after deletion of card {i+1}: {next_button_error}")

                        # Add a longer wait after handling the Next button to ensure UI stability for next card
                        await asyncio.sleep(3)
                        
                    except Exception as e:
                        print(f"Error in deletion process for card {i+1}: {e}")
                
                print(f"Deleted {cards_to_delete} cards")
                
                # Wait for user input before closing
                input("Card deletion complete. Press Enter to close the browser...")
                
            except Exception as e:
                print(f"Error in delete_cards method: {e}")
            
            finally:
                # Ensure browser is closed properly in all cases
                try:
                    await browser.close()
                except:
                    print("Browser may already be closed")
