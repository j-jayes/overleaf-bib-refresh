import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
from selenium.common.exceptions import StaleElementReferenceException

# Load environment variables from .env file
load_dotenv()

# Get ORCID credentials from environment variables
orcid_email = os.getenv('ORCID_EMAIL')
orcid_password = os.getenv('ORCID_PASSWORD')

def setup_driver():
    """
    Setup the Selenium WebDriver.
    """
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment this to run in headless mode for CRON jobs
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--lang=en-US")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def handle_cookie_consent(driver):
    """
    Dismisses the cookie consent banner if it appears.
    """
    try:
        cookie_consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        cookie_consent_button.click()
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.ID, "onetrust-accept-btn-handler"))
        )
        print("Cookie consent banner dismissed.")
        time.sleep(1) # Pause after action
    except Exception as e:
        print("No cookie consent banner found or error occurred:", str(e))

def login_to_overleaf(driver, email, password):
    """Logs into Overleaf using ORCID credentials."""
    driver.get("https://www.overleaf.com/login")
    
    orcid_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='orcid']"))
    )
    orcid_button.click()
    time.sleep(1) # Pause after action

    handle_cookie_consent(driver)

    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "username-input"))
    ).send_keys(email)
    
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "signin-button").click()
    time.sleep(1) # Pause after action

    WebDriverWait(driver, 20).until(
        EC.url_contains("overleaf.com/project")
    )
    print("Login successful.")
    time.sleep(1) # Pause after stage completion

def navigate_to_project(driver):
    """
    Navigates directly to a specific project on Overleaf.
    """
    try:
        driver.get("https://www.overleaf.com/project/66f4186e60aea777158f4a42")
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-testid='file-tree']"))
        )
        print("Successfully navigated to the specific project.")
        time.sleep(1) # Pause after stage completion
    except Exception as e:
        print(f"Failed to navigate to the specific project: {e}")
        raise

def navigate_to_bibliography(driver):
    """
    Navigates to the bibliography section of the project.
    """
    try:
        bibliography_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='bibliography.bib']]"))
        )
        bibliography_button.click()
        print("Successfully navigated to the bibliography file.")
        time.sleep(1) # Pause after action
    except Exception as e:
        print(f"Failed to find or click the 'bibliography.bib' file: {e}")
        raise

def refresh_bibliography(driver):
    """
    Clicks the refresh button, retrying if the element becomes stale, and waits for the process to complete.
    """
    for attempt in range(3):
        try:
            refresh_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Refresh']]"))
            )
            refresh_button.click()
            print("Refresh button clicked successfully.")
            time.sleep(1) # Pause after action
            
            WebDriverWait(driver, 20).until(
                EC.invisibility_of_element_located((By.XPATH, "//*[text()='Refreshing...']"))
            )
            print("Bibliography successfully refreshed.")

            print("Adding a final 10-second pause before closing...")
            time.sleep(10)
            
            return

        except StaleElementReferenceException:
            print(f"Stale element detected on attempt {attempt + 1}. Retrying...")
            time.sleep(1)
            
        except Exception as e:
            print(f"Failed to refresh the bibliography: {e}")
            raise
            
    raise Exception("Could not click the refresh button after multiple attempts.")

# Main workflow
driver = setup_driver()

try:
    login_to_overleaf(driver, orcid_email, orcid_password)
    navigate_to_project(driver)
    navigate_to_bibliography(driver)
    refresh_bibliography(driver)
    exit(0)
except Exception as e:
    print(f"An error occurred: {str(e)}")
    exit(1)
finally:
    driver.quit()