import json
import time
import random
import ssl
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ssl._create_default_https_context = ssl._create_unverified_context

with open('config.json', 'r') as file:
    config = json.load(file)

# Browser options
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-popup-blocking")
driver = uc.Chrome(options=options)
driver.maximize_window()
driver.get(config["survey_url"])

def human_typing(element, text):
    """
    Simulates human typing to avoid bot detection.
    """
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.1))
    element.send_keys(Keys.RETURN)

def safe_find_element(by, value, retries=5):
    """
    Finds the HTML element on the page.
    """
    for attempt in range(retries):
        try:
            element = driver.find_element(by, value)
            print(f"✅ Found element: {value}")
            return element
        except NoSuchElementException:
            print(f"⚠️ Attempt {attempt + 1}: Could not find element {value}")
            time.sleep(0.05) 
    print(f"❌ Element not found after {retries} attempts: {value}")
    return None

def click_element(element):
    """
    Clicks the HTMl element on the page.
    """
    try:
        element.click()
        time.sleep(0.8)
        return True
    except ElementClickInterceptedException:
        print("⚠️ Click intercepted, retrying...")
        time.sleep(0.05)
        return click_element(element)
    except Exception as e:
        print(f"⚠️ Error clicking element: {e}")
    return False

def click_next():
    """
    Clicks the next button.
    """
    next_button = safe_find_element(By.ID, "NextButton")
    if next_button:
        click_element(next_button)

def select_first_option():
    """
    Selects the first option.
    """
    try:
        radio_buttons = driver.find_elements(By.XPATH, "//label/span")
        if radio_buttons:
            click_element(radio_buttons[0])
            print("✅ Selected first available radio option")
    except Exception as e:
        print(f"⚠️ Error selecting first radio option: {e}")

def handle_multiple_radio_groups():
    """
    Automatically answers when there are multiple radio groups.
    """
    try:
        # Wait for radio groups to load
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ChoiceStructure"))
        )

        # Find all radio groups
        radio_groups = driver.find_elements(By.CSS_SELECTOR, "ul.ChoiceStructure")

        # Iterate through each group
        for group in radio_groups:
            # Find the first clickable LABEL (not the input)
            first_label = group.find_element(By.CSS_SELECTOR, "label.SingleAnswer")
            click_element(first_label)
            print("✅ Selected first option in a radio group")
            time.sleep(0.05)

    except Exception as e:
        print(f"⚠️ Error handling multiple radio groups: {e}")

def select_radio_answers():
    """
    Automatically fills a table with radio answers.
    """
    try:
        # Wait for the table to load
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr.ChoiceRow"))
        )

        # Find all rows in the table
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.ChoiceRow")

        # Iterate through each row (question)
        for row in rows:
            # Find all radio button labels in the current row
            radio_labels = row.find_elements(By.CSS_SELECTOR, "label.q-radio")

            # Click the first label (e.g., "Highly Satisfied")
            if radio_labels:
                radio_labels[0].click()
                print("✅ Selected first radio option for the question.")
                time.sleep(0.05)

        print("✅ All questions answered.")
    except Exception as e:
        print(f"⚠️ Error selecting radio answers: {e}")

def fill_text_input():
    """
    Automatically fills all input fields and textareas on the current page using human-like typing.
    """
    try:
        # Find all text input fields
        text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='TEXT']")
        for input_field in text_inputs:
            if input_field.is_displayed() and input_field.is_enabled():
                input_field.clear()
                human_typing(input_field, "...")
                print(f"✅ Filled input field: {input_field.get_attribute('id') or input_field.get_attribute('name')}")

        # Find all textareas
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        for textarea in textareas:
            if textarea.is_displayed() and textarea.is_enabled():
                textarea.clear()
                human_typing(textarea, "...") 
                print(f"✅ Filled textarea: {textarea.get_attribute('id') or textarea.get_attribute('name')}")

    except Exception as e:
        print(f"⚠️ Error filling input fields: {e}")

