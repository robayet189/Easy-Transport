import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
from datetime import datetime

@pytest.fixture(scope="session")
def driver():
    """Initialize Chrome WebDriver with options"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Uncomment for headless mode
    # chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    yield driver
    
    driver.quit()

@pytest.fixture(scope="function")
def setup(driver):
    """Setup for each test"""
    base_url = "http://127.0.0.1:8000"
    yield {
        'driver': driver,
        'base_url': base_url
    }