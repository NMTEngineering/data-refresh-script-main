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

# --- Setup Chrome Options ---
options = Options()
options.add_argument("--headless=new") # Mandatory for GitHub Actions
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-extensions')
options.add_argument('--disable-blink-features=AutomationControlled')

# NOTE: We removed 'options.binary_location'. 
# The system (and the YAML setup) will handle the path automatically.

print("Attempting to initialize ChromeDriver...")
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print(f"✅ ChromeDriver initialized successfully.")
except Exception as e:
    print(f"❌ FATAL ERROR: Failed to initialize ChromeDriver. Error: {e}")
    sys.exit(1)

# --- Scraping Logic ---
base_url = "https://www.yellowpages-uae.com/uae/hammer-unions?page={}"
data = []
role_keywords = ["manufacturer", "supplier", "distributor", "dealer", "stockist", "exporter", "trader", "retailer"]

# Scrape Page 1
for page in range(1, 2):
    print(f"\n🔁 Scraping page {page}...")
    driver.get(base_url.format(page))

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box'))
        )
        company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box')

        if not company_cards:
            print(f"⚠️ Found 0 company cards. Skipping.")
            continue

        for i in range(len(company_cards)):
            company_cards = driver.find_elements(By.CSS_SELECTOR, 'div.box') # Refresh elements
            try:
                print(f"  --> Scraping Company {i+1}...")
                link_elem = company_cards[i].find_element(By.TAG_NAME, "a")
                
                # Scroll and Open
                driver.execute_script("arguments[0].scrollIntoView();", link_elem)
                link = link_elem.get_attribute("href")
                company_name = link_elem.text.strip()

                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[-1])
                
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # Data Extraction
                mobile, phone, website, location, product_type = '', '', '', '', ''

                try:
                    m_elem = soup.find("a", id=lambda x: x and "lblMobile" in x)
                    mobile = m_elem.text.strip() if m_elem else ''
                except: pass

                try:
                    p_elem = soup.find("a", id=lambda x: x and "lblPhone" in x)
                    phone = p_elem.text.strip() if p_elem else ''
                except: pass

                try:
                    w_btn = soup.find("button", {"data-url": True})
                    if w_btn and w_btn.text.strip().lower() == "website":
                         website = w_btn['data-url']
                except: pass

                try:
                    info_div = soup.find("div", class_="grid grid-cols-2")
                    if info_div:
                        for p in info_div.find_all("p"):
                            if "City :" in p.text:
                                location = p.find_all("span")[1].text.strip() + ", UAE"
                                break
                except: pass

                try:
                    right_section = driver.find_element(By.CLASS_NAME, "flex.justify-between")
                    p_links = right_section.find_elements(By.XPATH, ".//a[@class='text-[#1e2f71]']")
                    product_type = ", ".join([l.text.strip() for l in p_links if l.text.strip()])
                except: pass

                # Role Detection
                role = "Not Described"
                full_text = soup.get_text(" ", strip=True).lower()
                for kw in role_keywords:
                    if kw in full_text:
                        role = kw.capitalize()
                        break

                data.append({
                    'Company Name': company_name,
                    'Website URL': website,
                    'Product Types': product_type,
                    'Mobile Number': mobile,
                    'Phone Number': phone,
                    'Location': location,
                    'Role': role,
                    'Contact Supplier URL': driver.current_url
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)

            except Exception as e:
                print(f"❌ Error on company {i+1}: {e}")
                if len(driver.window_handles) > 1:
                     driver.close()
                     driver.switch_to.window(driver.window_handles[0])
                continue

    except Exception as e:
        print(f"⚠️ Page load error: {e}")

# --- Save CSV ---
if data:
    try:
        with open("yellowpages_hammer_unions.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print("\n✅ Data saved to yellowpages_hammer_unions.csv")
    except Exception as e:
        print(f"\n❌ CSV Write Error: {e}")
else:
    print("\n⚠️ No data scraped.")

driver.quit()
