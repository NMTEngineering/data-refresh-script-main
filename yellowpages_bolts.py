# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager # Make sure to install this
# from bs4 import BeautifulSoup
# import time
# import csv
# import sys

# # --- Setup Chrome Options for GitHub Actions ---
# options = Options()
# # 1. Headless is MANDATORY in GitHub Actions
# options.add_argument("--headless=new") 
# # 2. Fixes "DevToolsActivePort file doesn't exist" in containers
# options.add_argument("--no-sandbox")
# # 3. CRITICAL: Prevents crashes due to limited shared memory in Docker/Linux
# options.add_argument("--disable-dev-shm-usage")
# # 4. Standard settings
# options.add_argument("--disable-gpu")
# options.add_argument("--window-size=1920,1080")

# # 5. ANTI-BOT MEASURES (Crucial for Yellowpages)
# # Spoof a real User-Agent so they don't see "HeadlessChrome"
# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# options.add_argument(f'user-agent={user_agent}')
# # Disable automation flags
# options.add_argument('--disable-blink-features=AutomationControlled')
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)

# print("Initializing Chrome Driver...")
# try:
#     # Use ChromeDriverManager to automatically install the driver matching the container's Chrome
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)
    
#     # 6. Advanced Stealth: Remove 'navigator.webdriver' property
#     driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#         "source": """
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined
#             })
#         """
#     })
#     print("✅ Driver initialized successfully.")
# except Exception as e:
#     print(f"❌ Failed to initialize driver: {e}")
#     sys.exit(1)

# # --- Rest of your scraping logic below ---
# driver.get("https://www.yellowpages-uae.com/uae/bolt?page=1")
# # ... continue with your existing loop ...

# soup = BeautifulSoup(driver.page_source, "html.parser")

# base_url = "https://www.yellowpages-uae.com/uae/bolt?page={}"
# data = []

# role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

# for page in range(1, 5):  # Update range for more pages
#     print(f"🔁 Scraping page {page}...")
#     driver.get(base_url.format(page))

#     try:
#         WebDriverWait(driver, 15).until(
#             EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
#         )
#         company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')

#         for i in range(len(company_cards)):
#             # Re-fetch elements to avoid stale reference
#             company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
#             try:
#                 link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
#                 driver.execute_script("arguments[0].scrollIntoView();", link_elem)
#                 link = link_elem.get_attribute("href")
#                 company_name = link_elem.text.strip()

#                 # Open detail page in new tab
#                 driver.execute_script("window.open(arguments[0]);", link)
#                 driver.switch_to.window(driver.window_handles[-1])
#                 WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.TAG_NAME, "body"))
#                 )

#                 soup = BeautifulSoup(driver.page_source, "html.parser")
#                 text = soup.get_text(separator=" ", strip=True).lower()

#                 # mobile number
#                 try:
#                     mobile = soup.find("a", id=lambda x: x and "lblMobile" in x)
#                     mobile = mobile.text.strip() if mobile else ''
#                 except:
#                     mobile = ''

#                 # phone number
#                 try:
#                     phone = soup.find("a", id=lambda x: x and "lblPhone" in x)
#                     phone = phone.text.strip() if phone else ''
#                 except:
#                     phone = ''

#                 # Website URL
#                 try:
#                     website_btn = soup.find("button", text="Website")
#                     website = website_btn['data-url'] if website_btn else ''
#                     if "undefined" in website:
#                         website = website_btn.get("title", "")
#                 except:
#                     website = ''

#                 try:
#                     location = ""
#                     info_container = soup.find("div", class_="grid grid-cols-2")
#                     if info_container:
#                         for p in info_container.find_all("p"):
#                             spans = p.find_all("span")
#                             if len(spans) == 2 and "City :" in spans[0].text:
#                                 city = spans[1].text.strip()
#                                 location = city + ", UAE"
#                                 break
#                 except Exception as e:
#                     print(f"⚠️ Location extraction failed: {e}")
#                     location = ""

#                 try:
#                     # Find the entire right-side container
#                     right_section = driver.find_element(By.CLASS_NAME, "flex.justify-between")

