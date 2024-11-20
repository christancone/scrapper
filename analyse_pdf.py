import boto3
import PyPDF2
import openai
import os
from io import BytesIO
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# AWS S3 and OpenAI setup
bucket_name = "my-bucket-chris"
openai.api_key = "your_openai_api_key"  # Replace with your OpenAI API key

# Initialize S3 client
s3_client = boto3.client('s3')

def download_pdf_from_s3(bucket, key):
    """
    Download a PDF file from S3 and return as a BytesIO object.

    Args:
        bucket (str): The name of the S3 bucket.
        key (str): The S3 key for the file.

    Returns:
        BytesIO: In-memory file-like object containing the PDF data.
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

    Args:
        pdf_data (BytesIO): In-memory file-like object containing the PDF data.

    Returns:
        str: Extracted text from the PDF.
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
    Analyze the extracted PDF text using OpenAI's GPT-3 model.

    Args:
        text (str): The text to be analyzed.

    Returns:
        str: GPT-3's analysis of the text.
    """
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # You can choose a different model if needed
            prompt=f"Analyze the following text and provide a summary:\n\n{text}",
            max_tokens=500
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error analyzing text with OpenAI: {e}")
    return "Error analyzing text."

def process_pdfs():
    """
    Process all PDF files in the S3 bucket, analyze them using GPT-3, and print results.
    """
    # List all PDF files in the S3 bucket under the 'pdfs/' folder
    try:
        pdf_files = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="pdfs/")
        if 'Contents' not in pdf_files:
            print("No PDFs found in the S3 bucket.")
            return

        for file in pdf_files['Contents']:
            file_key = file['Key']
            print(f"Processing {file_key}...")

            # Step 1: Download the PDF from S3
            pdf_data = download_pdf_from_s3(bucket_name, file_key)
            if not pdf_data:
                print(f"Skipping {file_key} due to download error.")
                continue

            # Step 2: Extract text from the PDF
            pdf_text = extract_text_from_pdf(pdf_data)
            if not pdf_text:
                print(f"Skipping {file_key} due to text extraction error.")
                continue

            # Step 3: Analyze text with OpenAI GPT-3
            analysis = analyze_text_with_openai(pdf_text)
            print(f"Analysis for {file_key}:\n{analysis}\n")

            # Optionally, save the analysis result to a file in S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=f"analysis/{file_key.replace('pdfs/', '').replace('.pdf', '_analysis.txt')}",
                Body=analysis,
                ContentType="text/plain"
            )
            print(f"Saved analysis for {file_key}.")

    except Exception as e:
        print(f"Error processing PDFs from S3: {e}")

if __name__ == "__main__":
    process_pdfs()