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
CAPITAL_ONE_USERNAME=your_username
CAPITAL_ONE_PASSWORD=your_password
RELAY_USERNAME=your_relay_username
RELAY_PASSWORD=your_relay_password
```

## Usage

1. Run the script:
```bash
python main.py
```

2. Choose your bank:
   - Option 1: Capital One
   - Option 2: Relay

3. For Capital One:
   - The script will check for your credentials in the `.env` file
   - Prompt you to enter the number of virtual cards you want to generate
   - Launch an automated browser session
   - Log into your Capital One account
   - Navigate through the verification process (requires manual input)
   - Generate the requested number of virtual cards
   - Save card details to `cap_genned.txt`

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
- Automated login
- Multi-card generation support
- Automated navigation through verification process
- Card details extraction and storage
- Environment variable configuration

### Relay
- Support for both card creation and deletion
- Action recording system for teaching the automation
- Reusable saved actions for repeated tasks
- Customizable delays between actions
- Browser positioning guide
- Double-click activation system
- Error recovery mechanisms

## Technical Details

### Relay Automation
- Uses pyautogui for screen interaction
- OpenCV and PIL for image processing
- OCR capabilities for card detail extraction
- JSON-based action storage
- Supports random text generation
- Custom delay configuration per action

## Note

This tool is for educational purposes only. Please ensure you comply with both Capital One's and Relay's terms of service and policies.

## Requirements

- Python 3.x
- Playwright
- PyAutoGUI
- OpenCV
- Pillow
- Pytesseract
- Required environment variables in `.env` file