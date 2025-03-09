import boto3
import re
import json

# Initialize AWS Textract client
textract = boto3.client("textract", region_name="us-west-2")  # Change region if needed

# Read PDF and send to Textract
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        response = textract.analyze_document(
            Document={"Bytes": file.read()},
            FeatureTypes=["FORMS", "TABLES"]
        )
    return response
