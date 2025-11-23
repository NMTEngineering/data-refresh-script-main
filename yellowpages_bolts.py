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
from bs4 import BeautifulSoup
import time
import csv
import os

# ================================
# 🔐 Proxy / ScraperAPI Configuration
# ================================
proxy = os.getenv("PROXY_STRING", None)

# ================================
# 🧭 Setup Chrome with Proxy
# ================================
options = Options()
options.add_argument("--headless")  # Comment out if debugging locally
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

if proxy:
    print(f"🛡 Using proxy: {proxy}")
    options.add_argument(f"--proxy-server={proxy}")
else:
    print("⚠️ No proxy configured. Running direct connection.")

driver = webdriver.Chrome(options=options)

# ================================
# 🌐 Base URL
# ================================
base_url = "https://www.yellowpages-uae.com/uae/bolt?page={}"
data = []
role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

# ================================
# 🔁 Scraping Logic
# ================================
for page in range(1, 5):  # Scrape first 4 pages
    print(f"🔁 Scraping page {page}...")
    driver.get(base_url.format(page))

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
        )
        company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')

        for i in range(len(company_cards)):
            company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')  # Refresh elements
            try:
                link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
                driver.execute_script("arguments[0].scrollIntoView();", link_elem)
                link = link_elem.get_attribute("href")
                company_name = link_elem.text.strip()

                # Open detail page in new tab
                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[-1])
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                soup = BeautifulSoup(driver.page_source, "html.parser")

                # ====== Extract Fields ======
                # Mobile number
                mobile = ''
                try:
                    mobile = soup.find("a", id=lambda x: x and "lblMobile" in x)
                    mobile = mobile.text.strip() if mobile else ''
                except:
                    pass

                # Phone number
                phone = ''
                try:
                    phone = soup.find("a", id=lambda x: x and "lblPhone" in x)
                    phone = phone.text.strip() if phone else ''
                except:
                    pass

                # Website URL
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
                except Exception as e:
                    print(f"⚠️ Location extraction failed: {e}")

                # Product types
                product_type = ''
                try:
                    right_section = driver.find_element(By.CLASS_NAME, "flex.justify-between")
                    product_links = right_section.find_elements(By.XPATH, ".//a[@class='text-[#1e2f71]']")
                    product_type_list = []
                    for link in product_links:
                        if 'brands' in link.get_attribute('href').lower():
                            break
                        product_type_list.append(link.text.strip())
                    product_type = ", ".join([pt for pt in product_type_list if pt])
                except Exception as e:
                    print("❌ Product type not found:", e)

                # Contact URL
                contact_url = driver.current_url

                # Role detection
                role = "Not Described"
                combined_text = soup.get_text(" ", strip=True).lower()
                for keyword in role_keywords:
                    if keyword in combined_text:
                        role = keyword.capitalize()
                        break

                # Append Data
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

# ================================
# 💾 Save to CSV
# ================================
if data:
    with open("yellowpages_bolts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("✅ Done! Data saved to yellowpages_bolts.csv")
else:
    print("⚠️ No data scraped. Please check scraping logic.")

driver.quit()
