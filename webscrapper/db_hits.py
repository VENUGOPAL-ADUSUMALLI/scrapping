from .models import Companydetails, RecentCount

def get_data():
    # Check if any company has been seen before
    recent_entry = RecentCount.objects.last()

    if recent_entry:

        next_company = Companydetails.objects.filter(id__gt=recent_entry.recent_company_id.id).order_by('id').first()
    else:

        next_company = Companydetails.objects.order_by('id').first()

    if not next_company:
        return "✅ All companies have been sent."

    # Track the newly seen company
    RecentCount.objects.create(recent_company_id=next_company)

    # Prepare data
    data = f"""*🚀 Company Spotlight: {next_company.company_name}*

    📍 *Location:* {next_company.location}  
    🏭 *Type:* {next_company.company_type}
    
    🔗 *Company Profile:* {next_company.company_profile_url}

    🗂 *Directories:*  
    🔸 {next_company.directory_url.split(';')[0].strip()}  
    🔸 {next_company.directory_url.split(';')[1].strip()}  
    🔸 {next_company.directory_url.split(';')[2].strip()}

    """

    return data.strip()
