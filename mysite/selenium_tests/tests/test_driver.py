import pytest
import time
from selenium.webdriver.common.by import By

class TestDriverModule:
    def test_driver_login_and_trip_view(self, driver, base_url, wait):
        driver.get(f"{base_url}/login/")
        time.sleep(1)
        
        # Driver login uses same form as student
        driver.find_element(By.ID, "username").send_keys("driver@test.com")
        driver.find_element(By.ID, "password").send_keys("DriverPass123!")
        driver.find_element(By.ID, "loginBtn").click()
        
        time.sleep(3)
        
        # Driver should be on dashboard (role-based redirect handled by backend)
        assert "dashboard" in driver.current_url.lower()
        
        # Check for trip-related content
        assert "trip" in driver.page_source.lower() or "schedule" in driver.page_source.lower()