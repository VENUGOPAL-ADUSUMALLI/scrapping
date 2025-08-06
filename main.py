from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in background

# Initialize driver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Load the page
    driver.get('https://www.ycombinator.com/companies')
    base_url = "https://www.ycombinator.com"

    # Wait for content to load
    time.sleep(3)

    # Get page source after JavaScript execution
    html_text = driver.page_source

    soup = BeautifulSoup(html_text, 'html.parser')

    # Now try finding companies
    company = soup.find_all('a', class_='!py-4 _company_i9oky_355')
    for each in company:
        company_name = each.find('span', class_='_coName_i9oky_470').text
        company_location = each.find('span', class_='_coLocation_i9oky_486').text.replace(' ', "")
        company_type = each.find('div', class_='mb-1.5 text-sm').text
        company_directory = each.find_all('a', class_='_tagLink_i9oky_1040')
        directories_list = []
        for each_directory in company_directory:
            directory_name = each_directory.find('span', class_='pill _pill_i9oky_33').text.replace(" ", "")
            get_directory_url = each_directory.get('href')
            if ' ' in get_directory_url:
                get_directory_url = get_directory_url.replace(' ', '%20')

            full_url = urljoin(base_url, get_directory_url)
            directories_list.append((directory_name, full_url))

        more_about_company = each.get('href')
        full_info_url = urljoin(base_url, more_about_company)

        print(
            f" company name: {company_name} \n location: {company_location} \n based on: {company_type} \n directories :{directories_list}  \n more_info :{full_info_url}")
        print("          ")

    print(f"Found {len(company)} companies")

finally:
    driver.quit()