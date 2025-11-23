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
from webdriver_manager.chrome import ChromeDriverManager # <-- UNCOMMENTED/ADDED for remote setup
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


# Setup Chrome driver (Updated for remote/headless environments)
options = Options()
options.add_argument("--headless=new") 
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage") 
options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-blink-features=AutomationControlled') 

print("🚀 Initializing Chrome Driver...")
try:
    # Using ChromeDriverManager to handle driver binary (REQUIRED for GitHub Actions)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(90)
    print("✅ Driver initialized.")
except Exception as e:
    print(f"❌ Driver Init Failed: {e}")
    sys.exit(1)


# MODIFICATION 1: Proxy the initial URL
INITIAL_URL = "https://www.yellowpages-uae.com/uae/search?q=bolt&page=1"
driver.get(get_proxy_url(INITIAL_URL))
# No need to parse soup here, as we immediately start the loop

# Update base_url to reflect the new search query structure
base_url = "https://www.yellowpages-uae.com/uae/search?q=bolt&page={}"
data = []

role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

for page in range(1, 2): # Update range for more pages
    print(f"🔁 Scraping page {page}...")
    
    # MODIFICATION 2: Proxy the listing page URL
    driver.get(get_proxy_url(base_url.format(page)))

    try:
        # Wait for the listing boxes to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
        )
        
        # --- CRITICAL FIX: Extract all necessary link data BEFORE iterating ---
        company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
        company_links = []
        for card in company_cards:
            try:
                link_elem = card.find_element(By.TAG_NAME, "a")
                # Store the name and the href link in a list of tuples
                company_links.append({
                    'name': link_elem.text.strip(),
                    'link': link_elem.get_attribute("href")
                })
            except Exception as e:
                print(f"⚠️ Could not extract link/name from a card on page {page}: {e}")
                continue # Skip to the next card
        
        print(f"   ✅ Found {len(company_links)} companies to process on page {page}.")
        # --- END CRITICAL FIX ---

        # Now, iterate over the stable 'company_links' list
        for company_info in company_links:
            link = company_info['link']
            company_name = company_info['name']
            
            # Use the original Yellow Pages link for the proxy call
            detail_proxy_url = get_proxy_url(link)
            
            try:
                # Open the new window for the detail page
                driver.execute_script("window.open(arguments[0]);", detail_proxy_url)
                driver.switch_to.window(driver.window_handles[-1])
                
                print(f"      ---> Opening Detail for: {company_name}")
                
                # Check for the 404 page content explicitly to fail fast
                page_source = driver.page_source
                if "404 Not Found" in page_source or "page you are looking for has changed" in page_source:
                    raise Exception("Detail page returned 404 Not Found or changed.")

                # Wait for the company name header on the detail page to confirm successful load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-3xl.font-semibold"))
                )

                soup = BeautifulSoup(driver.page_source, "html.parser")
                text = soup.get_text(separator=" ", strip=True).lower()

                # mobile number
                try:
                    mobile = soup.find("a", id=lambda x: x and "lblMobile" in x)
                    mobile = mobile.text.strip() if mobile else ''
                except:
                    mobile = ''

                # phone number
                try:
                    phone = soup.find("a", id=lambda x: x and "lblPhone" in x)
                    phone = phone.text.strip() if phone else ''
                except:
                    phone = ''

                # Website URL (Updated selector to be more robust)
                try:
                    # Find the button that is likely hidden but holds the URL
                    website_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Website')]")
                    website = website_btn.get_attribute("data-url")
                    if not website or "undefined" in website:
                        # Fallback to checking the title attribute if data-url is missing/broken
                        website = website_btn.get_attribute("title")
                    
                    # If we still haven't found a decent URL, check the link wrapper
                    if not website or "undefined" in website:
                         # Attempt to find the anchor tag in the same structure if available
                        website_link = soup.find('a', {'href': lambda href: href and 'website_redirection' in href})
                        website = website_link['href'] if website_link else ''
                except:
                    website = ''

                try:
                    location = ""
                    # The location structure seems stable in the new layout
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
                    location = ""

                try:
                    # Find the entire right-side container for product links
                    right_section = driver.find_element(By.CLASS_NAME, "flex.justify-between")

                    # Extract all <a> tags inside it
                    product_links = right_section.find_elements(By.XPATH, ".//a[@class='text-[#1e2f71]']")

                    # Filter out brands by looking for those BEFORE the span with "Brands :"
                    product_type_list = []
                    for plink in product_links:
                        # Ensure we don't accidentally stop at the "Brands" header text link
                        if 'brands' in plink.get_attribute('href').lower() or plink.text.strip().lower() == 'brands':
                            break  # stop when we hit the brands section
                        product_type_list.append(plink.text.strip())

                    product_type = ", ".join([pt for pt in product_type_list if pt])
                except Exception as e:
                    print(f"❌ Product type not found: {e}")
                    product_type = ""

                # Contact URL (from current page - which is the successful proxy URL)
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

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)

            except Exception as e:
                print(f"❌ Error scraping company '{company_name}': {e}")
                
                # If an error occurs, still record the company name and the link that failed
                data.append({
                    'Company Name': company_name,
                    'Website URL': '',
                    'Product Types': '',
                    'Mobile Number': '',
                    'Phone Number': '',
                    'Location': '',
                    'Role': 'Error/404',
                    'Contact Supplier URL': link # Record the original Yellow Pages link that failed
                })

                # Close the new window if an error occurred during scraping detail page
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                
                continue

    except Exception as e:
        print(f"⚠️ No company cards found on page {page}: {e}")
        continue

# Save to CSV
if data:
    with open("yellowpages_bolts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("✅ Done! Data saved to yellowpages_bolts.csv")
else:
    print("⚠️ No data scraped. Please check scraping logic.")

driver.quit()
