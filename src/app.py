import streamlit as st
import tempfile
import os
import json
from textract_utils import extract_text_from_pdf
from process_data import process_textract_output

# Streamlit UI
st.title("🏠 PDF Data Extractor with AWS Textract")
st.write("Upload a PDF document, and we'll extract key details using AWS Textract.")

# Upload file section
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_file_path = tmp_file.name

    # Extract text using AWS Textract
    st.write("📄 Processing document...")
    response = extract_text_from_pdf(temp_file_path)

    # Process extracted data
    extracted_data = process_textract_output(response)

    # Display structured data
    st.subheader("Extracted Information")
    st.json(extracted_data)

    # Option to download as JSON
    st.download_button(
        label="Download Extracted Data as JSON",
        data=json.dumps(extracted_data, indent=4),
        file_name="extracted_data.json",
        mime="application/json"
    )

    # Cleanup temp file
    os.remove(temp_file_path)
    st.success("✅ Extraction completed!")