def extract_validation_code(file_path="validation_codes.txt"):
    """
    Extracts the validation code from the page and appends it to a .txt file.
    """
    try:
        # Wait for the validation code to appear
        validation_code_element = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Validation Code:')]"))
        )

        # Extract the text containing the validation code
        validation_text = validation_code_element.text

        # Extract the code (assuming it's in the format "Validation Code: 434346345")
        validation_code = validation_text.split("Validation Code:")[-1].strip()

        # Append the validation code to the .txt file
        with open(file_path, "a") as file:
            file.write(f"{validation_code}\n")
        print(f"✅ Validation code saved to {file_path}")

        return validation_code

    except Exception as e:
        print(f"⚠️ Error extracting validation code: {e}")
        return None
    
def fill_input_by_label_text(label_text, input_value):
    try:
        # Find the label containing the specified text
        label = driver.find_element(By.XPATH, f"//label[contains(., '{label_text}')]")
        
        # Find the associated input field
        input_field = label.find_element(By.XPATH, ".//ancestor::td/following-sibling::td//input")
        
        # Remove the readonly attribute if present
        driver.execute_script("arguments[0].removeAttribute('readonly')", input_field)
        
        # Clear and fill the input field
        input_field.clear()
        human_typing(input_field, input_value)
        print(f"✅ Filled input for label: {label_text}")

    except NoSuchElementException:
        print(f"⚠️ Label or input field not found: {label_text}")
    except Exception as e:
        print(f"⚠️ Error filling input for label {label_text}: {e}")

def fill_time_picker_by_label_text(label_text, hour_value, minute_value, ampm_value):
    try:
        # Find the label containing the specified text
        label = driver.find_element(By.XPATH, f"//label[contains(., '{label_text}')]")
        
        # Find the associated time picker fields
        hour_field = label.find_element(By.XPATH, ".//ancestor::tr//select[contains(@id, '#1')]")
        minute_field = label.find_element(By.XPATH, ".//ancestor::tr//select[contains(@id, '#2')]")
        ampm_field = label.find_element(By.XPATH, ".//ancestor::tr//select[contains(@id, '#3')]")
        
        # Select the specified values by clicking the corresponding <option> elements
        hour_field.find_element(By.XPATH, f".//option[@value='{hour_value}']").click()
        minute_field.find_element(By.XPATH, f".//option[@value='{minute_value}']").click()
        ampm_field.find_element(By.XPATH, f".//option[@value='{ampm_value}']").click()
        
        print(f"✅ Filled time picker for label: {label_text}")

    except NoSuchElementException:
        print(f"⚠️ Time picker fields not found for label: {label_text}")
    except Exception as e:
        print(f"⚠️ Error filling time picker for label {label_text}: {e}")

time.sleep(3)

try:
    # Click into the iframe
    iframe = safe_find_element(By.CLASS_NAME, "Home_iframe__T3nfU")
    if iframe:
        driver.switch_to.frame(iframe)
    
    # Preliminary pages of the survey
    click_next()

    fill_input_by_label_text("Restaurant", config["restaurant_number"])
    fill_input_by_label_text("Date", config["visit_date"])
    fill_time_picker_by_label_text(
        "Time",
        config["time"]["hour"],
        config["time"]["minute"], 
        config["time"]["ampm"] 
    )
    fill_input_by_label_text("Total", config["amount"])

    click_next()
    click_next()

    # Subsequent Q&A
    while True:
        select_first_option()
        select_radio_answers()
        fill_text_input()
        handle_multiple_radio_groups()
        click_next()

        # Extract the validation code and conclude the survey
        validation_code = extract_validation_code()
        if validation_code:
            print(f"✅ Survey completed! Validation Code: {validation_code}")
            break
        
        time.sleep(0.05)
except Exception as e:
    print(f"⚠️ Error: {e}")

time.sleep(30)
driver.quit()