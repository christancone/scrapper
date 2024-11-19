from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import boto3
import os
import time

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
time.sleep(5)  # Adjust this value based on your network speed

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
bucket_name = "my-bucket-chris"

# Initialize S3 client
try:
    s3_client = boto3.client('s3')  # Ensure your credentials are configured properly
    print("Successfully connected to S3.")
except Exception as e:
    print(f"Error initializing S3 client: {e}")
    driver.quit()
    exit(1)

# Function to check if a file already exists in the S3 bucket
def file_exists_in_s3(bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except s3_client.exceptions.ClientError:
        return False

# Download PDFs and upload them to S3, avoiding duplicates
if pdf_links:
    for pdf_url in pdf_links:
        try:
            # Get the file name from the URL
            file_name = pdf_url.split("/")[-1]
            s3_key = f"pdfs/{file_name}"

            # Check if the file already exists in the bucket
            if file_exists_in_s3(bucket_name, s3_key):
                print(f"File {file_name} already exists in the S3 bucket. Skipping upload.")
                continue

            # Get the PDF file content
            response = requests.get(pdf_url)
            response.raise_for_status()  # Ensure request was successful

            # Upload to S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,  # Path in S3 bucket
                Body=response.content,
                ContentType="application/pdf"
            )
            print(f"Uploaded: {file_name} to S3 bucket {bucket_name}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error downloading {pdf_url}: {req_err}")
        except boto3.exceptions.S3UploadFailedError as s3_err:
            print(f"Error uploading {pdf_url} to S3: {s3_err}")
        except Exception as e:
            print(f"Unexpected error: {e}")
else:
    print("No PDF links found.")

# Close the browser
driver.quit()
