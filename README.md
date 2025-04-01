# Virtual Card Generator

An automated tool for generating and managing virtual cards through Capital One and Relay web interfaces using Python.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/benjamin-githubprofile/vccGen.git
cd vccGen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
playwright install
```

3. Create a `.env` file in the root directory:
```plaintext
# Capital One credentials
CAPITAL_ONE_USERNAME=your_username
CAPITAL_ONE_PASSWORD=your_password
# Second Capital One profile (optional)
CAPITAL_ONE_USERNAME_2=second_username
CAPITAL_ONE_PASSWORD_2=second_password
# Relay credentials
RELAY_USERNAME=your_relay_username
RELAY_PASSWORD=your_relay_password
```

4. For Relay automation: Install Tesseract OCR
   - Windows: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

## Usage

1. Run the script:
```bash
python main.py
```

2. Choose your bank:
   - Option 1: Capital One
   - Option 2: Relay

3. For Capital One:
   - Select profile (Profile 1 or Profile 2)
   - Choose action (Create or Delete virtual cards)
   - For creation:
     - Enter the number of virtual cards you want to generate
     - The script will launch an automated browser session
     - Log into your Capital One account
     - Navigate through the verification process (requires manual input)
     - Generate the requested number of virtual cards
     - Save card details to `cap_genned.txt`
   - For deletion:
     - Enter the number of cards to delete
     - For Profile 1, choose which card to use (ending in 8060 or 2653)
     - The script will automatically delete the specified number of cards

4. For Relay:
   - Choose your action:
     1. Create virtual cards
     2. Delete cards
   - For card creation:
     - First-time use will enter "Action Collection Mode" where you'll teach the automation by demonstrating the clicks
     - Subsequent runs can use saved actions
     - Generated card details are saved to `relay_genned.txt`
   - For card deletion:
     - Similar to creation, first record the deletion process
     - Automation will repeat the recorded actions for the specified number of cards

## Output Files

- Capital One cards: `cap_genned.txt`
- Relay cards: `relay_genned.txt`

## Features

### Capital One
- Support for multiple user profiles
- Card selection for different physical cards
- Automated login and navigation
- Multi-card generation support
- Card deletion capabilities
- Automated navigation through verification process
- Card details extraction and storage
- Environment variable configuration
- Success verification for card deletion

### Relay
- Support for both card creation and deletion
- Action recording system for teaching the automation
- Reusable saved actions for repeated tasks
- Customizable delays between actions
- Browser positioning guide
- Double-click activation system
- Error recovery mechanisms
- OCR-based text recognition on screen

## Technical Details

### Capital One Automation
- Uses Playwright for browser automation
- Robust element selection with multiple fallback methods
- Success verification for operations
- Automatic zoom adjustment for better element visibility

### Relay Automation
- Uses pyautogui for screen interaction
- OpenCV and PIL for image processing
- OCR capabilities for card detail extraction
- JSON-based action storage
- Supports random text generation
- Custom delay configuration per action
- Color-based element detection

## Troubleshooting

- **Authentication Issues**: Ensure your credentials in the `.env` file are correct
- **Visibility Problems**: The automation sets page zoom to 80% to ensure buttons are visible
- **Element Detection**: If the automation fails to find elements, it will attempt alternative selectors
- **Manual Fallback**: For critical operations, the tool will prompt for manual input if automation fails

## Note

This tool is for educational purposes only. Please ensure you comply with both Capital One's and Relay's terms of service and policies.

## Requirements

- Python 3.8+
- Playwright
- PyAutoGUI
- OpenCV
- Pillow
- Pytesseract
- Required environment variables in `.env` file