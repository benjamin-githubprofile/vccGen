# Capital One Virtual Card Generator

An automated tool for generating virtual cards through Capital One's web interface using Python and Playwright.

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
```

## Usage

1. Run the script:
```bash
python main.py
```

2. The script will:
   - Check for your Capital One credentials in the `.env` file
   - Prompt you to enter the number of virtual cards you want to generate
   - Launch an automated browser session
   - Log into your Capital One account
   - Navigate through the verification process (requires manual input)
   - Generate the requested number of virtual cards
   - Save card details to `cap_genned.txt`

3. During the process:
   - You will need to manually complete the verification when prompted
   - Follow the on-screen instructions for any required manual actions
   - Card details will be automatically saved in CSV format (number,month,year,cvv)

## Output

Generated card details are saved to `cap_genned.txt` in the following format:

## Features

- Automated login to Capital One
- Multi-card generation support
- Automated navigation through verification process
- Card details extraction and storage
- Environment variable configuration for secure credential management

## Note

This tool is for educational purposes only. Please ensure you comply with Capital One's terms of service and policies.