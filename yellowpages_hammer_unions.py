# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service
# # from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# import time
# import csv

# # Setup Chrome driver
# options = Options()
# options.add_argument("--headless")  # Optional
# options.add_argument("--no-sandbox")
# # options.add_argument("--disable-gpu")
# # options.add_argument("--window-size=1920,1080")

# driver = webdriver.Chrome(options=options)

# # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# driver.get("https://www.yellowpages-uae.com/uae/hammer-unions?page=1")
# soup = BeautifulSoup(driver.page_source, "html.parser")

# base_url = "https://www.yellowpages-uae.com/uae/hammer-unions?page={}"
# data = []

# role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

# for page in range(1, 2):  # Update range for more pages
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
#     with open("yellowpages_hammer_unions.csv", "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=data[0].keys())
#         writer.writeheader()
#         writer.writerows(data)
#     print("✅ Done! Data saved to yellowpages_hammer_unions.csv")
# else:
#     print("⚠️ No data scraped. Please check scraping logic.")


# driver.quit()




# 1. Install necessary system packages for Google Chrome and dependencies
!wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
!dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -y --fix-broken # Fix broken dependencies
!apt-get update -qq
!apt-get install -y fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcairo2 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxss1 libxtst6 lsb-release xdg-utils libvulkan1
!dpkg -i google-chrome-stable_current_amd64.deb # Try installing again after dependencies

# 2. Install Python packages
!pip install selenium webdriver-manager beautifulsoup4

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
import sys # For sys.exit if driver fails to initialize

# Setup Chrome driver for Colab
options = Options()

# Explicitly set binary location to the newly installed Google Chrome Stable
options.binary_location = '/usr/bin/google-chrome'

options.add_argument("--headless=new") # Use 'new' for modern headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# The following options can help with stability in headless environments
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-extensions')
options.add_argument('--disable-browser-side-navigation')
options.add_argument('--disable-setuid-sandbox')
options.add_argument('--disable-blink-features=AutomationControlled') # Evade detection

print("Attempting to initialize ChromeDriver...")
try:
    # Use ChromeDriverManager to automatically get the correct driver version for the installed Chrome browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print(f"✅ ChromeDriver initialized successfully. Chrome version: {driver.capabilities['browserVersion']}")
    print(f"✅ ChromeDriver version: {driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]}")
except Exception as e:
    print(f"❌ FATAL ERROR: Failed to initialize ChromeDriver. Error: {e}")
    sys.exit(1) # Exit the script if driver initialization fails

# Initial setup - open the first page once
driver.get("https://www.yellowpages-uae.com/uae/hammer-unions?page=1")
soup = BeautifulSoup(driver.page_source, "html.parser")

base_url = "https://www.yellowpages-uae.com/uae/hammer-unions?page={}"
data = []

role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

# Starting loop from page 1 up to 2 (scrapes only page 1, change range for more pages)
for page in range(1, 2):
    print(f"\n🔁 Scraping page {page}...")
    driver.get(base_url.format(page))

    try:
        # Wait for the company cards to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
        )
        company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')

        if not company_cards:
            print(f"⚠️ Found 0 company cards after waiting on page {page}. Skipping.")
            continue

        for i in range(len(company_cards)):
            # Re-fetch elements to avoid stale reference
            company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')
            try:
                print(f"  --> Scraping Company {i+1} of {len(company_cards)}...")
                link_elem = company_cards[i].find_element(By.TAG_NAME, "a")

                # Scroll element into view
                driver.execute_script("arguments[0].scrollIntoView();", link_elem)

                link = link_elem.get_attribute("href")
                company_name = link_elem.text.strip()

                # Open detail page in new tab
                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[-1])
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                soup = BeautifulSoup(driver.page_source, "html.parser")

                # --- Contact Details Extraction (using BeautifulSoup) ---
                mobile = ''
                try:
                    mobile_elem = soup.find("a", id=lambda x: x and "lblMobile" in x)
                    mobile = mobile_elem.text.strip() if mobile_elem else ''
                except:
                    pass

                phone = ''
                try:
                    phone_elem = soup.find("a", id=lambda x: x and "lblPhone" in x)
                    phone = phone_elem.text.strip() if phone_elem else ''
                except:
                    pass

                website = ''
                try:
                    website_btn = soup.find("button", {"data-url": True})
                    if website_btn and website_btn.text.strip().lower() == "website":
                         website = website_btn['data-url']
                         if "undefined" in website or not website:
                            website = website_btn.get("title", "")
                except:
                    pass

                # --- Location Extraction ---
                location = ""
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
                    location = ""

                # --- Product Type Extraction ---
                product_type = ""
                try:
                    right_section = driver.find_element(By.CLASS_NAME, "flex.justify-between")
                    product_links = right_section.find_elements(By.XPATH, ".//a[@class='text-[#1e2f71]']")

                    products_list = []
                    for link_elem in product_links:
                         href = link_elem.get_attribute('href')
                         if href and 'brands' in href.lower():
                             break
                         products_list.append(link_elem.text.strip())

                    product_type = ", ".join([pt for pt in products_list if pt])
                except Exception as e:
                    product_type = ""

                # --- Role Detection ---
                contact_url = driver.current_url
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

                # Close the detail tab and switch back to the main tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)

            except Exception as e:
                print(f"❌ Error scraping company {i+1} on page {page}: {e}")
                # Clean up if the tab is still open
                if len(driver.window_handles) > 1:
                     driver.close()
                     driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)
                continue

    except Exception as e:
        print(f"⚠️ Failed to load company cards on page {page} within timeout: {e}")
        continue

# --- Save to CSV ---
if data:
    try:
        with open("yellowpages_hammer_unions.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print("\n✅ Done! Data saved to yellowpages_hammer_unions.csv")
    except Exception as e:
        print(f"\n❌ Failed to write CSV file: {e}")
else:
    print("\n⚠️ No data scraped. Please check scraping logic.")

# Clean up
driver.quit()
