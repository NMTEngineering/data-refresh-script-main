from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
import sys
import urllib.parse

# --- CONFIGURATION ---
# We use your API Key directly here to simplify debugging
SCRAPER_API_KEY = "4e0f35d8236f741f56d86ac31c941f95"

def get_proxy_url(target_url):
    """Wraps the target URL in the ScraperAPI Gateway format"""
    # 1. Encode the URL (e.g., turns 'http://...' into 'http%3A%2F%2F...')
    encoded_url = urllib.parse.quote(target_url)
    # 2. Add render=true to make sure Javascript loads
    return f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={encoded_url}&render=true"

# --- SETUP CHROME ---
options = Options()
options.add_argument("--headless=new") 
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-blink-features=AutomationControlled')

print("🚀 Initializing Chrome Driver (Gateway Mode)...")
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Driver initialized.")
except Exception as e:
    print(f"❌ Driver Init Failed: {e}")
    sys.exit(1)

# --- SCRAPING LOGIC ---
base_url = "https://www.yellowpages-uae.com/uae/bolt?page={}"
data = []
role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

# Reduced to 2 pages for testing speed
for page in range(1, 3):  
    print(f"\n🔁 Scraping page {page}...")
    
    # 1. CONSTRUCT GATEWAY URL
    target_url = base_url.format(page)
    proxy_url = get_proxy_url(target_url)
    
    print(f"   ⏳ Sending request to ScraperAPI...")
    
    try:
        # 2. LOAD PAGE via GATEWAY
        driver.get(proxy_url)
        
        # Check if ScraperAPI gave us an error page
        if "Request failed" in driver.page_source:
            print("❌ ScraperAPI returned an error.")
            continue

        # 3. INCREASED TIMEOUT to 60s (Residential proxies are slower)
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
        )
        company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
        
        if not company_cards:
            print("⚠️ No cards found (Page might be empty).")
            continue

        print(f"   ✅ Found {len(company_cards)} companies.")

        for i in range(len(company_cards)):
            try:
                # Refresh elements
                company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
                link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
                
                real_link = link_elem.get_attribute("href")
                company_name = link_elem.text.strip()
                
                # 4. OPEN DETAIL PAGE VIA GATEWAY
                # We must wrap the detail link in the proxy URL too!
                detail_proxy_url = get_proxy_url(real_link)
                
                # Open in new tab
                driver.execute_script("window.open(arguments[0]);", detail_proxy_url)
                driver.switch_to.window(driver.window_handles[-1])
                
                # Wait for detail page load
                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # --- Extraction ---
                mobile = ''
                try:
                    m = soup.find("a", id=lambda x: x and "lblMobile" in x)
                    mobile = m.text.strip() if m else ''
                except: pass

                phone = ''
                try:
                    p = soup.find("a", id=lambda x: x and "lblPhone" in x)
                    phone = p.text.strip() if p else ''
                except: pass

                website = ''
                try:
                    w = soup.find("button", attrs={"data-url": True})
                    if w and "website" in w.text.lower(): website = w['data-url']
                except: pass

                location = ""
                try:
                    info = soup.find("div", class_="grid grid-cols-2")
                    if info:
                        for p in info.find_all("p"):
                            if "City :" in p.text:
                                location = p.find_all("span")[1].text.strip() + ", UAE"
                except: pass

                product_type = ""
                try:
                    rs = driver.find_element(By.CLASS_NAME, "flex.justify-between")
                    pls = rs.find_elements(By.XPATH, ".//a[@class='text-[#1e2f71]']")
                    p_list = [pl.text.strip() for pl in pls if 'brands' not in pl.get_attribute('href').lower()]
                    product_type = ", ".join(p_list)
                except: pass

                role = "Not Described"
                full_text = soup.get_text(" ", strip=True).lower()
                for k in role_keywords:
                    if k in full_text: role = k.capitalize(); break

                print(f"   --> Extracted: {company_name}")

                data.append({
                    'Company Name': company_name, 'Website URL': website, 'Product Types': product_type,
                    'Mobile Number': mobile, 'Phone Number': phone, 'Location': location,
                    'Role': role, 'Contact Supplier URL': real_link
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as e:
                # print(f"   ❌ Error on card: {e}") 
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

    except Exception as e:
        print(f"⚠️ Page Load Error: {e}")

# Save CSV
if data:
    with open("yellowpages_bolts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("✅ CSV Saved: yellowpages_bolts.csv")
else:
    print("❌ No data collected.")

driver.quit()
