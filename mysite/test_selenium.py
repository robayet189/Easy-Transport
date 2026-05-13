from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time

# Setup
options = Options()
# options.add_argument('--headless')  # Uncomment for background run
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)
BASE_URL = 'http://127.0.0.1:8000'

# Results tracking
results = []
passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        results.append(f"✅ PASSED: {name}")
        passed += 1
    else:
        results.append(f"❌ FAILED: {name}")
        failed += 1
        driver.save_screenshot(f"screenshots/{name.replace(' ', '_')}.png")

# Create screenshots folder
import os
os.makedirs('screenshots', exist_ok=True)

print("=" * 60)
print("SELENIUM TESTING STARTED")
print("=" * 60)

# ==================== AUTH TESTS ====================
print("\n📝 AUTH TESTS")

# TC-01: Homepage loads
driver.get(BASE_URL)
test("Homepage loads", 'Next Route' in driver.title)

# TC-02: Register page loads
driver.get(f'{BASE_URL}/register/')
test("Register page loads", 'Register' in driver.title or 'Create Account' in driver.page_source)

# TC-03: Login page loads
driver.get(f'{BASE_URL}/login/')
test("Login page loads", 'Login' in driver.title or 'Sign In' in driver.page_source)

# ==================== ADMIN TESTS ====================
print("\n📝 ADMIN TESTS")

# TC-04: Admin login
driver.get(f'{BASE_URL}/login/')
time.sleep(1)
try:
    driver.find_element(By.NAME, 'username').send_keys('admin@test.com')
    driver.find_element(By.NAME, 'password').send_keys('admin123')
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(2)
    test("Admin login", '/admin_page' in driver.current_url or '/dashboard' in driver.current_url)
except:
    test("Admin login", False)

# TC-05: Admin dashboard
driver.get(f'{BASE_URL}/admin_page/dashboard/')
time.sleep(1)
has_stats = len(driver.find_elements(By.CSS_SELECTOR, '.stat-card, .stats-grid')) > 0
test("Admin dashboard shows stats", has_stats)

# TC-06: Admin fleet page
driver.get(f'{BASE_URL}/admin_page/fleet/')
time.sleep(1)
has_table = len(driver.find_elements(By.CSS_SELECTOR, '.data-table, table')) > 0
test("Admin fleet page", has_table)

# TC-07: Admin schedule page
driver.get(f'{BASE_URL}/admin_page/schedule/')
time.sleep(1)
has_schedule = 'Schedule' in driver.page_source
test("Admin schedule page", has_schedule)

# ==================== DRIVER TESTS ====================
print("\n📝 DRIVER TESTS")

# TC-08: Driver login page
driver.get(f'{BASE_URL}/driver/login/')
time.sleep(1)
has_login = len(driver.find_elements(By.CSS_SELECTOR, 'input, form')) > 0
test("Driver login page", has_login)

# TC-09: Driver dashboard (if logged in)
try:
    driver.find_element(By.NAME, 'username').send_keys('sulivan@test.com')
    driver.find_element(By.NAME, 'password').send_keys('driver123')
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(2)
    test("Driver login", '/driver/dashboard' in driver.current_url)
except:
    test("Driver login", False)

# ==================== HOMEPAGE TESTS ====================
print("\n📝 HOMEPAGE TESTS")

driver.get(BASE_URL)
time.sleep(1)

# TC-10: Navigation exists
has_nav = len(driver.find_elements(By.TAG_NAME, 'nav')) > 0
test("Navigation bar exists", has_nav)

# TC-11: Hero section
has_hero = len(driver.find_elements(By.CSS_SELECTOR, '.hero, h1')) > 0
test("Hero section visible", has_hero)

# TC-12: Theme toggle
has_toggle = len(driver.find_elements(By.CSS_SELECTOR, '.theme-toggle, #themeToggle')) > 0
test("Theme toggle exists", has_toggle)

# TC-13: Features section
driver.get(f'{BASE_URL}/#features')
time.sleep(1)
has_features = len(driver.find_elements(By.CSS_SELECTOR, '.feature-card, .features-grid')) > 0
test("Features section", has_features)

# ==================== TRACKING TESTS ====================
print("\n📝 TRACKING TESTS")

# TC-14: Track bus page
driver.get(f'{BASE_URL}/track-bus/')
time.sleep(1)
test("Track bus page", 'Track' in driver.page_source or 'map' in driver.page_source.lower())

# ==================== RESULTS ====================
print("\n" + "=" * 60)
print("TEST RESULTS")
print("=" * 60)

for r in results:
    print(r)

total = passed + failed
print(f"\n━━━━━━━━━━━━━━━━━━━━")
print(f"✅ Passed: {passed}/{total}")
print(f"❌ Failed: {failed}/{total}")
print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
print(f"━━━━━━━━━━━━━━━━━━━━")

# Generate simple HTML report
html = f"""
<html>
<head><title>Selenium Test Report</title>
<style>
body{{font-family:Arial;margin:40px;background:#0b0b14;color:white}}
h1{{color:#ff4757}}
.pass{{color:#4ade80}}.fail{{color:#ff4757}}
.card{{background:#13131f;border-radius:12px;padding:20px;margin:10px 0}}
.stats{{display:flex;gap:20px;margin:20px 0}}
.stat{{background:#13131f;border-radius:12px;padding:24px;text-align:center;flex:1}}
</style></head>
<body>
<h1>🚀 Selenium Test Report</h1>
<p>Date: {datetime.now().strftime('%d %B %Y, %I:%M %p')}</p>
<p>Base URL: {BASE_URL}</p>
<div class="stats">
<div class="stat"><h2 style="color:#4ade80">{passed}</h2>Passed</div>
<div class="stat"><h2 style="color:#ff4757">{failed}</h2>Failed</div>
<div class="stat"><h2>{passed+failed}</h2>Total</div>
</div>
<h2>Results:</h2>
{''.join([f'<div class="card"><span class="{"pass" if "PASSED" in r else "fail"}">{r}</span></div>' for r in results])}
</body></html>
"""

with open('selenium_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n📄 Report saved: selenium_report.html")
driver.quit()