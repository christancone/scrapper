from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os

# Setup Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode for better performance
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.cse.lk/pages/company-profile/company-profile.component.html?symbol=JKH.N0000"

# Load the page
driver.get(url)

# Wait for content to load (adjust timeout if needed)
driver.implicitly_wait(10)

# Extract all PDF links
pdf_links = []
elements = driver.find_elements(By.TAG_NAME, "a")
for element in elements:
    href = element.get_attribute("href")
    if href and href.endswith(".pdf"):
        pdf_links.append(href)

# Download PDFs
if not os.path.exists("pdfs"):
    os.makedirs("pdfs")

for pdf_url in pdf_links:
    response = requests.get(pdf_url)
    filename = os.path.join("pdfs", pdf_url.split("/")[-1])
    with open(filename, "wb") as file:
        file.write(response.content)
    print(f"Downloaded: {filename}")

# Close the browser
driver.quit()