#                     # Extract all <a> tags inside it
#                     product_links = right_section.find_elements(By.XPATH, ".//a[@class='text-[#1e2f71]']")

#                     # Filter out brands by looking for those BEFORE the span with "Brands :"
#                     product_type = []
#                     for link in product_links:
#                         if 'brands' in link.get_attribute('href').lower():
#                             break  # stop when we hit the brands section
#                         product_type.append(link.text.strip())

#                     product_type = ", ".join([pt for pt in product_type if pt])
#                 except Exception as e:
#                     print("❌ Product type not found:", e)
#                     product_type = ""

#                 # Contact URL (from current page)
#                 contact_url = driver.current_url

#                 # Detect role
#                 role = "Not Described"
#                 combined_text = soup.get_text(" ", strip=True).lower()
#                 for keyword in role_keywords:
#                     if keyword in combined_text:
#                         role = keyword.capitalize()
#                         break

#                 # Append data
#                 data.append({
#                     'Company Name': company_name,
#                     'Website URL': website,
#                     'Product Types': product_type,
#                     'Mobile Number': mobile,
#                     'Phone Number': phone,
#                     'Location': location,
#                     'Role': role,
#                     'Contact Supplier URL': contact_url
#                 })

#                 driver.close()
#                 driver.switch_to.window(driver.window_handles[0])
#                 time.sleep(1)

#             except Exception as e:
#                 print(f"❌ Error scraping company: {e}")
#                 continue

#     except Exception as e:
#         print(f"⚠️ No company cards found on page {page}: {e}")
#         continue

# # Save to CSV
# if data:
#     with open("yellowpages_bolts.csv", "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=data[0].keys())
#         writer.writeheader()
#         writer.writerows(data)
#     print("✅ Done! Data saved to yellowpages_bolts.csv")
# else:
#     print("⚠️ No data scraped. Please check scraping logic.")

# driver.quit()




#without hardcoded url
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# import time
# import csv
# import sys
# import os

# # --- SETUP CHROME ---
# options = Options()
# options.add_argument("--headless=new") 
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--window-size=1920,1080")
# options.add_argument('--disable-blink-features=AutomationControlled')

# # --- 1. PROXY CONFIGURATION (CRITICAL) ---
# proxy_server = os.environ.get("PROXY_STRING") 
# if proxy_server:
#     print(f"🌍 Using Proxy: {proxy_server}")
#     options.add_argument(f'--proxy-server={proxy_server}')
# else:
#     print("⚠️ WARNING: No Proxy found. Request might be blocked.")

# print("Initializing Chrome Driver...")
# try:
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)
#     print("✅ Driver initialized.")
# except Exception as e:
#     print(f"❌ Driver Init Failed: {e}")
#     sys.exit(1)

# # --- 2. SCRAPING LOGIC ---
# base_url = "https://www.yellowpages-uae.com/uae/bolt?page={}"
# data = []
# role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

# for page in range(1, 5): 
#     print(f"\n🔁 Scraping page {page}...")
#     try:
#         driver.get(base_url.format(page))
#         time.sleep(2) # Polite delay

#         if "Access Denied" in driver.title:
#             print("❌ Blocked by Website.")
#             continue

#         WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box')))
#         company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
        
#         if not company_cards:
#             print("⚠️ No cards found.")
#             continue
            
#         print(f"   ✅ Found {len(company_cards)} companies.")

#         for i in range(len(company_cards)):
#             try:
#                 # Refresh elements
#                 company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
#                 link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
                
#                 driver.execute_script("arguments[0].scrollIntoView();", link_elem)
#                 link = link_elem.get_attribute("href")
#                 company_name = link_elem.text.strip()
                
#                 driver.execute_script("window.open(arguments[0]);", link)
#                 driver.switch_to.window(driver.window_handles[-1])
#                 WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
#                 soup = BeautifulSoup(driver.page_source, "html.parser")

#                 # Extraction
#                 mobile = ''
#                 try:
#                     m = soup.find("a", id=lambda x: x and "lblMobile" in x)
#                     mobile = m.text.strip() if m else ''
#                 except: pass

