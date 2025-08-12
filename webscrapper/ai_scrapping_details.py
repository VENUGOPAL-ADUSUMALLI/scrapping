import requests
from openai import OpenAI

TAVILY_API_KEY ="tavily api key"
OPENAI_API_KEY="Your APi KEY"

client = OpenAI(api_key=OPENAI_API_KEY)

def fetch_company_info_from_web(company_name):
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": f"{company_name} founders, background, market scope, risk factors",
        "max_results": 3
    }
    res = requests.post(url, json=payload, headers=headers)
    data = res.json()
    return "\n".join([r["content"] for r in data.get("results", [])])

def get_more_company_details(company_details):
    web_info = fetch_company_info_from_web(company_details.company_name)

    prompt = f"""
    You are an experienced business analyst.

    Use BOTH the provided company details AND the web search results to 
    produce a structured, factual summary. 
    If still no info is found, write "Not Available".

    Format:
    Company Name:
    Founders and Background:
    Problem They’re Solving:
    Risk Factor Analysis:
    Future Scope:
    Market Scope:

    Provided Company Data:
    Name: {company_details.company_name}
    Location: {company_details.location}
    Type: {company_details.company_type}
    Directory: {company_details.directory}
    Profile URL: {company_details.company_profile_url}
    Directories: {company_details.directory_url}

    Web Search Results:
    {web_info}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
