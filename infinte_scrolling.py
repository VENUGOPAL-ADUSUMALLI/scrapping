from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
import os

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)


def scroll_to_load_all_companies(driver, max_scrolls=50, scroll_pause_time=2):
    """Scroll to load all companies with infinite scroll"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls_performed = 0
    no_new_content_count = 0

    print("Starting infinite scroll...")

    while scrolls_performed < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        current_companies = len(driver.find_elements(By.CSS_SELECTOR, 'a._company_i9oky_355'))
        print(f"Scroll {scrolls_performed + 1}: Found {current_companies} companies")

        if new_height == last_height:
            no_new_content_count += 1
            print(f"No new content detected (attempt {no_new_content_count})")

            if no_new_content_count >= 3:
                print("Reached end of content or no more companies to load")
                break
        else:
            no_new_content_count = 0

        last_height = new_height
        scrolls_performed += 1

    final_count = len(driver.find_elements(By.CSS_SELECTOR, 'a._company_i9oky_355'))
    print(f"Finished scrolling. Total companies loaded: {final_count}")
    return final_count


def extract_company_data(soup, base_url):
    """Extract company data from parsed HTML"""
    companies_data = []
    companies = soup.find_all('a', class_='_company_i9oky_355')

    for company in companies:
        try:
            # Extract company name
            company_name_elem = company.find('span', class_='_coName_i9oky_470')
            company_name = company_name_elem.text.strip() if company_name_elem else "N/A"

            # Extract company location
            company_location_elem = company.find('span', class_='_coLocation_i9oky_486')
            company_location = company_location_elem.text.strip() if company_location_elem else "N/A"

            # Extract company type/description
            company_type_elem = company.find('div', class_='mb-1.5')
            company_type = company_type_elem.text.strip() if company_type_elem else "N/A"

            # Extract directories/tags
            directories_list = []
            directory_urls_list = []
            directory_elements = company.find_all('a', class_='_tagLink_i9oky_1040')

            for directory_elem in directory_elements:
                pill_elem = directory_elem.find('span', class_='pill')
                if pill_elem:
                    directory_name = pill_elem.text.strip()
                    directory_url = directory_elem.get('href', '')

                    if ' ' in directory_url:
                        directory_url = directory_url.replace(' ', '%20')

                    full_directory_url = urljoin(base_url, directory_url)
                    directories_list.append(directory_name)
                    directory_urls_list.append(full_directory_url)

            # Convert directories to strings for CSV compatibility
            directories_str = "; ".join(directories_list) if directories_list else "N/A"
            directory_urls_str = "; ".join(directory_urls_list) if directory_urls_list else "N/A"

            # Extract company profile URL
            company_url = company.get('href', '')
            full_company_url = urljoin(base_url, company_url)

            company_data = {
                'company_name': company_name,
                'location': company_location,
                'company_type': company_type,
                'directories': directories_str,
                'directory_urls': directory_urls_str,
                'profile_url': full_company_url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            companies_data.append(company_data)

        except Exception as e:
            print(f"Error extracting data for a company: {e}")
            continue

    return companies_data


def export_to_csv(companies_data, filename=None):
    """Export company data to CSV file"""
    if not companies_data:
        print("No data to export!")
        return None

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"yc_companies_{timestamp}.csv"

    try:
        # Method 1: Using pandas (recommended)
        df = pd.DataFrame(companies_data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ Data exported to CSV using pandas: {filename}")

    except ImportError:
        # Method 2: Using built-in csv module (fallback)
        print("pandas not found, using built-in csv module...")

        # Get all field names
        fieldnames = companies_data[0].keys() if companies_data else []

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(companies_data)

        print(f"✅ Data exported to CSV using built-in csv: {filename}")

    except Exception as e:
        print(f"❌ Error exporting to CSV: {e}")
        return None

    return filename


def export_to_json(companies_data, filename=None):
    """Export company data to JSON file (bonus format)"""
    if not companies_data:
        print("No data to export!")
        return None

    import json

    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"yc_companies_{timestamp}.json"

    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(companies_data, jsonfile, indent=2, ensure_ascii=False)

        print(f"✅ Data exported to JSON: {filename}")
        return filename

    except Exception as e:
        print(f"❌ Error exporting to JSON: {e}")
        return None


def print_csv_summary(companies_data):
    """Print summary of data that will be exported"""
    if not companies_data:
        print("No data to summarize!")
        return

    print("\n" + "=" * 60)
    print("CSV EXPORT SUMMARY")
    print("=" * 60)
    print(f"Total companies: {len(companies_data)}")
    print(f"Columns in CSV:")

    if companies_data:
        for i, column in enumerate(companies_data[0].keys(), 1):
            print(f"  {i}. {column}")

    print("\nSample data (first company):")
    if companies_data:
        for key, value in companies_data[0].items():
            # Truncate long values for display
            display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"  {key}: {display_value}")

    print("=" * 60)


try:
    print("Loading Y Combinator companies page...")
    driver.get('https://www.ycombinator.com/companies')
    base_url = "https://www.ycombinator.com"

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a._company_i9oky_355')))

    print("Initial page loaded successfully")

    # Perform infinite scroll
    total_companies = scroll_to_load_all_companies(
        driver,
        max_scrolls=100,  # Adjust based on how much data you want
        scroll_pause_time=2
    )

    print("Extracting company data...")
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'html.parser')

    # Extract all company data
    companies_data = extract_company_data(soup, base_url)

    print("\n" + "=" * 80)
    print(f"EXTRACTION COMPLETE - Found {len(companies_data)} companies")
    print("=" * 80)

    # Print CSV summary
    print_csv_summary(companies_data)

    # Export to CSV
    csv_filename = export_to_csv(companies_data)

    # Optional: Also export to JSON
    json_filename = export_to_json(companies_data)

    # Display sample data (first 5 companies)
    print(f"\n📋 SAMPLE DATA (First 5 companies):")
    print("-" * 50)

    for i, company in enumerate(companies_data[:5], 1):
        print(f"\n--- Company {i} ---")
        print(f"Name: {company['company_name']}")
        print(f"Location: {company['location']}")
        print(f"Type: {company['company_type']}")
        print(f"Directories: {company['directories']}")
        print(f"Profile URL: {company['profile_url']}")

    if len(companies_data) > 5:
        print(f"\n... and {len(companies_data) - 5} more companies in the CSV file")

    # File information
    print(f"\n📁 FILES CREATED:")
    if csv_filename:
        file_size = os.path.getsize(csv_filename) / 1024  # Size in KB
        print(f"  📊 CSV: {csv_filename} ({file_size:.1f} KB)")

    if json_filename:
        file_size = os.path.getsize(json_filename) / 1024  # Size in KB
        print(f"  📄 JSON: {json_filename} ({file_size:.1f} KB)")

    print(f"\n✅ Total companies scraped and exported: {len(companies_data)}")

except Exception as e:
    print(f"❌ An error occurred: {e}")

finally:
    print("Closing browser...")
    driver.quit()

print("\n🎉 Scraping and CSV export completed!")