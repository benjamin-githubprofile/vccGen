import asyncio
import os
import time
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import pytesseract
import subprocess
import json
import random
import string
import re  # Add import at the module level

class RelayAutomation:
    def __init__(self, username, password, headless=False, num_cards=1):
        self.username = username
        self.password = password
        self.headless = headless
        self.num_cards = num_cards
        
        # Store actions (clicks and typing)
        self.actions = []  # Will contain dictionaries with type, position, name, and text
        self.delete_actions = []  # For storing card deletion actions
        
        # Set a small pause between actions to make movements more human-like
        pyautogui.PAUSE = 0.5
        
        # Load saved actions if available
        self.load_actions()
    
    def load_actions(self):
        """Load saved actions from file if it exists"""
        try:
            # Use the relay directory for storing the actions file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            actions_file_path = os.path.join(current_dir, "relay_actions.json")
            delete_actions_file_path = os.path.join(current_dir, "relay_delete_actions.json")
            
            if os.path.exists(actions_file_path):
                with open(actions_file_path, "r") as f:
                    self.actions = json.load(f)
                    click_count = sum(1 for action in self.actions if action["type"] == "click")
                    type_count = sum(1 for action in self.actions if action["type"] == "type")
                    print(f"Loaded {len(self.actions)} saved actions ({click_count} clicks, {type_count} typing actions)")
            
            # Load delete actions if they exist
            if os.path.exists(delete_actions_file_path):
                with open(delete_actions_file_path, "r") as f:
                    self.delete_actions = json.load(f)
                    click_count = sum(1 for action in self.delete_actions if action["type"] == "click")
                    type_count = sum(1 for action in self.delete_actions if action["type"] == "type")
                    print(f"Loaded {len(self.delete_actions)} saved delete actions ({click_count} clicks, {type_count} typing actions)")
            else:
                self.delete_actions = []
        except Exception as e:
            print(f"Could not load saved actions: {e}")
            self.actions = []
            self.delete_actions = []
    
    def save_actions(self, is_delete=False):
        """Save actions to file"""
        try:
            # Use the relay directory for storing the actions file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            actions_file_path = os.path.join(current_dir, "relay_actions.json")
            delete_actions_file_path = os.path.join(current_dir, "relay_delete_actions.json")
            
            if is_delete:
                with open(delete_actions_file_path, "w") as f:
                    json.dump(self.delete_actions, f)
                    print(f"Saved {len(self.delete_actions)} delete actions to {delete_actions_file_path}")
            else:
                with open(actions_file_path, "w") as f:
                    json.dump(self.actions, f)
                    print(f"Saved {len(self.actions)} actions to {actions_file_path}")
        except Exception as e:
            print(f"Could not save actions: {e}")
    
    def display_frame_guide(self, width=1400, height=900):
        """Create a simple outline image and display it using macOS Preview"""
        # Create a new image with black background
        img = Image.new('RGB', (width, height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a red rectangle border (5 pixels thick)
        for i in range(5):
            draw.rectangle([(i, i), (width-i-1, height-i-1)], outline=(255, 0, 0))
        
        # Add instructions as white text
        instructions = [
            "BROWSER POSITIONING GUIDE",
            "1. Resize Safari to fit this red frame",
            "2. Make sure Relay dashboard is visible", 
            "3. Keep browser in this position"
        ]
        
        y_text = 50
        for line in instructions:
            # Position the text
            draw.text((width//4, y_text), line, fill=(255, 255, 255))
            y_text += 50
        
        # Save the image
        img_path = "browser_guide.png"
        img.save(img_path)
        
        # Open the image with macOS Preview (macOS specific)
        print("Opening frame guide image. Please position your browser within the red frame.")
        subprocess.call(['open', img_path])
        
        # Wait for user confirmation
        input("Press Enter when your browser is positioned (with this terminal window focused)...")
        
        print("Browser positioned. Starting automation...")
        return True
    
    async def login(self):
        """Main entry point that assumes browser is already logged in"""
        print("Using existing logged-in browser session")
        
        # Determine if we need to collect actions or use saved ones
        if not self.actions:
            print("\n*************************************************************")
            print("ACTION COLLECTION MODE")
            print("*************************************************************")
            print("You'll be asked to perform clicks and typing for each step of the process.")
            print("The program will record your actions for automation.")
            
            await self.collect_actions()
            self.save_actions()
        else:
            use_saved = input(f"Use {len(self.actions)} saved actions? (y/n): ").lower() == 'y'
            if not use_saved:
                self.actions = []
                await self.collect_actions()
                self.save_actions()
        
        # Add confirmation before starting automation
        print("\n*************************************************************")
        print("READY TO START AUTOMATION")
        print("*************************************************************")
        print(f"Collected {len(self.actions)} actions that will be performed.")
        
        # Wait for user to double-click instead of typing "start"
        print("\nPosition your cursor where you want and DOUBLE-CLICK to begin the automation")
        self.wait_for_double_click()
        
        print("\nDouble-click detected! Starting automation process...")
        # Now run the automation using the collected actions
        await self.run_automation()
    
    def wait_for_double_click(self):
        """Wait for the user to perform a double-click to start automation"""
        import threading
        import time
        
        # Create an event to signal when double-click is detected
        double_click_event = threading.Event()
        
        # Function to monitor for double clicks
        def monitor_double_click():
            try:
                # Create a listener for mouse clicks
                from pynput import mouse
                
                # Track click times
                last_click_time = 0
                
                def on_click(x, y, button, pressed):
                    nonlocal last_click_time
                    
                    if pressed:
                        # Check if this is a double-click
                        current_time = time.time()
                        if current_time - last_click_time < 0.5:  # 500ms threshold for double-click
                            double_click_event.set()
                            return False  # Stop listener
                        last_click_time = current_time
                
                # Start listening for mouse clicks
                with mouse.Listener(on_click=on_click) as listener:
                    listener.join()
                    
            except ImportError:
                # If pynput isn't available, fall back to manual confirmation
                print("\nCouldn't detect mouse clicks automatically.")
                input("Press Enter when you've double-clicked to begin: ")
                double_click_event.set()
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_double_click)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Wait for double-click event
        double_click_event.wait()
    
    async def collect_actions(self):
        """Collect all necessary actions (clicks and typing) from the user"""
        print("\nPlease prepare your browser with the Relay dashboard open.")
        print("\nTIP: When asked to type text, you can enter 'random' to generate a random 5-letter string during automation.")
        print("TIP: You can specify a custom delay (in seconds) after each click.")
        input("Press Enter when ready to start collecting actions...")
        
        action_count = 1
        while True:
            print(f"\nAction {action_count}:")
            # Automatically use incremental numbers instead of asking for description
            description = str(action_count)
            
            print(f"Please position your cursor where you want click #{action_count} to occur")
            input("Position cursor and press Enter when ready...")
            
            position = pyautogui.position()
            
            # Ask for delay time after this click
            delay_time = 1  # Default delay
            try:
                delay_input = input(f"Enter delay in seconds after this click (default is 1): ")
                if delay_input.strip():
                    delay_time = int(delay_input)
                    if delay_time < 0:
                        delay_time = 0
                    print(f"Will wait {delay_time} seconds after this click")
            except ValueError:
                print("Using default delay of 1 second")
            
            # Record the click action with custom delay
            self.actions.append({
                "type": "click",
                "position": (position.x, position.y),
                "name": description,
                "text": None,
                "delay": delay_time
            })
            
            print(f"✅ Click {action_count} captured at position {position} with {delay_time}s delay")
            
            # Ask if typing is needed after this click
            typing_needed = input(f"Do you need to type anything after click {action_count}? (type 'n' if nothing to type): ")
            if typing_needed.lower() != 'n':
                # Record the typing action
                self.actions.append({
                    "type": "type",
                    "position": None,
                    "name": f"Type after {action_count}",
                    "text": typing_needed,
                    "delay": 1  # Default delay after typing
                })
                
                # Show special message for random text
                if typing_needed.lower() == 'random':
                    print(f"✅ Typing action recorded: Will generate random 5-letter text during automation")
                else:
                    print(f"✅ Typing action recorded: '{typing_needed}'")
            
            # Ask if there are more actions
            more_actions = input("\nDo you have more clicks in the process? (type 'n' if this is the end): ").lower()
            if more_actions == 'n':
                break
                
            action_count += 1
        
        print(f"\nCollection complete! Recorded {len(self.actions)} actions:")
        for i, action in enumerate(self.actions):
            if action["type"] == "click":
                print(f"{i+1}. Click '{action['name']}' at {action['position']} (delay: {action['delay']}s)")
            else:
                if action["text"].lower() == 'random':
                    print(f"{i+1}. Type random 5-letter string (delay: {action['delay']}s)")
                else:
                    print(f"{i+1}. Type '{action['text']}' (delay: {action['delay']}s)")
    
    def generate_random_text(self, length=5):
        """Generate a random string of letters with the specified length"""
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    
    def extract_card_details_from_screen(self):
        """Extract card number, expiration date, and CVV from the screen"""
        print("Taking screenshot to extract card details...")
        screenshot = pyautogui.screenshot()
        screenshot_path = "card_details_screenshot.png"
        screenshot.save(screenshot_path)
        
        # Convert the image for OCR processing
        img = cv2.imread(screenshot_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast to make text more readable
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        cv2.imwrite("processed_card_screenshot.png", gray)
        
        # Extract the details based on the screenshot layout
        # The screenshot shows card details in specific regions:
        # Card number is displayed prominently in the middle
        # Expiration date is shown as MM/YY format (like 03/29)
        # CVV is shown as a 3-digit code (like 348)
        
        # Use pytesseract to get all text from the image
        card_text = pytesseract.image_to_string(gray).replace(" ", "")
        print("Extracted text from screen, searching for card details...")
        
        # Extract card number - look for 16-digit number (may be spaced as 4x4)
        card_number = ""
        card_pattern = r'(\d{4}[^\d]?\d{4}[^\d]?\d{4}[^\d]?\d{4})'
        card_match = re.search(card_pattern, card_text)
        if card_match:
            card_number = card_match.group(1).replace(" ", "").replace("-", "")
            print(f"Found card number: {card_number}")
        else:
            # Try a more permissive pattern
            card_pattern = r'(\d{4}[ -]*\d{4}[ -]*\d{4}[ -]*\d{4})'
            card_match = re.search(card_pattern, card_text)
            if card_match:
                card_number = card_match.group(1).replace(" ", "").replace("-", "")
                print(f"Found card number: {card_number}")
            else:
                print("Could not extract card number automatically")
                card_number = input("Please enter card number manually: ")
        
        # Extract expiration date - look for format MM/YY
        exp_month = ""
        exp_year = ""
        exp_pattern = r'(\d{2})[/](\d{2})'
        exp_match = re.search(exp_pattern, card_text)
        if exp_match:
            exp_month = exp_match.group(1)
            exp_year = exp_match.group(2)
            print(f"Found expiration date: {exp_month}/{exp_year}")
        else:
            print("Could not extract expiration date automatically")
            exp_month = input("Please enter expiration month (MM): ")
            exp_year = input("Please enter expiration year (YY): ")
        
        # Extract CVV - look for "CVV" or "CVC" followed by 3 digits
        cvv = ""
        cvv_pattern = r'(?:CVV|CVC|cvv)[^\d]*(\d{3})'
        cvv_match = re.search(cvv_pattern, card_text)
        if cvv_match:
            cvv = cvv_match.group(1)
            print(f"Found CVV: {cvv}")
        else:
            # If we can't find CVV with a label, look for a 3-digit number near expiration
            # This is riskier but might work since the CVV is often displayed prominently
            text_after_exp = card_text[card_text.find(exp_year) + 2:]
            cvv_simple_match = re.search(r'(\d{3})', text_after_exp)
            if cvv_simple_match:
                cvv = cvv_simple_match.group(1)
                print(f"Found CVV: {cvv}")
            else:
                print("Could not extract CVV automatically")
                cvv = input("Please enter CVV: ")
        
        return card_number, exp_month, exp_year, cvv
    
    async def run_automation(self):
        """Run the automation using collected actions"""
        print("\n*************************************************************")
        print(f"STARTING AUTOMATION WITH {len(self.actions)} ACTIONS")
        print("*************************************************************")
        
        cards_generated = 0
        
        # Reset action to perform between card generations
        reset_action = {
            "type": "click", 
            "position": [964, 130], 
            "name": "RESET", 
            "text": None, 
            "delay": 5
        }
        
        while cards_generated < self.num_cards:
            print(f"\nGenerating card {cards_generated + 1} of {self.num_cards}")
            
            try:
                # Execute each action in sequence
                for i, action in enumerate(self.actions):
                    # Add a brief pause before each action to ensure stability
                    time.sleep(0.5)
                    
                    if action["type"] == "click":
                        x, y = action["position"]
                        print(f"Step {i+1}: Clicking '{action['name']}' at position ({x}, {y})")
                        
                        # Move mouse to position first, then click
                        pyautogui.moveTo(x, y, duration=0.2)
                        time.sleep(0.2)  # Small pause before clicking
                        pyautogui.click()
                        
                        print(f"✓ Clicked at position ({x}, {y})")
                        
                        # Take screenshots at key points
                        if any(keyword in action["name"].lower() for keyword in ["create", "radio", "next", "submit"]):
                            screenshot_name = f"{action['name'].lower().replace(' ', '_')}_{cards_generated + 1}.png"
                            pyautogui.screenshot().save(screenshot_name)
                            print(f"Saved screenshot: {screenshot_name}")
                        
                        # If this is the final action, wait 5 seconds then capture the card screenshot
                        if i == len(self.actions) - 1:
                            print("\nFinal click completed. Waiting 5 seconds before capturing card details...")
                            # Add a longer delay (5 seconds as requested) to ensure the card details are fully displayed
                            time.sleep(5)
                            
                            # Take a screenshot of the card details and save it as 1.png in parent directory
                            current_dir = os.path.dirname(os.path.abspath(__file__))
                            parent_dir = os.path.dirname(current_dir)
                            screenshot_path = os.path.join(parent_dir, "1.png")
                            
                            pyautogui.screenshot().save(screenshot_path)
                            print(f"Saved card screenshot to {screenshot_path}")
                            
                            # Process the screenshot to extract card details
                            card_number, exp_month, exp_year, cvv = test_card_extraction_from_image(screenshot_path)
                            
                            if card_number and cvv:
                                print("\nSUCCESS: Found card details")
                                print(f"Card Number: {card_number}")
                                print(f"CVV: {cvv}")
                                
                                # Save card details to relay_genned.txt in the parent directory
                                output_file = os.path.join(parent_dir, "relay_genned.txt")
                                try:
                                    with open(output_file, "a") as f:
                                        # Save only card number and CVV as requested
                                        f.write(f"{card_number},{cvv}\n")
                                    # Flush the file to ensure data is written immediately
                                    f.flush()
                                    print(f"\n✅ Card details saved to {output_file}")
                                except Exception as e:
                                    print(f"Error saving to file: {e}")
                            else:
                                print("\nFAILED: Could not extract complete card details")
                                
                                # Ask for manual input if extraction fails
                                print("Please enter the card details manually:")
                                card_number = input("Card Number: ")
                                cvv = input("CVV: ")
                                
                                # Save manually entered details
                                output_file = os.path.join(parent_dir, "relay_genned.txt")
                                try:
                                    with open(output_file, "a") as f:
                                        f.write(f"{card_number},{cvv}\n")
                                    # Flush the file to ensure data is written immediately
                                    f.flush()
                                    print(f"\n✅ Card details saved to {output_file}")
                                except Exception as e:
                                    print(f"Error saving to file: {e}")
                        
                        # Use the custom delay from the action
                        delay = action.get("delay", 1)  # Default to 1 if not specified
                        if delay > 0:
                            print(f"Waiting for {delay} seconds...")
                            time.sleep(delay)
                    
                    elif action["type"] == "type":
                        try:
                            # Check if this is a random text request
                            if action["text"].lower() == 'random':
                                random_text = self.generate_random_text()
                                print(f"Step {i+1}: Typing random text: '{random_text}'")
                                pyautogui.write(random_text, interval=0.1)
                            else:
                                print(f"Step {i+1}: Typing '{action['text']}'")
                                pyautogui.write(action['text'], interval=0.1)
                            
                            print(f"✓ Typed text successfully")
                            
                            # Use the custom delay from the action
                            delay = action.get("delay", 1)  # Default to 1 if not specified
                            if delay > 0:
                                print(f"Waiting for {delay} seconds...")
                                time.sleep(delay)
                        except Exception as typing_error:
                            print(f"Error during typing: {typing_error}")
                            input("Press Enter to continue with next action (or Ctrl+C to exit)...")
                    
                    # If this is a form step, ask user to fill it
                    if action["type"] == "click" and "form" in action["name"].lower():
                        print("\nPlease fill out the card creation form")
                        input("Press Enter when you've filled the form and are ready to continue...")
                
                # Increment counter
                cards_generated += 1
                
                # If more cards need to be generated, perform reset action first
                if cards_generated < self.num_cards:
                    print(f"\nPreparing to generate card {cards_generated + 1} of {self.num_cards}...")
                    
                    # Perform reset click to prepare for next card
                    x, y = reset_action["position"]
                    print(f"Performing RESET click at position ({x}, {y})")
                    
                    # Move mouse to reset position and click
                    pyautogui.moveTo(x, y, duration=0.2)
                    time.sleep(0.2)
                    pyautogui.click()
                    
                    print(f"✓ Reset click completed")
                    print(f"Waiting {reset_action['delay']} seconds after reset...")
                    time.sleep(reset_action["delay"])
            
            except Exception as e:
                print(f"Error generating card: {e}")
                print("Please complete this card generation manually.")
                response = input("Press Enter to continue or type 'q' to quit: ")
                if response.lower() == 'q':
                    break
                
                # Still perform reset click even after an error
                try:
                    x, y = reset_action["position"]
                    print(f"Performing RESET click at position ({x}, {y}) to recover...")
                    pyautogui.moveTo(x, y, duration=0.2)
                    time.sleep(0.2)
                    pyautogui.click()
                    time.sleep(reset_action["delay"])
                except Exception as reset_error:
                    print(f"Error during reset click: {reset_error}")
                    print("Please reset manually before continuing.")
                    input("Press Enter when ready to continue...")
                
                cards_generated += 1
        
        print(f"\nCompleted generation of {cards_generated} cards")
    
    def get_mouse_position(self):
        """Utility function to help calibrate coordinates"""
        print("Move your mouse to the desired position and wait 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        position = pyautogui.position()
        print(f"Mouse position: {position}")
        return position
    
    def calibrate_coordinates(self):
        """Calibrate all coordinates manually"""
        print("\n*************************************************************")
        print("COORDINATE CALIBRATION")
        print("*************************************************************\n")
        
        print("Let's calibrate the coordinates for each element.")
        print("For each element, move your mouse to the correct position and press Enter.")
        
        # Calibrate Cards menu
        input("Position mouse over Cards menu in sidebar and press Enter...")
        self.coordinates["cards_menu"] = pyautogui.position()
        print(f"Cards menu coordinates set to {self.coordinates['cards_menu']}")
        
        # Calibrate Create Card button
        input("Position mouse over Create Card button and press Enter...")
        self.coordinates["create_card"] = pyautogui.position()
        print(f"Create Card button coordinates set to {self.coordinates['create_card']}")
        
        # Calibrate Virtual Card radio button
        input("Position mouse over Virtual Card radio button and press Enter...")
        self.coordinates["virtual_card"] = pyautogui.position()
        print(f"Virtual Card radio button coordinates set to {self.coordinates['virtual_card']}")
        
        # Calibrate Next button
        input("Position mouse over Next button and press Enter...")
        self.coordinates["next_button"] = pyautogui.position()
        print(f"Next button coordinates set to {self.coordinates['next_button']}")
        
        # Calibrate Create/Submit button
        input("Position mouse over final Create/Submit button and press Enter...")
        self.coordinates["create_button"] = pyautogui.position()
        print(f"Create/Submit button coordinates set to {self.coordinates['create_button']}")
        
        print("\nCalibration complete!")
        return True

    def find_text_on_screen(self, text, screenshot_path=None, confidence=0.7):
        """Find text on screen using OCR and return its coordinates"""
        # Take a screenshot if not provided
        if not screenshot_path:
            screenshot = pyautogui.screenshot()
            screenshot_path = "temp_screenshot.png"
            screenshot.save(screenshot_path)
        
        # Read the image
        img = cv2.imread(screenshot_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply some image processing to improve OCR accuracy
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Save the processed image
        cv2.imwrite("processed_screenshot.png", gray)
        
        # Use pytesseract to get text and bounding boxes
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Find the coordinates for the text
        min_x, min_y, max_x, max_y = None, None, None, None
        
        for i in range(len(data['text'])):
            if data['text'][i].strip() == text:
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                
                if min_x is None or x < min_x:
                    min_x = x
                if min_y is None or y < min_y:
                    min_y = y
                if max_x is None or x + w > max_x:
                    max_x = x + w
                if max_y is None or y + h > max_y:
                    max_y = y + h
        
        if min_x is not None:
            # Calculate center point
            center_x = min_x + (max_x - min_x) // 2
            center_y = min_y + (max_y - min_y) // 2
            return (center_x, center_y)
        
        return None
    
    def click_text_on_screen(self, text):
        """Find and click on text on the screen"""
        print(f"Looking for text: '{text}' on screen...")
        coordinates = self.find_text_on_screen(text)
        
        if coordinates:
            x, y = coordinates
            print(f"Found '{text}' at position ({x}, {y}). Clicking...")
            pyautogui.click(x, y)
            return True
        else:
            print(f"Could not find '{text}' on screen")
            return False

    def find_sidebar_elements(self, screenshot_path=None):
        """Find elements in the sidebar based on their position and appearance"""
        # Take a screenshot if not provided
        if not screenshot_path:
            screenshot = pyautogui.screenshot()
            screenshot_path = "temp_screenshot.png"
            screenshot.save(screenshot_path)
        
        # Use template matching to find the Cards menu item
        try:
            # Look for "Cards" in the left sidebar - common colors in the Relay interface
            # Based on the screenshot, look for a dark green sidebar with white text
            
            # Create a folder for templates if it doesn't exist
            if not os.path.exists("templates"):
                os.makedirs("templates")
            
            # Analyze the screenshot to find the sidebar
            img = cv2.imread(screenshot_path)
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Define range for green color (adjust based on the actual colors in your UI)
            lower_green = np.array([40, 40, 40])
            upper_green = np.array([80, 255, 255])
            
            # Create a mask for green regions
            mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Find contours in the mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Look for large green areas (sidebar)
            sidebar_x = None
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                # Check if this could be the sidebar (tall and on the left)
                if h > img.shape[0] * 0.5 and x < img.shape[1] * 0.3:
                    sidebar_x = x + w
                    break
            
            # Look for "Cards" text in the sidebar area
            if sidebar_x:
                # Check the area to the right of the sidebar edge
                for y in range(100, img.shape[0] - 100, 50):  # Sample at different heights
                    # Extract a region that might contain "Cards"
                    region = img[y:y+50, sidebar_x-100:sidebar_x+100]
                    cv2.imwrite(f"region_{y}.png", region)
                    
                    # Use OCR on this region
                    text = pytesseract.image_to_string(region).strip()
                    if "Cards" in text:
                        center_x = sidebar_x - 50
                        center_y = y + 25
                        return (center_x, center_y)
            
            # If OCR fails, try using image recognition
            # Use pyautogui to look for the cards icon
            cards_location = pyautogui.locateOnScreen("templates/cards_icon.png", confidence=0.7)
            if cards_location:
                center = pyautogui.center(cards_location)
                return center
            
            # As a fallback, look for text with more robust methods
            print("Trying more robust text detection for 'Cards'...")
            return self.find_text_on_screen("Cards", screenshot_path)
            
        except Exception as e:
            print(f"Error finding sidebar elements: {e}")
            return None
    
    def click_cards_in_sidebar(self):
        """Find and click on the Cards item in the sidebar"""
        print("Looking for 'Cards' in the sidebar...")
        
        # First try direct OCR approach
        try:
            coords = self.find_text_on_screen("Cards")
            if coords:
                x, y = coords
                print(f"Found 'Cards' text at ({x}, {y}). Clicking...")
                pyautogui.click(x, y)
                time.sleep(1)
                return True
        except Exception as e:
            print(f"Error with OCR approach: {e}")
        
        # If first approach fails, try the sidebar detection approach
        try:
            screenshot_path = "relay_screen.png"
            pyautogui.screenshot().save(screenshot_path)
            
            # Specifically look for the coordinates shown in the screenshot
            # Based on your screenshot, the Cards menu item appears to be in the left sidebar
            # around coordinates (X: ~64, Y: ~450) - these are estimates from the screenshot
            
            coords = self.find_sidebar_elements(screenshot_path)
            if coords:
                x, y = coords
                print(f"Found Cards menu item at ({x}, {y}). Clicking...")
                pyautogui.click(x, y)
                return True
            else:
                # Fallback: Try clicking approximately where Cards should be
                # In your screenshot, Cards appears to be at approximately (64, 450)
                print("Using fallback position for Cards menu...")
                pyautogui.click(64, 450)
                return True
        except Exception as e:
            print(f"Error with sidebar approach: {e}")
        
        # Last resort: Ask user to click
        print("Automated detection failed. Please help:")
        input("Position your cursor over the 'Cards' menu item and press Enter...")
        pyautogui.click()
        print("Clicked at user-specified position")
        return True

    def click_by_color(self, color_name):
        """Click an element by its color"""
        color_ranges = {
            "green_button": ([40, 50, 180], [80, 255, 255]),  # Light green/yellow buttons
            "dark_green": ([40, 100, 40], [80, 255, 150]),    # Dark green sidebar
            "white_text": ([0, 0, 200], [180, 30, 255])       # White text
        }
        
        if color_name not in color_ranges:
            print(f"Unknown color: {color_name}")
            return False
        
        screenshot = pyautogui.screenshot()
        screenshot_path = f"color_detection_{color_name}.png"
        screenshot.save(screenshot_path)
        
        img = cv2.imread(screenshot_path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        lower_range, upper_range = color_ranges[color_name]
        mask = cv2.inRange(hsv, np.array(lower_range), np.array(upper_range))
        cv2.imwrite(f"color_mask_{color_name}.png", mask)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        largest_area = 0
        largest_contour = None
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > largest_area and area > 1000:  # Minimum size threshold
                largest_area = area
                largest_contour = contour
        
        if largest_contour is not None:
            x, y, w, h = cv2.boundingRect(largest_contour)
            center_x = x + w//2
            center_y = y + h//2
            print(f"Found {color_name} element at ({center_x}, {center_y}). Clicking...")
            pyautogui.click(center_x, center_y)
            return True
        
        print(f"Could not find {color_name} element")
        return False

    async def delete_cards(self):
        """Main entry point for deleting cards"""
        print("Using existing logged-in browser session for card deletion")
        
        # Determine if we need to collect actions or use saved ones
        if not self.delete_actions:
            print("\n*************************************************************")
            print("DELETE ACTION COLLECTION MODE")
            print("*************************************************************")
            print("You'll be asked to perform clicks and typing for each step of the deletion process.")
            print("The program will record your actions for automation.")
            
            await self.collect_delete_actions()
            self.save_actions(is_delete=True)
        else:
            use_saved = input(f"Use {len(self.delete_actions)} saved delete actions? (y/n): ").lower() == 'y'
            if not use_saved:
                self.delete_actions = []
                await self.collect_delete_actions()
                self.save_actions(is_delete=True)
        
        # Add confirmation before starting automation
        print("\n*************************************************************")
        print("READY TO START DELETION AUTOMATION")
        print("*************************************************************")
        print(f"Collected {len(self.delete_actions)} actions that will be performed.")
        
        # Wait for user to double-click instead of typing "start"
        print("\nPosition your cursor where you want and DOUBLE-CLICK to begin the deletion automation")
        self.wait_for_double_click()
        
        print("\nDouble-click detected! Starting deletion automation process...")
        # Now run the automation using the collected actions
        await self.run_delete_automation()

    async def collect_delete_actions(self):
        """Collect all necessary actions for deleting cards"""
        print("\nPlease prepare your browser with the Relay dashboard open.")
        print("\nTIP: When asked to type text, you can enter 'random' to generate a random 5-letter string during automation.")
        print("TIP: You can specify a custom delay (in seconds) after each click.")
        input("Press Enter when ready to start collecting delete actions...")
        
        action_count = 1
        while True:
            print(f"\nDelete Action {action_count}:")
            # Automatically use incremental numbers instead of asking for description
            description = f"Delete_{action_count}"
            
            print(f"Please position your cursor where you want click #{action_count} to occur")
            input("Position cursor and press Enter when ready...")
            
            position = pyautogui.position()
            
            # Ask for delay time after this click
            delay_time = 1  # Default delay
            try:
                delay_input = input(f"Enter delay in seconds after this click (default is 1): ")
                if delay_input.strip():
                    delay_time = int(delay_input)
                    if delay_time < 0:
                        delay_time = 0
                    print(f"Will wait {delay_time} seconds after this click")
            except ValueError:
                print("Using default delay of 1 second")
            
            # Record the click action with custom delay
            self.delete_actions.append({
                "type": "click",
                "position": (position.x, position.y),
                "name": description,
                "text": None,
                "delay": delay_time
            })
            
            print(f"✅ Delete Click {action_count} captured at position {position} with {delay_time}s delay")
            
            # Ask if typing is needed after this click
            typing_needed = input(f"Do you need to type anything after click {action_count}? (type 'n' if nothing to type): ")
            if typing_needed.lower() != 'n':
                # Record the typing action
                self.delete_actions.append({
                    "type": "type",
                    "position": None,
                    "name": f"Type after Delete_{action_count}",
                    "text": typing_needed,
                    "delay": 1  # Default delay after typing
                })
                
                # Show special message for random text
                if typing_needed.lower() == 'random':
                    print(f"✅ Typing action recorded: Will generate random 5-letter text during automation")
                else:
                    print(f"✅ Typing action recorded: '{typing_needed}'")
            
            # Ask if there are more actions
            more_actions = input("\nDo you have more clicks in the delete process? (type 'n' if this is the end): ").lower()
            if more_actions == 'n':
                break
            
            action_count += 1
        
        print(f"\nCollection complete! Recorded {len(self.delete_actions)} delete actions:")
        for i, action in enumerate(self.delete_actions):
            if action["type"] == "click":
                print(f"{i+1}. Click '{action['name']}' at {action['position']} (delay: {action['delay']}s)")
            else:
                if action["text"].lower() == 'random':
                    print(f"{i+1}. Type random 5-letter string (delay: {action['delay']}s)")
                else:
                    print(f"{i+1}. Type '{action['text']}' (delay: {action['delay']}s)")

    async def run_delete_automation(self):
        """Run the automation for deleting cards using collected actions"""
        print("\n*************************************************************")
        print(f"STARTING DELETION AUTOMATION WITH {len(self.delete_actions)} ACTIONS")
        print("*************************************************************")
        
        cards_deleted = 0
        
        # If needed, add a reset action between card deletions
        reset_action = {
            "type": "click", 
            "position": [964, 130], 
            "name": "RESET", 
            "text": None, 
            "delay": 2
        }
        
        while cards_deleted < self.num_cards:
            print(f"\nDeleting card {cards_deleted + 1} of {self.num_cards}")
            
            try:
                # Execute each action in sequence
                for i, action in enumerate(self.delete_actions):
                    # Add a brief pause before each action to ensure stability
                    time.sleep(0.5)
                    
                    if action["type"] == "click":
                        x, y = action["position"]
                        print(f"Step {i+1}: Clicking '{action['name']}' at position ({x}, {y})")
                        
                        # Move mouse to position first, then click
                        pyautogui.moveTo(x, y, duration=0.2)
                        time.sleep(0.2)  # Small pause before clicking
                        pyautogui.click()
                        
                        print(f"✓ Clicked at position ({x}, {y})")
                        
                        # No OCR or card detail extraction needed for deletion
                        
                        # Use the custom delay from the action
                        delay = action.get("delay", 1)  # Default to 1 if not specified
                        if delay > 0:
                            print(f"Waiting for {delay} seconds...")
                            time.sleep(delay)
                    
                    elif action["type"] == "type":
                        try:
                            # Check if this is a random text request
                            if action["text"].lower() == 'random':
                                random_text = self.generate_random_text()
                                print(f"Step {i+1}: Typing random text: '{random_text}'")
                                pyautogui.write(random_text, interval=0.1)
                            else:
                                print(f"Step {i+1}: Typing '{action['text']}'")
                                pyautogui.write(action['text'], interval=0.1)
                            
                            print(f"✓ Typed text successfully")
                            
                            # Use the custom delay from the action
                            delay = action.get("delay", 1)  # Default to 1 if not specified
                            if delay > 0:
                                print(f"Waiting for {delay} seconds...")
                                time.sleep(delay)
                        except Exception as typing_error:
                            print(f"Error during typing: {typing_error}")
                            input("Press Enter to continue with next action (or Ctrl+C to exit)...")
                
                # Increment counter after completing all delete actions for one card
                cards_deleted += 1
                
                # If more cards need to be deleted, perform reset action first
                if cards_deleted < self.num_cards:
                    print(f"\nPreparing to delete card {cards_deleted + 1} of {self.num_cards}...")
                    
                    # Perform reset click to prepare for next card deletion
                    x, y = reset_action["position"]
                    print(f"Performing RESET click at position ({x}, {y})")
                    
                    # Move mouse to reset position and click
                    pyautogui.moveTo(x, y, duration=0.2)
                    time.sleep(0.2)
                    pyautogui.click()
                    
                    print(f"✓ Reset click completed")
                    print(f"Waiting {reset_action['delay']} seconds after reset...")
                    time.sleep(reset_action["delay"])
            
            except Exception as e:
                print(f"Error deleting card: {e}")
                print("Please complete this card deletion manually.")
                response = input("Press Enter to continue or type 'q' to quit: ")
                if response.lower() == 'q':
                    break
                
                cards_deleted += 1
        
        print(f"\nCompleted deletion of {cards_deleted} cards")

def test_card_extraction_from_image(image_path):
    """Extract card details from screenshot with focused cropping"""
    print(f"Testing card extraction from image: {image_path}")
    
    # Check if file exists
    if not os.path.isfile(image_path):
        print(f"Error: File not found at {image_path}")
        return None, None, None, None
    
    # Get the directory where the original image is located
    img_dir = os.path.dirname(image_path)
    
    try:
        # Load the original image
        original_img = Image.open(image_path)
        width, height = original_img.size
        print(f"Image dimensions: {width}x{height}")
        
        # FIRST CROP: Focus on the right panel where card details are shown
        first_crop_x = int(width * 0.6)  # Start at 60% of screen width 
        first_crop_width = width - first_crop_x
        first_crop_height = int(height * 0.45)  # Slightly larger vertical area
        
        first_crop = original_img.crop((first_crop_x, 0, width, first_crop_height))
        first_crop_path = os.path.join(img_dir, "card_area_first_crop.png")
        first_crop.save(first_crop_path)
        print(f"Created first crop: {first_crop_path}")
        
        # FINAL CROP: Focus specifically on the card
        first_crop_cv = cv2.cvtColor(np.array(first_crop), cv2.COLOR_RGB2BGR)
        
        # Use HSV color space to detect the green card
        hsv = cv2.cvtColor(first_crop_cv, cv2.COLOR_BGR2HSV)
        
        # Green color range for the card 
        lower_green = np.array([40, 40, 40])  # Darker green
        upper_green = np.array([90, 255, 255])  # Brighter green
        
        # Create a mask for green regions
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Find contours for the green regions
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for the largest green contour (likely the card)
        max_area = 0
        card_rect = None
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area and area > 1000:  # Minimum size threshold
                max_area = area
                x, y, w, h = cv2.boundingRect(contour)
                card_rect = (x, y, w, h)
        
        # If we found a green card area, crop to it
        if card_rect:
            x, y, w, h = card_rect
            # Add a slightly larger margin
            margin = 10
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(first_crop.width - x, w + (2 * margin))
            h = min(first_crop.height - y, h + (2 * margin))
            
            card_only = first_crop.crop((x, y, x + w, y + h))
        else:
            # Fallback if color detection fails
            card_only = first_crop.crop((
                int(first_crop.width * 0.05),  # 5% from left
                int(first_crop.height * 0.1),  # 10% from top
                int(first_crop.width * 0.95),  # 95% from left
                int(first_crop.height * 0.65)   # 65% from top
            ))
        
        card_only_path = os.path.join(img_dir, "card_area_only.png")
        card_only.save(card_only_path)
        print(f"Created card-only crop: {card_only_path}")
        
        # Enhance the card image for better OCR
        card_cv = cv2.cvtColor(np.array(card_only), cv2.COLOR_RGB2BGR)
        
        # Increase contrast and sharpness
        card_cv = cv2.convertScaleAbs(card_cv, alpha=1.5, beta=0)
        
        # Convert to grayscale for OCR
        gray = cv2.cvtColor(card_cv, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding to improve text extraction
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Extract text using multiple OCR approaches for better results
        card_text_gray = pytesseract.image_to_string(gray)
        card_text_binary = pytesseract.image_to_string(binary)
        
        # Combine results and clean up
        card_text = card_text_gray + "\n" + card_text_binary
        card_text = card_text.replace('@@', '00').replace('@', '0')
        
        print("\nRaw OCR output:")
        print(card_text)
        print("\nSearching for card details...")
        
        # Extract card number - look for 16-digit number (may be spaced as 4x4)
        card_number = ""
        card_patterns = [
            r'(\d{4}[ -]*\d{4}[ -]*\d{4}[ -]*\d{4})',  # Standard 16-digit with spaces/dashes
            r'(\d{4})[\s]*(\d{4})[\s]*(\d{4})[\s]*(\d{4})'  # 4 groups with any whitespace
        ]
        
        for pattern in card_patterns:
            card_matches = re.findall(pattern, card_text)
            if card_matches:
                if isinstance(card_matches[0], tuple):
                    # If match is a tuple (from groups), join them
                    card_number = ''.join(card_matches[0])
                else:
                    card_number = card_matches[0]
                card_number = card_number.replace(" ", "").replace("-", "")
                print(f"Found card number: {card_number}")
                break
        
        # If standard patterns fail, look for sequences of 4 digits
        if not card_number:
            digit_sequences = re.findall(r'\b\d{4}\b', card_text)
            if len(digit_sequences) >= 4:
                card_number = ''.join(digit_sequences[:4])
                print(f"Found card number by digit sequences: {card_number}")
        
        # Extract expiration date - look for MM/YY format
        exp_month = ""
        exp_year = ""
        exp_patterns = [
            r'(\d{2})[/](\d{2})',  # Standard MM/YY
            r'THRU[^\d]*(\d{2})[/](\d{2})',  # THRU MM/YY
            r'(\d{2})[\s]*[/][\s]*(\d{2})'  # MM / YY with spaces
        ]
        
        for pattern in exp_patterns:
            exp_match = re.search(pattern, card_text)
            if exp_match:
                exp_month = exp_match.group(1)
                exp_year = exp_match.group(2)
                
                # Fix common OCR errors in month detection
                # If month is outside valid range (1-12), it's likely a misread 0
                if int(exp_month) > 12:
                    # If first digit is 9, it's likely a misread 0
                    if exp_month[0] == '9':
                        exp_month = '0' + exp_month[1]
                    # If second digit is 9, it might be a misread 0 
                    elif exp_month[1] == '9':
                        exp_month = exp_month[0] + '0'
                
                print(f"Found expiration date: {exp_month}/{exp_year}")
                break
        
        # Define a function to clean CVV values from OCR errors
        def clean_cvv(raw_cvv):
            """Convert OCR errors in CVV to correct digits"""
            # Common OCR character substitutions
            ocr_fixes = {
                'O': '0', 'o': '0', 'Q': '0', 'D': '0',
                'I': '1', 'l': '1', 'i': '1',
                'Z': '2', 'z': '2',
                'B': '8', 'b': '8',
                'G': '6', 'C': '0',
                'S': '5', 's': '5'
            }
            
            # Special case handling for known patterns
            if raw_cvv.upper() in ["CWO7B", "CVO7B", "CWOTB", "O7B"]:
                return "078"
            
            # Replace letters with corresponding digits
            cvv_cleaned = ""
            for char in raw_cvv:
                if char.isdigit():
                    cvv_cleaned += char
                elif char.upper() in ocr_fixes:
                    cvv_cleaned += ocr_fixes[char.upper()]
                # Ignore other characters
            
            # If we have a partial CVV (1-2 digits), try to complete it
            if len(cvv_cleaned) < 3 and len(raw_cvv) >= 3:
                # Fill remaining positions with best guesses
                for i in range(len(cvv_cleaned), 3):
                    if i < len(raw_cvv):
                        char = raw_cvv[i]
                        if char.upper() in ocr_fixes:
                            cvv_cleaned += ocr_fixes[char.upper()]
                        else:
                            # Default to '0' if can't determine
                            cvv_cleaned += '0'
                    else:
                        cvv_cleaned += '0'
            
            # Return only the first 3 digits if longer
            if len(cvv_cleaned) > 3:
                return cvv_cleaned[:3]
                
            return cvv_cleaned
        
        # Extract CVV - first look for CVV/CW pattern followed by characters
        cvv = ""
        
        # If still no match, try more general CVV patterns
        if not cvv:
            cvv_patterns = [
                r'[Cc][Vv][Vv][^\d]*(\d{3})',     # CVV 123
                r'[Cc][Vv][^\d]*(\d{3})',         # CV 123 (OCR might miss a V)
                r'[Cc][Ww][^\d]*(\d{3})',         # CW 123 (common OCR error)
                r'[Cc][Vv][Vv][\s]*(\d+)',        # CVV with any digits
                r'[Cc][Vv][Vv][\s]*([^\s]+)',     # CVV with any characters
                r'[Cc][Ww][\s]*([^\s]+)'          # CW with any characters
            ]
            
            for pattern in cvv_patterns:
                cvv_match = re.search(pattern, card_text)
                if cvv_match:
                    cvv_raw = cvv_match.group(1)
                    # Clean up the raw CVV text - convert OCR errors to digits
                    cvv = clean_cvv(cvv_raw)
                    print(f"Found CVV: {cvv} (raw: {cvv_raw})")
                    break
        
        # Last resort: search for 3-digit numbers after specific markers
        if not cvv:
            # Try to find "cvv" or "cw" or something nearby
            cvv_locations = []
            for match in re.finditer(r'[Cc][VvWw]', card_text):
                cvv_locations.append(match.start())
            
            if cvv_locations:
                # Check the text after a potential CVV label
                for loc in cvv_locations:
                    # Look at up to 15 characters after the "cv" or "cw"
                    text_after = card_text[loc:loc+15]
                    # Look for anything that might be digits
                    potential_cvv = re.search(r'[O0]?[0-9IlB][0-9IlB8]', text_after)
                    if potential_cvv:
                        cvv_raw = potential_cvv.group(0)
                        cvv = clean_cvv(cvv_raw)
                        if len(cvv) < 3:  # Try to ensure we have 3 digits
                            print(f"Found CVV (proximity search): {cvv} (raw: {cvv_raw})")
                        break
        
        # If we still couldn't find CVV with a label, look for 3-digit sequences
        if not cvv:
            # Avoid matching ZIP codes
            if "91007" in card_text:
                card_text = card_text.replace("91007", "")
                
            # Find all 3-digit sequences
            all_3digits = re.findall(r'\b\d{3}\b', card_text)
            if all_3digits:
                # Use the first 3-digit sequence that's not part of other data
                for digit_seq in all_3digits:
                    if digit_seq not in card_number and digit_seq != exp_month + exp_year[:1]:
                        cvv = digit_seq
                        print(f"Found CVV by elimination: {cvv}")
                        break

        print("\nExtracted card details:")
        print(f"Card Number: {card_number}")
        print(f"Expiration: {exp_month}/{exp_year}")
        print(f"CVV: {cvv}")
        
        return card_number, exp_month, exp_year, cvv
        
    except Exception as e:
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None

if __name__ == "__main__":
    # Handle paths correctly when relay is a sub-repo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    
    # Try to find the screenshot image
    image_paths = [
        os.path.join(parent_dir, "1.png"),  # From parent directory
        "/Users/bentang/Desktop/CardGen/1.png",  # Absolute path
    ]
    
    # Try each path until one works
    success = False
    card_number = ""
    exp_month = ""
    exp_year = ""
    cvv = ""
    
    for path in image_paths:
        print(f"Trying image path: {path}")
        if os.path.exists(path):
            print(f"File exists at: {path}")
            
            print("Running card extraction test...")
            # Run the test and get results
            card_number, exp_month, exp_year, cvv = test_card_extraction_from_image(path)
            
            if card_number:
                print("\nSUCCESS: Found card details")
                print(f"RESULT: {card_number},{cvv}")
                success = True
                break
            else:
                print(f"Could not extract details from {path}, trying next path...")
        else:
            print(f"File does not exist at: {path}")
    
    if success:
        # Save card details to relay_genned.txt in the parent directory (main repo)
        output_file = os.path.join(parent_dir, "relay_genned.txt")
        try:
            with open(output_file, "a") as f:
                # Save only card number and CVV as requested
                f.write(f"{card_number},{cvv}\n")
            print(f"\n✅ Card details saved to {output_file}")
        except Exception as e:
            print(f"Error saving to file: {e}")
    else:
        print("\nFAILED: Could not extract complete card details from any path")
        
        # Ask user to provide path interactively
        user_path = input("Please enter the full path to your screenshot file: ")
        if user_path:
            print(f"Trying user-provided path: {user_path}")
            card_number, exp_month, exp_year, cvv = test_card_extraction_from_image(user_path)
            
            if card_number:
                print("\nSUCCESS: Found card details")
                print(f"RESULT: {card_number},{cvv}")
                
                # Save card details to relay_genned.txt in the parent directory
                output_file = os.path.join(parent_dir, "relay_genned.txt")
                try:
                    with open(output_file, "a") as f:
                        f.write(f"{card_number},{cvv}\n")
                    print(f"\n✅ Card details saved to {output_file}")
                except Exception as e:
                    print(f"Error saving to file: {e}")
            else:
                print("\nFAILED: Could not extract complete card details")