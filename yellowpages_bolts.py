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
from bs4 import BeautifulSoup
import time
import csv
import urllib.parse
import sys

# --- CONFIGURATION (MANDATORY) ---
# REPLACE THIS WITH YOUR ACTUAL SCRAPERAPI KEY
SCRAPER_API_KEY = "4e0f35d8236f741f56d86ac31c941f95" 

def get_proxy_url(target_url):
    """Wraps the target URL in the ScraperAPI Gateway format for remote execution."""
    encoded_url = urllib.parse.quote(target_url)
    # render=true ensures Javascript loads
    return f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={encoded_url}&render=true"

# --- SETUP CHROME DRIVER ---
options = Options()
options.add_argument("--headless=new") # Use the new, more reliable headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-blink-features=AutomationControlled')

print("🚀 Initializing Chrome Driver...")
try:
    # Use ChromeDriverManager for dynamic driver management (needed for remote environments)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(90)
    print("✅ Driver initialized.")
except Exception as e:
    print(f"❌ Driver Init Failed: {e}")
    sys.exit(1)


# --- START SCRAPING ---
base_listing_url = "https://www.yellowpages-uae.com/uae/bolt?page={}"
data = []

role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

for page in range(1, 5): 
    print(f"\n🔁 Scraping page {page}...")
    
    # Use ScraperAPI proxy for the listing page load
    listing_url = base_listing_url.format(page)
    driver.get(get_proxy_url(listing_url))

    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
        )
        company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
        print(f"   ✅ Found {len(company_cards)} companies on page {page}.")

        for i in range(len(company_cards)):
            # Re-fetch elements to avoid stale reference
            company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
            
            # Initialize with default values
            link = ''; company_name = 'Unknown'

            try:
                print(f"      ---> Processing Card {i+1}...")
                
                link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
                driver.execute_script("arguments[0].scrollIntoView();", link_elem)
                link = link_elem.get_attribute("href")
                company_name = link_elem.text.strip().split('\n')[0].strip()

                # Open detail page using ScraperAPI proxy
                detail_proxy_url = get_proxy_url(link)
                driver.execute_script("window.open(arguments[0]);", detail_proxy_url)
                driver.switch_to.window(driver.window_handles[-1])
                
                print(f"      ---> Opening Detail for: {company_name}")
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                soup = BeautifulSoup(driver.page_source, "html.parser")

                # Data extraction variables
                mobile = ''; phone = ''; website = ''; location = ''; product_type = ''

                # mobile number (BS4 - reliable)
                try:
                    mobile = soup.find("a", id=lambda x: x and "lblMobile" in x)
                    mobile = mobile.text.strip() if mobile else ''
                except:
                    mobile = ''

                # phone number (BS4 - reliable)
                try:
                    phone = soup.find("a", id=lambda x: x and "lblPhone" in x)
                    phone = phone.text.strip() if phone else ''
                except:
                    phone = ''

                # Website URL (BS4 - reliable)
                try:
                    website_btn = soup.find("button", text="Website")
                    website = website_btn['data-url'] if website_btn and 'data-url' in website_btn.attrs else ''
                    if "undefined" in website:
                        website = website_btn.get("title", "") if website_btn else ''
                except:
                    website = ''

                # Location (BS4 - reliable)
                try:
                    info_container = soup.find("div", class_="grid grid-cols-2")
                    if info_container:
                        for p in info_container.find_all("p"):
                            spans = p.find_all("span")
                            if len(spans) == 2 and "City :" in spans[0].text:
                                city = spans[1].text.strip()
                                location = city + ", UAE"
                                break
                except Exception as e:
                    print(f"      ⚠️ Location extraction failed: {e}")
                    location = ""

                # ----------------------------------------------------------------------
                # CRITICAL BUG FIX: Replaced the brittle CSS selector with a resilient XPath
                # ----------------------------------------------------------------------
                try:
                    # Find the entire right-side container using a descriptive XPath
                    # This searches for a div that contains the text "Product Types"
                    product_container = driver.find_element(By.XPATH, "//div[contains(., 'Product Types')]")

                    # Extract all <a> tags inside it that have the text color class
                    product_links = product_container.find_elements(By.XPATH, ".//a[contains(@class, 'text-[#1e2f71]')]")

                    # Filter out brands by looking for those BEFORE the span with "Brands :"
                    product_type_list = []
                    for plink in product_links:
                        # Check the actual text of the link
                        if 'brands' in plink.get_attribute('href').lower():
                            break  # stop when we hit the brands section
                        product_type_list.append(plink.text.strip())

                    product_type = ", ".join([pt for pt in product_type_list if pt])
                    
                    if not product_type:
                        print("      ⚠️ Found product section container, but extracted list was empty.")
                except Exception as e:
                    print(f"      ❌ Product type not found (using resilient XPath): {e}")
                    product_type = ""
                # ----------------------------------------------------------------------
                
                # Contact URL (from current page)
                contact_url = driver.current_url

                # Detect role
                role = "Not Described"
                combined_text = soup.get_text(" ", strip=True).lower()
                for keyword in role_keywords:
                    if keyword in combined_text:
                        role = keyword.capitalize()
                        break

                # Append data
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
                
                print(f"      ---> SUCCESS: Data for {company_name} appended. Products: '{product_type}'")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)

            except Exception as e:
                print(f"      ❌ Error scraping company {company_name}: {type(e).__name__} - {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

    except Exception as e:
        print(f"⚠️ Page {page} failed to load or find cards: {e}")
        continue

# Save to CSV
if data:
    output_path = "yellowpages_bolts.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"\n✅ Done! Data saved to {output_path}. Total records: {len(data)}")
else:
    print("\n⚠️ No data scraped. Please check logs for errors.")

driver.quit()
