import os
import time
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration & Setup ---

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Get credentials and config from environment variables
ORCID_EMAIL = os.getenv('ORCID_EMAIL')
ORCID_PASSWORD = os.getenv('ORCID_PASSWORD')
OVERLEAF_PROJECT_URL = os.getenv('OVERLEAF_PROJECT_URL')
BIB_FILENAME = os.getenv('BIB_FILENAME')

def setup_driver():
    """Sets up the Selenium WebDriver for Chrome."""
    chrome_options = Options()
    # Use headless mode for automated runs (e.g., GitHub Actions, CRON)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# --- Core Logic Functions ---

def login_to_overleaf(driver, email, password):
    """Logs into Overleaf using ORCID credentials."""
    logging.info("Navigating to Overleaf login page...")
    driver.get("https://www.overleaf.com/login")
    
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='orcid']"))).click()
    time.sleep(2) # Pause after action

    # Enter credentials on the ORCID page
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "username-input"))).send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "signin-button").click()
    time.sleep(2) # Pause after action

    WebDriverWait(driver, 20).until(EC.url_contains("overleaf.com/project"))
    logging.info("Login successful.")

def update_bibliography(driver, project_url, bib_filename):
    """Navigates to the project, finds the bib file, and refreshes it."""
    logging.info(f"Navigating to project: {project_url}")
    driver.get(project_url)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-testid='file-tree']")))
    logging.info("Project page loaded.")
    time.sleep(2) # Pause after page load

    # Click on the bibliography file
    try:
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[span[text()='{bib_filename}']]"))
        ).click()
        logging.info(f"Successfully navigated to '{bib_filename}'.")
        time.sleep(2) # Pause after action
    except TimeoutException:
        logging.error(f"Could not find or click the file '{bib_filename}'.")
        raise

    # Click the refresh button, retrying if it becomes stale
    for attempt in range(3):
        try:
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Refresh']]"))).click()
            logging.info("Refresh button clicked.")
            time.sleep(2) # Pause after action
            
            WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.XPATH, "//*[text()='Refreshing...']")))
            logging.info("✅ Bibliography successfully refreshed.")
            return # Exit the loop and function on success
        except StaleElementReferenceException:
            logging.warning(f"Stale element detected on attempt {attempt + 1}. Retrying...")
            time.sleep(2) # Wait before retrying
            
    raise Exception("Could not click the refresh button after multiple attempts.")

# --- Main Execution ---

def main():
    """Main function to run the web scraping workflow."""
    if not all([ORCID_EMAIL, ORCID_PASSWORD, OVERLEAF_PROJECT_URL, BIB_FILENAME]):
        logging.error("One or more environment variables are missing. Please check your .env file.")
        return

    driver = setup_driver()
    try:
        login_to_overleaf(driver, ORCID_EMAIL, ORCID_PASSWORD)
        update_bibliography(driver, OVERLEAF_PROJECT_URL, BIB_FILENAME)
        
        logging.info("Adding a final 10-second pause before closing...")
        time.sleep(10)
        
    except Exception as e:
        logging.error(f"An error occurred during the workflow: {e}")
        # Taking a screenshot on error is great for debugging headless runs
        driver.save_screenshot("error_screenshot.png")
        logging.info("Saved screenshot to error_screenshot.png")
    finally:
        logging.info("Closing the browser.")
        driver.quit()

if __name__ == "__main__":
    main()