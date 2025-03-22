# Survey Bot

A Selenium-based bot that automates filling out surveys.

## Installation

1. **Install Python** (if not already installed):  
   [Download Python](https://www.python.org/downloads/) and ensure `pip` is installed.

2. **Clone this repository**  
   ```sh
   git clone https://github.com/johnsonduong/survey-automation.git
   cd survey-automation
   ```

3. **Install dependencies**  
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up configuration**  
   - Edit `config.json` and provide survey details (e.g., restaurant number, visit date, amount).

## Usage

Run the bot using:  
```sh
python survey_bot.py
```

The bot will navigate through the survey, filling out responses automatically.

Validation code will be saved to `validation_codes.txt`.

## Notes

- Only works with Popeyes surveys at the moment.  
- Ensure Chrome is installed and up to date.  
- Uses `undetected_chromedriver` to bypass bot detection.
