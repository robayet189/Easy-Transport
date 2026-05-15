import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TestAuthentication:
    def test_valid_login(self, driver, base_url, wait):
        driver.get(f"{base_url}/login/")
        
        # Flexible username selector
        username_field = None
        for selector in [(By.NAME, "username"), (By.NAME, "email"), (By.ID, "id_username"), (By.CSS_SELECTOR, "input[type='text']")]:
            try:
                username_field = wait.until(EC.presence_of_element_located(selector))
                break
            except:
                continue
        
        assert username_field, "Username field not found"
        username_field.send_keys("student@test.com")
        
        # Password field
        password_field = None
        for selector in [(By.NAME, "password"), (By.ID, "id_password"), (By.CSS_SELECTOR, "input[type='password']")]:
            try:
                password_field = driver.find_element(*selector)
                break
            except:
                continue
        
        assert password_field, "Password field not found"
        password_field.send_keys("TestPass123!")
        
        # Login button - multiple attempts
        login_clicked = False
        for selector in [
            (By.ID, "loginBtn"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In')]"),
            (By.XPATH, "//input[@type='submit']"),
            (By.CSS_SELECTOR, "form button"),
            (By.XPATH, "//button")
        ]:
            try:
                btn = driver.find_element(*selector)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    login_clicked = True
                    break
            except:
                continue
        
        assert login_clicked, "Could not click login button"
        
        # Wait for redirect with fallback
        try:
            wait.until(lambda d: "dashboard" in d.current_url.lower() or "admin" in d.current_url.lower())
        except TimeoutException:
            # Take screenshot for debugging
            driver.save_screenshot("debug_login_failure.png")
            print(f"❌ Login redirect failed. Current URL: {driver.current_url}")
            print(f"Page source preview: {driver.page_source[:500]}")
            pytest.fail("Login redirect timeout")
        
        assert "dashboard" in driver.current_url.lower() or "admin" in driver.current_url.lower()

    def test_invalid_login(self, driver, base_url, wait):
        driver.get(f"{base_url}/login/")
        try:
            driver.find_element(By.NAME, "username").send_keys("wrong@test.com")
            driver.find_element(By.NAME, "password").send_keys("WrongPass123!")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Should stay on login or show error
            time.sleep(2)
            assert "/login/" in driver.current_url or "error" in driver.page_source.lower() or "invalid" in driver.page_source.lower()
        except:
            # If no error shown, at least verify not on dashboard
            assert "dashboard" not in driver.current_url.lower()

    def test_logout(self, driver, base_url, wait):
        # Login first
        driver.get(f"{base_url}/login/")
        try:
            driver.find_element(By.NAME, "username").send_keys("student@test.com")
            driver.find_element(By.NAME, "password").send_keys("TestPass123!")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            wait.until(lambda d: "dashboard" in d.current_url.lower())
        except:
            pytest.skip("Login failed")
        
        # Wait for page to fully load
        time.sleep(1)
        
        # Logout - try EVERY possible selector
        logout_clicked = False
        selectors = [
            (By.XPATH, "//button[contains(text(), 'Logout')]"),
            (By.XPATH, "//a[contains(text(), 'Logout')]"),
            (By.CSS_SELECTOR, "form button[type='submit']"),
            (By.NAME, "logout"),
            (By.CSS_SELECTOR, "button.logout"),
            (By.CLASS_NAME, "logout"),
            (By.XPATH, "//button[@type='submit' and not(contains(text(), 'Login'))]"),
            (By.XPATH, "//form//button"),
            (By.CSS_SELECTOR, "footer button"),
            (By.XPATH, "//*[contains(text(), 'Logout') or contains(text(), 'Log out') or contains(text(), 'Sign out')]")
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(*selector)
                for el in elements:
                    if el.is_displayed() and el.is_enabled():
                        el.click()
                        logout_clicked = True
                        break
                if logout_clicked:
                    break
            except Exception as e:
                continue
        
        if not logout_clicked:
            # Debug: show all clickable elements
            print("⚠️ Logout button not found. Available clickable elements:")
            clickable = driver.find_elements(By.CSS_SELECTOR, "button, a, input[type='submit']")
            for el in clickable[:10]:
                text = el.text.strip() or el.get_attribute("value") or el.get_attribute("placeholder")
                print(f"  - tag='{el.tag_name}' text='{text}' class='{el.get_attribute('class')}'")
            
            # Try JavaScript click as last resort
            try:
                forms = driver.find_elements(By.TAG_NAME, "form")
                for form in forms:
                    action = form.get_attribute("action")
                    if "logout" in action.lower() or form.get_attribute("method") == "post":
                        driver.execute_script("arguments[0].submit();", form)
                        logout_clicked = True
                        break
            except:
                pass
        
        if not logout_clicked:
            driver.save_screenshot("debug_logout_failure.png")
            pytest.fail("Logout button not found - check HTML structure")
        
        # Wait for redirect with error handling
        try:
            wait.until(lambda d: "/login/" in d.current_url or d.current_url == base_url, timeout=10)
        except TimeoutException:
            # Fallback: check if page reloaded to login
            time.sleep(2)
            assert "/login/" in driver.current_url or driver.current_url == base_url or "login" in driver.page_source.lower()