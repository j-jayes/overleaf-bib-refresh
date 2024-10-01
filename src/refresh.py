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
    chrome_options.add_argument("--headless")  # Uncomment this to run in headless mode for CRON jobs
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")

    # Optionally set geolocation to mimic the USA or other regions
    chrome_options.add_argument("--lang=en-US")  # Set language to US English
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Reduce bot-like behavior detection
    
    # Initialize WebDriver using ChromeDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def handle_cookie_consent(driver):
    """
    Dismisses the cookie consent banner if it appears.
    """
    try:
        # Wait for the cookie consent banner and click the "Accept" button
        cookie_consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        cookie_consent_button.click()
        
        # Wait for the cookie consent banner to disappear
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.ID, "onetrust-accept-btn-handler"))
        )
        print("Cookie consent banner dismissed.")
    except Exception as e:
        print("No cookie consent banner found or error occurred:", str(e))  # Log the error for GitHub Actions logs

def login_orcid(driver, orcid_email, orcid_password):
    """
    Logs into Overleaf using ORCID credentials.
    """
    # Navigate to Overleaf login page
    driver.get("https://www.overleaf.com/login")
    
    # Click the ORCID login button
    orcid_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".text-center:nth-child(2) .login-btn"))
    )
    orcid_button.click()

    # sleep for 1 second to ensure the page is loaded
    time.sleep(1)

    # Handle cookie consent before proceeding
    handle_cookie_consent(driver)

    # sleep for 1 second to ensure the page is loaded
    time.sleep(1)

    # Wait for ORCID login page to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#username-input"))  # ORCID email field
    )

    # Enter ORCID credentials
    driver.find_element(By.CSS_SELECTOR, "#username-input").send_keys(orcid_email)
    driver.find_element(By.CSS_SELECTOR, "#password").send_keys(orcid_password)
    
    # Submit the login form
    driver.find_element(By.ID, "signin-button").click()

    # Wait for redirect to the Overleaf project dashboard
    WebDriverWait(driver, 20).until(
        EC.url_contains("overleaf.com/project")
    )
    print("Login successful.")

def navigate_to_project(driver):
    """
    Navigates to the first project in the list on Overleaf.
    """
    # wait for 4 seconds to ensure the page is loaded
    time.sleep(4)
    try:
        # Wait for project list to be present
        project_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(1) a"))
        )
        
        # Ensure the project link is visible and clickable
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "tr:nth-child(1) a"))
        )
        
        # Click the project link
        project_link.click()
        print("Successfully navigated to the first project.")
    except Exception as e:
        print("Failed to navigate to the project:", str(e))

def navigate_to_bibliography(driver):
    """
    Navigates to the bibliography section of the project.
    """
    # Adding a short wait to ensure the project page is fully loaded
    time.sleep(1)
    try:
        # Wait for the bibliography link and click it
        bibliography_link = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".sr-only+ .item-name-button"))
        )
        bibliography_link.click()
        print("Successfully navigated to the bibliography section.")
    except Exception as e:
        print("Failed to navigate to the bibliography:", str(e))

def refresh_bibliography(driver):
    """
    Clicks the refresh button in the bibliography section.
    """
    # Wait one second to ensure the page is loaded
    time.sleep(1)
    try:
        # Wait for the refresh button and click it
        refresh_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#panel-ide .btn-primary"))
        )
        refresh_button.click()
        # wait 5 seconds for the refresh to complete
        time.sleep(5)
        print("Successfully clicked the refresh button.")
    except Exception as e:
        print("Failed to click the refresh button:", str(e))

# Main workflow
driver = setup_driver()

try:
    login_orcid(driver, orcid_email, orcid_password)
    navigate_to_project(driver)
    navigate_to_bibliography(driver)
    refresh_bibliography(driver)
    print("Bibliography refresh completed successfully.")
    exit(0)  # Exit with success
except Exception as e:
    print(f"An error occurred: {str(e)}")
    exit(1)  # Exit with failure
finally:
    driver.quit()
