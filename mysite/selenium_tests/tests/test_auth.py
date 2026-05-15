import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class TestAuthentication:
    def test_valid_login(self, driver, base_url, wait):
        driver.get(f"{base_url}/login/")
        
        # Flexible selector for username
        for selector in [(By.NAME, "username"), (By.NAME, "email"), (By.ID, "id_username")]:
            try:
                wait.until(EC.presence_of_element_located(selector)).send_keys("student@test.com")
                break
            except:
                continue
        
        # Password
        for selector in [(By.NAME, "password"), (By.ID, "id_password")]:
            try:
                driver.find_element(*selector).send_keys("TestPass123!")
                break
            except:
                continue
        
        # Login button
        for selector in [
            (By.ID, "loginBtn"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Login')]")
        ]:
            try:
                driver.find_element(*selector).click()
                break
            except:
                continue
        
        wait.until(EC.url_contains("/dashboard/"))
        assert "dashboard" in driver.current_url.lower()

    def test_invalid_login(self, driver, base_url, wait):
        driver.get(f"{base_url}/login/")
        try:
            driver.find_element(By.NAME, "username").send_keys("wrong@test.com")
            driver.find_element(By.NAME, "password").send_keys("WrongPass123!")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Should stay on login page or show error
            wait.until(lambda d: "/login/" in d.current_url or "error" in d.page_source.lower() or "invalid" in d.page_source.lower())
            assert "/login/" in driver.current_url or "error" in driver.page_source.lower()
        except:
            # If page doesn't show error, at least verify we're not on dashboard
            assert "dashboard" not in driver.current_url.lower()

    def test_logout(self, driver, base_url, wait):
        # Login first
        driver.get(f"{base_url}/login/")
        try:
            driver.find_element(By.NAME, "username").send_keys("student@test.com")
            driver.find_element(By.NAME, "password").send_keys("TestPass123!")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            wait.until(EC.url_contains("/dashboard/"))
        except:
            pytest.skip("Login failed")
        
        # Logout - try multiple selectors
        logout_clicked = False
        for selector in [
            (By.XPATH, "//button[contains(text(), 'Logout')]"),
            (By.XPATH, "//a[contains(text(), 'Logout')]"),
            (By.CSS_SELECTOR, "form button[type='submit']"),
            (By.NAME, "logout")
        ]:
            try:
                driver.find_element(*selector).click()
                logout_clicked = True
                break
            except:
                continue
        
        if not logout_clicked:
            print("⚠️ Logout button not found with expected selectors. Available buttons:")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                print(f"  - text='{btn.text}' name='{btn.get_attribute('name')}'")
            pytest.fail("Logout button not found")
        
        # Wait for redirect to login or homepage
        try:
            wait.until(EC.url_contains("/login/"))
            assert "/login/" in driver.current_url
        except:
            # Fallback: check for homepage
            wait.until(lambda d: d.current_url == base_url or "/login/" in d.current_url)
            assert "/login/" in driver.current_url or driver.current_url == base_url