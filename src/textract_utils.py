import boto3
import re
import json
import fitz

# Initialize AWS Textract client
textract = boto3.client("textract", region_name="us-west-2")  # Change region if needed

# Read PDF and send to Textract
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        doc = fitz.open(file_path)
        page = doc.load_page(0)  # First page only
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        pix.save("test.png")

        response = textract.analyze_document(
            Document={"Bytes": img_bytes},
            FeatureTypes=["FORMS", "TABLES"]
        )
    return response
