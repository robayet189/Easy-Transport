import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class TestAuthentication:
    def test_valid_login(self, driver, base_url, wait):
        driver.get(f"{base_url}/login/")
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("student@test.com")
        driver.find_element(By.NAME, "password").send_keys("TestPass123!")
        driver.find_element(By.ID, "loginBtn").click()
        wait.until(EC.url_contains("/dashboard/"))
        assert "dashboard" in driver.current_url

    def test_invalid_login(self, driver, base_url, wait):
        driver.get(f"{base_url}/login/")
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("wrong@test.com")
        driver.find_element(By.NAME, "password").send_keys("WrongPass123!")
        driver.find_element(By.ID, "loginBtn").click()
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Invalid"))
        assert "/login/" in driver.current_url

    def test_logout(self, driver, base_url, wait):
        # Login first
        driver.get(f"{base_url}/login/")
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("student@test.com")
        driver.find_element(By.NAME, "password").send_keys("TestPass123!")
        driver.find_element(By.ID, "loginBtn").click()
        wait.until(EC.url_contains("/dashboard/"))
        
        # Logout
        driver.find_element(By.XPATH, "//button[contains(text(), 'Logout') or @type='submit']").click()
        wait.until(EC.url_contains("/login/"))
        assert "/login/" in driver.current_url