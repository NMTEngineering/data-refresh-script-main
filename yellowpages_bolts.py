# working but failing at Website URL	Product Types	Mobile Number	Phone Number	Location

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
# import os 

# # --- CONFIGURATION ---
# SCRAPER_API_KEY = "4e0f35d8236f741f56d86ac31c941f95"

# def get_proxy_url(target_url):
#     """Wraps the target URL in the ScraperAPI Gateway format"""
#     encoded_url = urllib.parse.quote(target_url)
#     return f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={encoded_url}&render=true"

# # --- SETUP CHROME ---
# options = Options()
# options.add_argument("--headless=new") 
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--window-size=1920,1080")
# options.add_argument('--disable-blink-features=AutomationControlled')

# print("🚀 Initializing Chrome Driver...")
# try:
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)
#     driver.set_page_load_timeout(90)
#     print("✅ Driver initialized.")
# except Exception as e:
#     print(f"❌ Driver Init Failed: {e}")
#     sys.exit(1)

# # --- SCRAPING LOGIC ---
# base_url = "https://www.yellowpages-uae.com/uae/bolt?page={}"
# data = []
# role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

# for page in range(1, 3):  # Running 2 pages for quick debug
#     print(f"\n🔁 Scraping page {page}...")
    
#     target_url = base_url.format(page)
#     proxy_url = get_proxy_url(target_url)
    
#     try:
#         driver.get(proxy_url)
        
#         # We know this block succeeds now
#         WebDriverWait(driver, 60).until(
#             EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
#         )
#         company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
        
#         if not company_cards:
#             print("⚠️ No cards found.")
#             continue

#         print(f"   ✅ Found {len(company_cards)} companies. Starting extraction...")

#         for i in range(len(company_cards)):
#             try:
#                 # --- NEW DEBUG LOG ---
#                 print(f"      ---> Processing Card {i+1}...")
                
#                 # Refresh elements
#                 company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
#                 link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
                
#                 real_link = link_elem.get_attribute("href")
#                 company_name = link_elem.text.strip()
                
#                 # OPEN DETAIL PAGE VIA GATEWAY
#                 detail_proxy_url = get_proxy_url(real_link)
                
#                 print(f"      ---> Opening Detail for: {company_name}")
                
#                 driver.execute_script("window.open(arguments[0]);", detail_proxy_url)
#                 driver.switch_to.window(driver.window_handles[-1])
                
#                 # Wait for detail page load
#                 WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
#                 print(f"      ---> Detail Page Loaded. Starting data retrieval.")
                
#                 soup = BeautifulSoup(driver.page_source, "html.parser")
                
#                 # --- Extraction ---
#                 mobile = ''; phone = ''; website = ''; location = ''; product_type = ''; 

#                 # Mobile extraction is often the first to fail on structural changes
#                 try:
#                     m = soup.find("a", id=lambda x: x and "lblMobile" in x)
#                     mobile = m.text.strip() if m else ''
#                 except: pass

#                 # ... (rest of extraction logic for phone, website, location, etc.) ...
                
#                 role = "Not Described"
#                 full_text = soup.get_text(" ", strip=True).lower()
#                 for k in role_keywords:
#                     if k in full_text: role = k.capitalize(); break
                
#                 # Append data (success)
#                 data.append({
#                     'Company Name': company_name, 'Website URL': website, 'Product Types': product_type,
#                     'Mobile Number': mobile, 'Phone Number': phone, 'Location': location,
#                     'Role': role, 'Contact Supplier URL': real_link
#                 })
                
#                 print(f"      ---> SUCCESS: Data for {company_name} appended.")

#                 driver.close()
#                 driver.switch_to.window(driver.window_handles[0])
                
#             except Exception as e:
#                 # --- CRITICAL DEBUG CHANGE: PRINT THE ERROR ---
#                 print(f"\n   ❌ FATAL CARD ERROR on Card {i+1} ({company_name if 'company_name' in locals() else 'Unknown'}): {type(e).__name__} - {e}\n")
                
#                 # Clean up if tab is open
#                 if len(driver.window_handles) > 1:
#                     driver.close()
#                     driver.switch_to.window(driver.window_handles[0])
#                 continue # move to next card

#     except Exception as e:
#         print(f"⚠️ Page Load Error: {e}")

# # --- FINAL SAVE & CLEANUP ---
# if data:
#     with open("yellowpages_bolts.csv", "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=data[0].keys())
#         writer.writeheader()
#         writer.writerows(data)
#     print("✅ CSV Saved: yellowpages_bolts.csv")
# else:
#     print("❌ No data collected. Please examine the debug output and screenshots.")

