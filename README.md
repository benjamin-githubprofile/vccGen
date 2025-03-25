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
```

3. Create a `.env` file in the root directory:
```plaintext
CAPITAL_ONE_USERNAME=your_username
CAPITAL_ONE_PASSWORD=your_password
```

## Usage

Run the script:
```bash
python main.py
```

Follow the prompts to specify the number of virtual cards to generate.

## Features

- Automated login to Capital One
- Multi-card generation support
- Automated navigation through verification process
- Card details extraction and storage
- Environment variable configuration for secure credential management

## Note

This tool is for educational purposes only. Please ensure you comply with Capital One's terms of service and policies.