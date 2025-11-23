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






"""
YellowPages UAE Scraper - Bolts Category (with ScraperAPI HTML rendering)
------------------------------------------------------------------------
✅ Works with ScraperAPI render=true to bypass dynamic loading issues.
✅ Uses API key from GitHub secret (PROXY_STRING).
✅ Exports yellowpages_bolts.csv
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import csv
import os
import urllib.parse

# ==========================================================
# 🔐 ScraperAPI Setup (use from PROXY_STRING or extract key)
# ==========================================================
proxy_env = os.getenv("PROXY_STRING", "")
# Extract API key if full proxy string was provided
# e.g., http://scraperapi:KEY@proxy-server.scraperapi.com:8001
SCRAPERAPI_KEY = None
if "@" in proxy_env and ":" in proxy_env:
    try:
        SCRAPERAPI_KEY = proxy_env.split(":")[2].split("@")[0]
    except Exception:
        SCRAPERAPI_KEY = None

# Fallback: direct secret as raw key
if not SCRAPERAPI_KEY or len(SCRAPERAPI_KEY) < 10:
    SCRAPERAPI_KEY = proxy_env.strip()

print(f"🔑 Using ScraperAPI Key: {SCRAPERAPI_KEY[:6]}****")

# ==========================================================
# 🧭 Setup Chrome (no need for proxy here)
# ==========================================================
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

# ==========================================================
# 🌐 Helper function to load page via ScraperAPI
# ==========================================================
def get_scraperapi_url(target_url):
    encoded_url = urllib.parse.quote_plus(target_url)
    return f"https://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={encoded_url}&render=true"

# ==========================================================
# 🧩 Main scraping logic
# ==========================================================
base_url = "https://www.yellowpages-uae.com/uae/bolt?page={}"
data = []
role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

for page in range(1, 5):
    print(f"🔁 Scraping page {page}...")
    target_url = get_scraperapi_url(base_url.format(page))
    driver.get(target_url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
        )
        company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')

        if not company_cards:
            print(f"⚠️ No company cards detected on page {page}")
            continue

        for i in range(len(company_cards)):
            company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')  # Refresh each iteration
            try:
                link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
                driver.execute_script("arguments[0].scrollIntoView();", link_elem)
                link = link_elem.get_attribute("href")
                company_name = link_elem.text.strip()

                # Open detail page through ScraperAPI (rendered)
                detail_url = get_scraperapi_url(link)
                driver.execute_script("window.open(arguments[0]);", detail_url)
                driver.switch_to.window(driver.window_handles[-1])
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                soup = BeautifulSoup(driver.page_source, "html.parser")

                # ====== Extract Fields ======
                def safe_find_text(id_keyword):
                    try:
                        tag = soup.find("a", id=lambda x: x and id_keyword in x)
                        return tag.text.strip() if tag else ''
                    except:
                        return ''

                mobile = safe_find_text("lblMobile")
                phone = safe_find_text("lblPhone")

                # Website
                website = ''
                try:
                    website_btn = soup.find("button", text="Website")
                    website = website_btn['data-url'] if website_btn else ''
                    if "undefined" in website:
                        website = website_btn.get("title", "")
                except:
                    pass

                # Location
                location = ''
                try:
                    info_container = soup.find("div", class_="grid grid-cols-2")
                    if info_container:
                        for p in info_container.find_all("p"):
                            spans = p.find_all("span")
                            if len(spans) == 2 and "City :" in spans[0].text:
                                city = spans[1].text.strip()
                                location = city + ", UAE"
                                break
                except:
                    pass

                # Product Types
                product_type = ''
                try:
                    right_section = driver.find_element(By.CLASS_NAME, "flex.justify-between")
                    product_links = right_section.find_elements(By.XPATH, ".//a[@class='text-[#1e2f71]']")
                    pt_list = []
                    for link in product_links:
                        if 'brands' in link.get_attribute('href').lower():
                            break
                        pt_list.append(link.text.strip())
                    product_type = ", ".join(pt_list)
                except:
                    pass

                # Contact URL
                contact_url = link

                # Role detection
                role = "Not Described"
                combined_text = soup.get_text(" ", strip=True).lower()
                for keyword in role_keywords:
                    if keyword in combined_text:
                        role = keyword.capitalize()
                        break

                # Save record
                data.append({
                    'Company Name': company_name,
                    'Website URL': website,
                    'Product Types': product_type,
                    'Mobile Number': mobile,
                    'Phone Number': phone,
                    'Location': location,
                    'Role': role,
                    'Contact Supplier URL': contact_url
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)

            except Exception as e:
                print(f"❌ Error scraping company: {e}")
                continue

    except Exception as e:
        print(f"⚠️ No company cards found on page {page}: {e}")
        continue

# ==========================================================
# 💾 Save CSV
# ==========================================================
if data:
    with open("yellowpages_bolts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Done! Scraped {len(data)} records and saved to yellowpages_bolts.csv")
else:
    print("⚠️ No data scraped. Please check scraping logic or rendering.")

driver.quit()