# driver.quit()






from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException 
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
    # render=true ensures Javascript loads
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
        
        # Wait for card list to load
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
        )
        company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
        
        if not company_cards:
            print("⚠️ No cards found.")
            continue

        print(f"   ✅ Found {len(company_cards)} companies. Starting extraction...")

        for i in range(len(company_cards)):
            
            # Initialize detail variables before the inner try/except block
            company_name = 'Unknown'
            real_link = ''
            
            try:
                # --- NEW DEBUG LOG ---
                print(f"      ---> Processing Card {i+1}...")
                
                # Refresh elements
                company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
                link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
                
                real_link = link_elem.get_attribute("href")
                company_name = link_elem.text.strip().replace('\n', ' ').split('More Info')[0].strip() # Clean name 
                
                # OPEN DETAIL PAGE VIA GATEWAY
                detail_proxy_url = get_proxy_url(real_link)
                
                print(f"      ---> Opening Detail for: {company_name}")
                
                # Open in new tab
                driver.execute_script("window.open(arguments[0]);", detail_proxy_url)
                driver.switch_to.window(driver.window_handles[-1])
                
                # Wait for detail page load
                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                print(f"      ---> Detail Page Loaded. Starting data retrieval.")
                
                soup = BeautifulSoup(driver.page_source, "html.parser")
                
                # --- Extraction ---
                mobile = ''; phone = ''; website = ''; location = ''; product_type = ''; role = "Not Described"

                # 1. Mobile Number Extraction
                try:
                    m = soup.find("a", id=lambda x: x and "lblMobile" in x)
                    mobile = m.text.strip() if m else ''
                except Exception as e:
                    print(f"      🚨 Mobile Error: {e}")
                    
                # 2. Phone Number Extraction
                try:
                    p = soup.find("a", id=lambda x: x and "lblPhone" in x)
                    phone = p.text.strip() if p else ''
                except Exception as e:
                    print(f"      🚨 Phone Error: {e}")

                # 3. Website URL Extraction
                try:
                    w = soup.find("button", attrs={"data-url": True})
                    if w and "website" in w.text.lower(): 
                        website = w['data-url']
                except Exception as e:
                    print(f"      🚨 Website Error: {e}")

                # 4. Location Extraction
                try:
                    # Look for the grid that contains location data
                    info = soup.find("div", class_="grid grid-cols-2")
                    if info:
                        for p in info.find_all("p"):
                            if "City :" in p.text:
                                location = p.find_all("span")[1].text.strip() + ", UAE"
                except Exception as e:
                    print(f"      🚨 Location Error: {e}")

                # 5. Product Type Extraction (This relies on Selenium finding dynamic links)
                try:
                    # Use CSS selector to find the relevant container
                    rs = driver.find_element(By.CSS_SELECTOR, ".flex.justify-between")
                    
                    # Find product links within that container
                    # This XPath targets <a> tags with the specific text color class
                    pls = rs.find_elements(By.XPATH, ".//a[contains(@class, 'text-[#1e2f71]')]")
                    
                    # Filter out links that are not product related (like 'brands')
                    p_list = [pl.text.strip() for pl in pls if 'brands' not in pl.get_attribute('href').lower()]
                    product_type = ", ".join(p_list)
                except Exception as e:
                    # If this fails, try falling back to BeautifulSoup (less reliable for dynamic content)
                    try:
                        product_div = soup.find('div', class_='flex justify-between')
                        p_list = [a.text.strip() for a in product_div.find_all('a') if 'brands' not in a.get('href', '').lower()]
                        product_type = ", ".join(p_list)
                    except Exception as fallback_e:
                        print(f"      🚨 Product Type Error (Selenium/BS4): {e} / Fallback: {fallback_e}")
                        pass
                
                # 6. Role Extraction
                full_text = soup.get_text(" ", strip=True).lower()
                for k in role_keywords:
                    if k in full_text: 
                        role = k.capitalize()
                        break
                
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
                print(f"\n   ❌ FATAL CARD ERROR on Card {i+1} ({company_name}): {type(e).__name__} - {e}\n")
                
                # Clean up if tab is open
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue # move to next card

    except TimeoutException:
        print("\n❌ TIMEOUT: Could not find listing cards within 60 seconds. Moving to next page.")
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
    print("❌ No data collected. Please examine the debug output for '🚨' errors.")

driver.quit()
