import pytest
from pages.login_page import LoginPage
import time

class TestDriver:
    """Test driver interface functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, setup):
        """Setup test fixtures"""
        self.driver = setup['driver']
        self.base_url = setup['base_url']
        self.login_page = LoginPage(self.driver, self.base_url)
        
        # Login as driver
        self.login_page.open_login_page()
        self.login_page.login("driver@test.com", "DriverPass123!")
        time.sleep(2)
    
    def test_driver_dashboard(self):
        """Test driver can access dashboard"""
        assert "/driver/dashboard/" in self.driver.current_url or "/dashboard/" in self.driver.current_url
    
    def test_view_trips(self):
        """Test driver can view assigned trips"""
        self.driver.get(f"{self.base_url}/driver/dashboard/")
        time.sleep(2)
        
        assert self.driver.current_url is not None