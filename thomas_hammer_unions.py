from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import re
import requests

# Chrome setup
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

company_data = []

for page in range(1, 2):
    print(f"\n🔁 Scraping page {page}...")
    paginated_url = f"https://www.thomasnet.com/suppliers/search?cov=NA&heading=97018968&searchsource=suppliers&searchterm=hammer+un&what=Hammer+Unions&pg={page}"
    driver.get(paginated_url)
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    cards = soup.select("div[data-sentry-component='SupplierNameLink'] h2")
    print(f"🔍 Found {len(cards)} companies")

    json_ld_script = soup.find("script", {"id": "json-ld", "type": "application/ld+json"})
    company_url_map = {}

    if json_ld_script:
        try:
            json_data = json.loads(json_ld_script.string)
            for item in json_data.get("itemListElement", []):
                company = item.get("item", {})
                name = company.get("name", "").strip()
                url = company.get("url", "").strip()
                if name and url:
                    company_url_map[name.lower()] = url
        except Exception as e:
            print("❌ Failed to parse JSON-LD:", e)

    for idx, card in enumerate(cards, start=1):
        try:
            name_tag = card.find(["a", "button"])
            if not name_tag:
                print(f"⚠️ No name tag in card #{idx}")
                continue

            company_name = name_tag.get_text(strip=True)
            company_key = company_name.lower()
            profile_link = company_url_map.get(company_key)

            if not profile_link:
                print(f"⚠️ No profile link for: {company_name}")
                continue

            contact_supplier_url = ""
            match = re.search(r"-(\d+)/profile", profile_link)
            if match:
                company_id = match.group(1)
                contact_supplier_url = f"https://www.thomasnet.com/suppliers/request?tgramsId={company_id}&heading=30212203"

            driver.get(profile_link)
            time.sleep(1)
            profile_soup = BeautifulSoup(driver.page_source, "html.parser")

# Define your HTML content as a string first
            html = '''<div role="tabpanel" aria-labelledby="companyProductsCategoriesTab">
            <div class="mar-t-3">
                <h4>Unions</h4>
                <div class="mar-t-3 mar-b-3">
                <ul class="section-list_twoColumnsUnorderedList__RG6CC">
                    <li><div class="pad-1 width-max"><a kind="dark" class="flex align-items-center gap-1 txt-smallest font-reg ">Unions: Hammer</a></div></li>
                    <li><div class="pad-1 width-max"><a kind="dark" class="flex align-items-center gap-1 txt-smallest font-reg ">Fittings: Pipe, Stainless Steel</a></div></li>
                    <li><div class="pad-1 width-max"><a kind="dark" class="flex align-items-center gap-1 txt-smallest font-reg ">Fittings: Carbon Steel</a></div></li>
                    <li><div class="pad-1 width-max"><a kind="dark" class="flex align-items-center gap-1 txt-smallest font-reg ">Fittings: Pipe, Aluminum</a></div></li>
                    <li><div class="pad-1 width-max"><a kind="dark" class="flex align-items-center gap-1 txt-smallest font-reg ">Fittings</a></div></li>
                    <li><div class="pad-1 width-max"><a kind="dark" class="flex align-items-center gap-1 txt-smallest font-reg ">Fittings: Alloy</a></div></li>
                    <li><div class="pad-1 width-max"><a kind="dark" class="flex align-items-center gap-1 txt-smallest font-reg ">Fittings: Alloy, 304 & 316</a></div></li>
                    <li><div class="pad-1 width-max"><a kind="dark" class="flex align-items-center gap-1 txt-smallest font-reg ">Fittings: Aluminum</a></div></li>
                    <li><div class="pad-1 width-max"><a kind="dark" class="flex align-items-center gap-1 txt-smallest font-reg ">Fittings: Brass</a></div></li>
                </ul>
                </div>
            </div>
            </div>'''

            hammer_unions_products = []
            # Now parse the HTML
            soup = BeautifulSoup(html, 'html.parser')

            hammer_unions_header = soup.find('h4', string=lambda text: text and 'Unions' in text)

            if not hammer_unions_header:
                print("Unions header not found")
            else:
                ul = hammer_unions_header.find_next('ul')
                hammer_unions_products = [a.get_text(strip=True) for a in ul.find_all('a')]
                print('\n'.join(hammer_unions_products))

            # Location & Role
            location, role = "", ""
            supplier_section = profile_soup.select_one("[data-sentry-component='SupplierDetails']")
            if supplier_section:
                info_blocks = supplier_section.find_all("div", class_="txt-smallest font-semi")
                for block in info_blocks:
                    text = block.get_text(strip=True).replace("*", "")
                    lower_text = text.lower()
                    if not location and re.match(r"^[A-Za-z .\-]+,\s?[A-Z]{2}(?:\s+\d{5})?$", text):
                        location = text
                    if not role:
                        if "manufacturer" in lower_text:
                            role = "Manufacturer"
                        elif "supplier" in lower_text:
                            role = "Supplier"

            if not location:
                fallback_location_tag = profile_soup.select_one("[data-sentry-component='SupplierLocations'] a")
                if fallback_location_tag:
                    fallback_text = fallback_location_tag.get_text(strip=True)
                    if re.match(r"^[A-Za-z .\-]+,\s?[A-Z]{2}(?:\s+\d{5})?$", fallback_text):
                        location = fallback_text

            # Website URL
            website = ""
            website_tag = profile_soup.find("div", class_="txt-label", string="Website")
            if website_tag:
                ul = website_tag.find_next_sibling("ul")
                if ul:
                    a = ul.find("a", href=True)
                    if a:
                        website = a["href"].strip()


            # Phone number
            phone = ""
            try:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'View Phone Number')]"))
                )
                btn.click()
                time.sleep(2)
                dlg = BeautifulSoup(driver.page_source, "html.parser")
                tel = dlg.select_one("dialog a[href^='tel:']")
                if tel:
                    phone = tel.text.strip()
            except:
                phone = ""

            # Annual Sales
            annual_sales = ""
            sales_label = profile_soup.find("div", class_="txt-label", string=re.compile("Annual Sales", re.I))
            if sales_label:
                sales_value_tag = sales_label.find_next("p")
                if sales_value_tag:
                    annual_sales = sales_value_tag.get_text(strip=True)

            company_data.append({
                "Company Name": company_name,
                "Website URL": website,
                # "Product Types": ", ".join(product_types),
                "Product Types": hammer_unions_products,
                "Phone Number": phone,
                "Location": location,
                "Role": role,
                "Annual Sale": annual_sales,
                "Contact Supplier URL": contact_supplier_url
            })

            print(f"✅ ({idx}) {company_name} | {location} | {phone}")
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error at item {idx}: {e}")
            continue

driver.quit()

df = pd.DataFrame(company_data)
df.to_csv("thomas_hammer_unions.csv", index=False)
print("📁 Done! Data saved to thomas_hammer_unions.csv")
