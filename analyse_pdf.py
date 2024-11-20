import boto3
import PyPDF2
import openai
import os
from io import BytesIO
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# AWS S3 and OpenAI setup
bucket_name = "my-bucket-chris"
openai.api_key = os.getenv("OPENAI_API_KEY")  # Get the key from the .env file

# Initialize S3 client
s3_client = boto3.client('s3')

def download_pdf_from_s3(bucket, key):
    """
    Download a PDF file from S3 and return as a BytesIO object.
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        pdf_data = response['Body'].read()
        return BytesIO(pdf_data)
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"AWS credentials error: {e}")
    except Exception as e:
        print(f"Error downloading PDF from S3: {e}")
    return None

def extract_text_from_pdf(pdf_data):
    """
    Extract text from a PDF file.
    """
    try:
        reader = PyPDF2.PdfReader(pdf_data)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return ""

def analyze_text_with_openai(text):
    """
    Analyze the extracted PDF text using OpenAI's GPT-3.5 or GPT-4 model.

    Args:
        text (str): The text to be analyzed.

    Returns:
        str: Analysis summary from OpenAI.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if needed
            messages=[
                {"role": "system", "content": "You are an AI assistant that provides summaries of documents."},
                {"role": "user", "content": f"Analyze the following text and provide a summary:\n\n{text}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error analyzing text with OpenAI: {e}")
    return "Unable to analyze text due to an error."

def process_pdfs():
    """
    Process all PDF files in the S3 bucket, analyze them using GPT-3, and print results.
    """
    try:
        pdf_files = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="pdfs/")
        if 'Contents' not in pdf_files:
            print("No PDFs found in the S3 bucket.")
            return

        for file in pdf_files['Contents']:
            file_key = file['Key']
            print(f"Processing {file_key}...")

            # Step 1: Download the PDF from S3
            pdf_data = download
