from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import boto3
import os
import time
from io import BytesIO

# Setup Selenium WebDriver with additional options for headless mode
options = Options()
options.add_argument("--headless")  # Run in headless mode for better performance
options.add_argument("--no-sandbox")  # Prevent sandboxing issues in headless mode
options.add_argument("--disable-dev-shm-usage")  # Prevent /dev/shm usage
options.add_argument("--disable-gpu")  # Disable GPU usage (optional for headless)
options.add_argument("--window-size=1920,1080")  # Set screen size for headless mode

# Set the path to Chrome binary
options.binary_location = "/usr/bin/google-chrome-stable"

# Initialize the WebDriver
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("WebDriver successfully initialized.")
except Exception as e:
    print(f"Error initializing WebDriver: {e}")
    exit(1)

# Define the target URL
url = "https://www.cse.lk/pages/company-profile/company-profile.component.html?symbol=JKH.N0000"

# Load the page
try:
    driver.get(url)
    print(f"Successfully loaded: {url}")
except Exception as e:
    print(f"Error loading the page: {e}")
    driver.quit()
    exit(1)

# Wait for content to load (adjust timeout if needed)
time.sleep(5)  # This can be adjusted for your network speed

# Extract all PDF links
pdf_links = []
try:
    elements = driver.find_elements(By.TAG_NAME, "a")
    for element in elements:
        href = element.get_attribute("href")
        if href and href.endswith(".pdf"):
            pdf_links.append(href)
    print(f"Found {len(pdf_links)} PDF links.")
except Exception as e:
    print(f"Error extracting PDF links: {e}")

# AWS S3 configuration
s3_client = boto3.client('s3')
bucket_name = "my-bucket-chris"

# Download PDFs and upload them to S3
if pdf_links:
    for pdf_url in pdf_links:
        try:
            # Get the PDF file content
            response = requests.get(pdf_url)
            file_name = pdf_url.split("/")[-1]

            # Upload to S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=f"pdfs/{file_name}",  # Path in S3 bucket (adjust as needed)
                Body=BytesIO(response.content),
                ContentType="application/pdf"
            )
            print(f"Uploaded: {file_name} to S3 bucket {bucket_name}")
        except Exception as e:
            print(f"Error uploading {pdf_url} to S3: {e}")
else:
    print("No PDF links found.")

# Close the browser
driver.quit()
