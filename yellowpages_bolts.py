#found first 20 companies but failed at 1st card
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.common.exceptions import TimeoutException # Import specific exception
# from bs4 import BeautifulSoup
# import time
# import csv
# import sys
# import urllib.parse
# import os # Ensure os is imported for path handling

# # --- CONFIGURATION ---
# SCRAPER_API_KEY = "4e0f35d8236f741f56d86ac31c941f95"

# def get_proxy_url(target_url):
#     encoded_url = urllib.parse.quote(target_url)
#     return f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={encoded_url}&render=true"

# # --- SETUP CHROME ---
# options = Options()
# options.add_argument("--headless=new") 
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--window-size=1920,1080")
# options.add_argument('--disable-blink-features=AutomationControlled')

# print("🚀 Initializing Chrome Driver (Debugging Mode)...")
# try:
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)
#     # Set overall page load timeout
#     driver.set_page_load_timeout(90)
#     print("✅ Driver initialized.")
# except Exception as e:
#     print(f"❌ Driver Init Failed: {e}")
#     sys.exit(1)

# # --- SCRAPING LOGIC ---
# base_url = "https://www.yellowpages-uae.com/uae/bolt?page={}"
# data = []
# # Rest of variables...

# for page in range(1, 3):  # Running 2 pages for quick debug
#     print(f"\n🔁 Scraping page {page}...")
    
#     target_url = base_url.format(page)
#     proxy_url = get_proxy_url(target_url)
    
#     print(f"   ⏳ Sending request to ScraperAPI (max 90s)...")
    
#     try:
#         # Load Page
#         driver.get(proxy_url)
        
#         # --- Wait for elements with explicit timeout handling ---
#         try:
#             WebDriverWait(driver, 60).until(
#                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
#             )
#             # If successful, continue to scrape loop...
            
#             company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
            
#             if not company_cards:
#                 print("⚠️ No cards found (Page might be empty).")
#                 continue
    
#             print(f"   ✅ Found {len(company_cards)} companies. Starting extraction...")
            
#             # --- START SCRAPING LOOP ---
#             for i in range(len(company_cards)):
#                 # ... (Your existing scraping logic for cards goes here) ...
#                 # To keep it short for debugging, we will skip the detailed loop for now
#                 pass
#             # --- END SCRAPING LOOP ---


#         except TimeoutException:
#             # THIS BLOCK RUNS ON FAILURE
#             print("\n❌ TIMEOUT: Could not find company cards within 60 seconds.")
            
#             # --- DEBUG STEP 1: Screenshot ---
#             screenshot_path = f"debug_timeout_page_{page}.png"
#             driver.save_screenshot(screenshot_path)
#             print(f"📸 Screenshot saved: {screenshot_path}")
            
#             # --- DEBUG STEP 2: HTML Dump ---
#             print("\n--- HTML DUMP (First 500 chars) ---")
#             print(driver.page_source[:500])
#             print("------------------------------------\n")

#             # This will create artifacts you can download:
#             print("📝 Check the 'scrape-output-csvs' artifact for the screenshot.")
#             continue # Move to the next page


#     except Exception as e:
#         print(f"⚠️ Network Error during GET: {e}")


# # --- FINAL SAVE & CLEANUP ---
# if data:
#     # ... (Your save logic here) ...
#     print("✅ CSV Saved.")
# else:
#     # If no data, check the screenshots and HTML dump!
#     print("❌ No data collected. Please examine the debug output and screenshots.")

# driver.quit()








#debugging 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException # Import specific exception
from bs4 import BeautifulSoup
import time
import csv
import sys
import urllib.parse
import os 

# --- CONFIGURATION ---
SCRAPER_API_KEY = "4e0f35d8236f741f56d86ac31c941f95"

def get_proxy_url(target_url):
    """Wraps the target URL in the ScraperAPI Gateway format"""
    encoded_url = urllib.parse.quote(target_url)
    return f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={encoded_url}&render=true"

# --- SETUP CHROME ---
options = Options()
options.add_argument("--headless=new") 
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-blink-features=AutomationControlled')

print("🚀 Initializing Chrome Driver...")
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(90)
    print("✅ Driver initialized.")
except Exception as e:
    print(f"❌ Driver Init Failed: {e}")
    sys.exit(1)

# --- SCRAPING LOGIC ---
base_url = "https://www.yellowpages-uae.com/uae/bolt?page={}"
data = []
role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

for page in range(1, 3):  # Running 2 pages for quick debug
    print(f"\n🔁 Scraping page {page}...")
    
    target_url = base_url.format(page)
    proxy_url = get_proxy_url(target_url)
    
    try:
        driver.get(proxy_url)
        
        # We know this block succeeds now
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
        )
        company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
        
        if not company_cards:
            print("⚠️ No cards found.")
            continue

        print(f"   ✅ Found {len(company_cards)} companies. Starting extraction...")

        for i in range(len(company_cards)):
            try:
                # --- NEW DEBUG LOG ---
                print(f"      ---> Processing Card {i+1}...")
                
                # Refresh elements
                company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
                link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
                
                real_link = link_elem.get_attribute("href")
                company_name = link_elem.text.strip()
                
                # OPEN DETAIL PAGE VIA GATEWAY
                detail_proxy_url = get_proxy_url(real_link)
                
                print(f"      ---> Opening Detail for: {company_name}")
                
                driver.execute_script("window.open(arguments[0]);", detail_proxy_url)
                driver.switch_to.window(driver.window_handles[-1])
                
                # Wait for detail page load
                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                print(f"      ---> Detail Page Loaded. Starting data retrieval.")
                
                soup = BeautifulSoup(driver.page_source, "html.parser")
                
                # --- Extraction ---
                mobile = ''; phone = ''; website = ''; location = ''; product_type = ''; 

                # Mobile extraction is often the first to fail on structural changes
                try:
                    m = soup.find("a", id=lambda x: x and "lblMobile" in x)
                    mobile = m.text.strip() if m else ''
                except: pass

                # ... (rest of extraction logic for phone, website, location, etc.) ...
                
                role = "Not Described"
                full_text = soup.get_text(" ", strip=True).lower()
                for k in role_keywords:
                    if k in full_text: role = k.capitalize(); break
                
                # Append data (success)
                data.append({
                    'Company Name': company_name, 'Website URL': website, 'Product Types': product_type,
                    'Mobile Number': mobile, 'Phone Number': phone, 'Location': location,
                    'Role': role, 'Contact Supplier URL': real_link
                })
                
                print(f"      ---> SUCCESS: Data for {company_name} appended.")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as e:
                # --- CRITICAL DEBUG CHANGE: PRINT THE ERROR ---
                print(f"\n   ❌ FATAL CARD ERROR on Card {i+1} ({company_name if 'company_name' in locals() else 'Unknown'}): {type(e).__name__} - {e}\n")
                
                # Clean up if tab is open
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue # move to next card

    except Exception as e:
        print(f"⚠️ Page Load Error: {e}")

# --- FINAL SAVE & CLEANUP ---
if data:
    with open("yellowpages_bolts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("✅ CSV Saved: yellowpages_bolts.csv")
else:
    print("❌ No data collected. Please examine the debug output and screenshots.")

driver.quit()
