import requests
from bs4 import BeautifulSoup

url = 'https://www.cse.lk/pages/company-profile/company-profile.component.html?symbol=JKH.N0000'  # Replace with actual URL

# Fetch page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all PDF links
pdf_links = []
for link in soup.find_all('a', href=True):
    if link['href'].endswith('.pdf'):
        pdf_links.append(link['href'])

# Download PDFs
for pdf in pdf_links:
    pdf_url = f"{url}/{pdf}" if not pdf.startswith('http') else pdf
    pdf_response = requests.get(pdf_url)
    with open(pdf.split('/')[-1], 'wb') as file:
        file.write(pdf_response.content)

    print(f"Downloaded: {pdf.split('/')[-1]}")
