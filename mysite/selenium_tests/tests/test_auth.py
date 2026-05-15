import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class TestAuthentication:
    def test_valid_login(self, driver, base_url, wait):
        driver.get(f"{base_url}/login/")
        time.sleep(1)  # Let page render
        
        # ✅ Replace these with ACTUAL selectors from your debug output
        driver.find_element(By.NAME, "username").send_keys("student@test.com")  # ← Check your debug output!
        driver.find_element(By.NAME, "password").send_keys("TestPass123!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()  # ← Or use actual button ID
        
        # Wait for dashboard with flexible check
        time.sleep(2)
        assert "dashboard" in driver.current_url.lower() or "welcome" in driver.page_source.lower()

    def test_logout(self, driver, base_url, wait):
        # Login first
        driver.get(f"{base_url}/login/")
        driver.find_element(By.NAME, "username").send_keys("student@test.com")
        driver.find_element(By.NAME, "password").send_keys("TestPass123!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        
        # ✅ Find logout using actual HTML
        # Try: form submit, link click, or button click
        try:
            # Method 1: Submit logout form
            logout_form = driver.find_element(By.XPATH, "//form[contains(@action, 'logout')]")
            driver.execute_script("arguments[0].submit();", logout_form)
        except:
            try:
                # Method 2: Click logout link/button
                logout_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Logout') or contains(text(), 'Log out')]")
                logout_btn.click()
            except:
                pytest.fail("Logout element not found - check your HTML")
        
        time.sleep(2)
        assert "/login/" in driver.current_url or "login" in driver.page_source.lower()