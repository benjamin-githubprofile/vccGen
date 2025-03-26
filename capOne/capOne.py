import asyncio
import os
from playwright.async_api import async_playwright

class CapitalOneAutomation:
    def __init__(self, username, password, headless=False, num_cards=1):
        self.username = username
        self.password = password
        self.headless = headless
        self.num_cards = num_cards  # Store the number of cards to generate
        
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
                
                # Take a screenshot to see the verification page
                await page.screenshot(path="verification_page.png")
                
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
                    # Take periodic screenshots to track progress
                    await page.screenshot(path="waiting_for_verification.png")
                    
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
                    # Take a screenshot of the card creation form
                    await page.screenshot(path="card_creation_form.png")
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
                        
                        # Take a screenshot of the generated card
                        await page.screenshot(path="generated_card.png")
                        
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
                                await page.screenshot(path="after_scroll_for_got_it.png")
                                
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
                                    await page.screenshot(path="after_got_it.png")
                                    
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
                                            
                                            # Take screenshot of the card creation form
                                            await page.screenshot(path=f"card_{cards_generated+1}_creation_form.png")
                                            
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
                                                        await page.screenshot(path=f"after_scroll_for_got_it_card_{cards_generated+1}.png")
                                                        
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
                                                        await page.screenshot(path=f"after_card_{cards_generated+1}_got_it.png")
                                                        
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
                                            await page.screenshot(path=f"card_{cards_generated+1}_error.png")
                                            # Remove this break statement that was causing premature loop exit
                                            # break  
                                
                                except Exception as extract_error:
                                    print(f"Error extracting card details: {extract_error}")
                                    await page.screenshot(path="extraction_error.png")
                                    
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
                            await page.screenshot(path="card_creation_error.png")
                            
                    except Exception as e:
                        print(f"Error while creating or extracting card details: {e}")
                        await page.screenshot(path="card_creation_error.png")
                                                    
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
                    await page.screenshot(path="verification_timeout.png")
                
            except Exception as e:
                print(f"Error during process: {e}")
                try:
                    await page.screenshot(path="error.png")
                except:
                    print("Could not take error screenshot as page may be closed")
            
            # Instead of closing, wait for user input to close
            input("Process complete. Press Enter to close the browser...")
            try:
                await browser.close()
            except:
                print("Browser may already be closed")
