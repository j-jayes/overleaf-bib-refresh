"""
Automates refreshing the bibliography in an Overleaf project using Selenium.

This script logs into Overleaf via ORCID credentials, navigates to the specified project, 
and refreshes the bibliography section by clicking the "Refresh" button. 
The script is intended to be run periodically using a CRON job to ensure that 
the bibliography is always up-to-date in the Overleaf document.

Steps involved:
1. Login to Overleaf using ORCID credentials.
2. Navigate to the desired Overleaf project.
3. Locate and navigate to the bibliography section of the project.
4. Click the refresh button to update the bibliography.
   - The refresh button is identified by the CSS selector: "#panel-ide .btn-primary"

Requirements:
- Selenium WebDriver
- ChromeDriver (or another WebDriver)
- Credentials for ORCID login
- CRON job setup for periodic execution

Usage:
- Deploy this script in a CRON job for periodic execution.
"""
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

load_dotenv()

orcid_email = os.getenv('ORCID_EMAIL')
orcid_password = os.getenv('ORCID_PASSWORD')

def setup_driver():
    """
    Setup the Selenium WebDriver.
    """
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def login_orcid(driver, orcid_email, orcid_password):
    """
    Logs into Overleaf using ORCID credentials, assuming the cookie banner is handled manually.
    """
    # Navigate to Overleaf login page
    driver.get("https://www.overleaf.com/login")
    
    # Click the ORCID login button
    orcid_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".text-center:nth-child(2) .login-btn"))
    )
    orcid_button.click()

    # Wait for the ORCID login page to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#username-input"))  # ORCID email field
    )

    # Enter ORCID credentials using the correct selectors
    driver.find_element(By.CSS_SELECTOR, "#username-input").send_keys(orcid_email)
    driver.find_element(By.CSS_SELECTOR, "#password").send_keys(orcid_password)
    
    # Submit the login form
    driver.find_element(By.ID, "signin-button").click()

    # Wait for the redirect back to Overleaf after login
    WebDriverWait(driver, 20).until(
        EC.url_contains("overleaf.com/project")
    )
    print("Login successful.")

def navigate_to_project(driver):
    """
    Navigates to the first project in the list on Overleaf.
    """
    try:
        # Wait for the project list to load and click the first project link
        project_link = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "tr:nth-child(1) a"))
        )
        project_link.click()
        print("Successfully navigated to the first project.")
    except Exception as e:
        print("Failed to navigate to the project:", str(e))


def navigate_to_bibliography(driver):
    """
    Navigates to the bibliography section of the project.
    """
    # wait for 1 second to ensure the page is loaded
    time.sleep(1)
    try:
        # Wait for the bibliography link to be clickable and click it
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
    try:
        # Wait for the refresh button to be clickable and click it
        refresh_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#panel-ide .btn-primary"))
        )
        refresh_button.click()
        print("Successfully clicked the refresh button.")
    except Exception as e:
        print("Failed to click the refresh button:", str(e))

# Example usage of the login function
driver = setup_driver()
# orcid_email = "0000-0003-4967-4869"
# orcid_password = "Vivera54321"
login_orcid(driver, orcid_email, orcid_password)
navigate_to_project(driver)
navigate_to_bibliography(driver)
refresh_bibliography(driver)
