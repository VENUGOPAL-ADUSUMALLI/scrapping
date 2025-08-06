import pandas as pd
from webscrapper.models import Companydetails

# Read CSV file into a DataFrame
csv_file_path ='yc_companies_20250806_213317.csv'

df = pd.read_csv(csv_file_path, on_bad_lines="skip")

# Iterate through the DataFrame and create Book instances
for index, row in df.iterrows():
    company = Companydetails(
        company_name=row['company_name'],
        location=row['location'],
        company_type=row['company_type'],
        directory=row['directories'],
        directory_url=row['directory_urls'],
        company_profile_url=row['profile_url'],
        scrapped_at=row['scraped_at'],
    )
    company.save()

print("CSV data has been loaded into the Django database.")