#                 phone = ''
#                 try:
#                     p = soup.find("a", id=lambda x: x and "lblPhone" in x)
#                     phone = p.text.strip() if p else ''
#                 except: pass

#                 website = ''
#                 try:
#                     w = soup.find("button", attrs={"data-url": True})
#                     if w and "website" in w.text.lower(): website = w['data-url']
#                 except: pass

#                 location = ""
#                 try:
#                     info = soup.find("div", class_="grid grid-cols-2")
#                     if info:
#                         for p in info.find_all("p"):
#                             if "City :" in p.text:
#                                 location = p.find_all("span")[1].text.strip() + ", UAE"
#                 except: pass

#                 product_type = ""
#                 try:
#                     rs = driver.find_element(By.CLASS_NAME, "flex.justify-between")
#                     pls = rs.find_elements(By.XPATH, ".//a[@class='text-[#1e2f71]']")
#                     p_list = [pl.text.strip() for pl in pls if 'brands' not in pl.get_attribute('href').lower()]
#                     product_type = ", ".join(p_list)
#                 except: pass

#                 contact_url = driver.current_url
#                 role = "Not Described"
#                 full_text = soup.get_text(" ", strip=True).lower()
#                 for k in role_keywords:
#                     if k in full_text: role = k.capitalize(); break

#                 data.append({
#                     'Company Name': company_name, 'Website URL': website, 'Product Types': product_type,
#                     'Mobile Number': mobile, 'Phone Number': phone, 'Location': location,
#                     'Role': role, 'Contact Supplier URL': contact_url
#                 })

#                 driver.close()
#                 driver.switch_to.window(driver.window_handles[0])
#             except Exception:
#                 if len(driver.window_handles) > 1:
#                     driver.close()
#                     driver.switch_to.window(driver.window_handles[0])
#                 continue

#     except Exception as e:
#         print(f"⚠️ Page error: {e}")

# # Save CSV
# if data:
#     with open("yellowpages_bolts.csv", "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=data[0].keys())
#         writer.writeheader()
#         writer.writerows(data)
#     print("✅ CSV Saved: yellowpages_bolts.csv")
# else:
#     print("❌ No data collected.")

# driver.quit()




# hard coded scraper api
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
# We use your API Key directly in the URL to avoid browser auth issues
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

# NOTE: We REMOVED the --proxy-server argument because we are using Gateway Mode
print("Initializing Chrome Driver...")
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

for page in range(1, 3):  # Reduced to 2 pages for testing speed
    print(f"\n🔁 Scraping page {page}...")
    
    # 1. CONSTRUCT PROXY URL
    target_url = base_url.format(page)
    proxy_url = get_proxy_url(target_url)
    
    print(f"   ⏳ Requesting via ScraperAPI (this takes 20-40s)...")
    
    try:
        driver.get(proxy_url)
        
        # Check if ScraperAPI gave us an error
        if "Request failed" in driver.page_source or "Access Denied" in driver.title:
            print("❌ ScraperAPI failed to retrieve this page.")
            continue

        # 2. INCREASED TIMEOUT (Crucial for Proxies)
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
        )
        company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
        
        if not company_cards:
            print("⚠️ No cards found (Possible layout change or empty page).")
            continue

        print(f"   ✅ Found {len(company_cards)} companies.")

        for i in range(len(company_cards)):
            try:
                # Refresh elements
                company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
                link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
                
                link = link_elem.get_attribute("href")
                company_name = link_elem.text.strip()
                
                # 3. OPEN DETAIL PAGE VIA PROXY
                # We must wrap the detail link in the proxy URL too!
                detail_proxy_url = get_proxy_url(link)
                
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

                contact_url = link # Store the real URL, not the proxy one
                role = "Not Described"
                full_text = soup.get_text(" ", strip=True).lower()
                for k in role_keywords:
                    if k in full_text: role = k.capitalize(); break

                print(f"   --> Extracted: {company_name}")

                data.append({
                    'Company Name': company_name, 'Website URL': website, 'Product Types': product_type,
                    'Mobile Number': mobile, 'Phone Number': phone, 'Location': location,
                    'Role': role, 'Contact Supplier URL': contact_url
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
