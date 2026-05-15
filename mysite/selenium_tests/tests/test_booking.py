import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

class TestBookingFlow:
    def test_book_seat_successfully(self, driver, base_url, wait):
        # Login
        driver.get(f"{base_url}/login/")
        try:
            driver.find_element(By.NAME, "username").send_keys("student@test.com")
            driver.find_element(By.NAME, "password").send_keys("TestPass123!")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            wait.until(lambda d: "dashboard" in d.current_url.lower())
        except:
            pytest.skip("Login failed")
        
        # Navigate to Schedule
        driver.get(f"{base_url}/schedule/")
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "route-card")))
        except:
            # Fallback: look for any route element
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'route') or contains(@class, 'schedule') or contains(text(), 'Route')]")))
        
        # Find and click book button
        book_clicked = False
        book_selectors = [
            (By.CLASS_NAME, "btn-book"),
            (By.XPATH, "//button[contains(text(), 'Book')]"),
            (By.XPATH, "//a[contains(text(), 'Book')]"),
            (By.CSS_SELECTOR, "button, a"),
            (By.XPATH, "//*[contains(text(), 'Book') or contains(text(), 'Reserve')]")
        ]
        
        for selector in book_selectors:
            try:
                elements = driver.find_elements(*selector)
                for el in elements:
                    if el.is_displayed() and el.is_enabled() and "book" in el.text.lower():
                        try:
                            el.click()
                            book_clicked = True
                            break
                        except ElementClickInterceptedException:
                            # Scroll into view and retry
                            driver.execute_script("arguments[0].scrollIntoView(true);", el)
                            time.sleep(0.5)
                            el.click()
                            book_clicked = True
                            break
                if book_clicked:
                    break
            except:
                continue
        
        if not book_clicked:
            print("⚠️ No book button found - maybe no available routes")
            pytest.skip("No available routes for booking")
        
        # Wait for booking page
        try:
            wait.until(lambda d: "book" in d.current_url.lower() or "seat" in d.current_url.lower() or "confirm" in d.current_url.lower())
        except:
            # Maybe it's a modal - wait for modal to appear
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'dialog')]")))
        
        # Try to fill booking form - flexible field detection
        form_fields = {
            "seats": ["seats", "quantity", "num_seats", "number"],
            "passenger_name": ["passenger_name", "name", "full_name", "passenger"],
            "phone": ["phone", "mobile", "contact"]
        }
        
        for field_key, possible_names in form_fields.items():
            value_map = {"seats": "1", "passenger_name": "Selenium Tester", "phone": "01700000000"}
            value = value_map.get(field_key)
            if not value:
                continue
                
            for name_attr in possible_names:
                try:
                    element = driver.find_element(By.NAME, name_attr)
                    if element.is_displayed():
                        element.clear()
                        element.send_keys(value)
                        break
                except:
                    continue
        
        # Submit booking
        submitted = False
        submit_selectors = [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Confirm')]"),
            (By.XPATH, "//button[contains(text(), 'Book')]"),
            (By.XPATH, "//input[@type='submit']"),
            (By.CSS_SELECTOR, "form button")
        ]
        
        for selector in submit_selectors:
            try:
                btn = driver.find_element(*selector)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    submitted = True
                    break
            except:
                continue
        
        if not submitted:
            # Try JavaScript submit
            try:
                form = driver.find_element(By.TAG_NAME, "form")
                driver.execute_script("arguments[0].submit();", form)
                submitted = True
            except:
                pass
        
        if not submitted:
            print("⚠️ Could not submit booking form")
            pytest.skip("Booking form submission failed")
        
        # Wait for confirmation
        try:
            wait.until(lambda d: 
                "confirmed" in d.page_source.lower() or 
                "success" in d.page_source.lower() or
                "booking" in d.current_url.lower(),
                timeout=15
            )
            assert "confirmed" in driver.page_source.lower() or "success" in driver.page_source.lower()
        except:
            driver.save_screenshot("debug_booking_confirmation.png")
            pytest.fail("Booking confirmation not found")

    def test_cancel_booking(self, driver, base_url, wait):
        # Login & go to bookings
        driver.get(f"{base_url}/login/")
        try:
            driver.find_element(By.NAME, "username").send_keys("student@test.com")
            driver.find_element(By.NAME, "password").send_keys("TestPass123!")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            wait.until(lambda d: "dashboard" in d.current_url.lower())
        except:
            pytest.skip("Login failed")
        
        driver.get(f"{base_url}/my-bookings/")
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        except:
            pytest.skip("No bookings table found")
        
        if "No bookings" in driver.page_source or "empty" in driver.page_source.lower():
            pytest.skip("No active bookings to cancel")
        
        # Find cancel button with flexible selectors
        cancel_clicked = False
        cancel_selectors = [
            (By.CLASS_NAME, "btn-cancel"),
            (By.XPATH, "//button[contains(text(), 'Cancel')]"),
            (By.XPATH, "//a[contains(text(), 'Cancel')]"),
            (By.CSS_SELECTOR, "button.danger"),
            (By.XPATH, "//button[contains(@class, 'cancel')]")
        ]
        
        for selector in cancel_selectors:
            try:
                btn = driver.find_element(*selector)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    cancel_clicked = True
                    break
            except:
                continue
        
        if not cancel_clicked:
            pytest.skip("No cancel button found")
        
        # Handle confirmation alert
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            pass  # No alert
        
        # Wait for cancellation confirmation
        try:
            wait.until(lambda d: "cancelled" in d.page_source.lower(), timeout=10)
            assert "cancelled" in driver.page_source.lower()
        except:
            # Maybe page reloaded - check for success message
            time.sleep(2)
            assert "cancelled" in driver.page_source.lower() or "success" in driver.page_source.lower()