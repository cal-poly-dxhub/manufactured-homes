import streamlit as st
import tempfile
import os
import pandas as pd
import csv
from textract_utils import extract_text_from_pdf
from process_data import process_textract_output, data_to_csv
from custom_queries import process_text_analysis

# Streamlit UI
st.title("🏠 PDF Data Extractor with AWS Textract")
st.write("Upload your PDF documents, and we will extract structured data, format it into a CSV, and prepare it for download.")

uploaded_files = st.file_uploader("Please choose PDF files to process", type=["pdf"], accept_multiple_files=True, key="file_uploader")

# list of json data from pdf's
all_extracted_data = []

if uploaded_files:
    st.write("📄 Processing documents...")

    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_file_path = tmp_file.name
            
            # extract text from files and process them
            response = extract_text_from_pdf(temp_file_path)
            extracted_table_data = process_textract_output(response)
            extracted_data = process_text_analysis(temp_file_path)
            extracted_data.update(extracted_table_data)
            all_extracted_data.append(extracted_data)

            # display json info in well-formated way
            with st.expander(f"📄 {uploaded_file.name} Extracted Data"):
                for key, value in extracted_data.items():
                    if key == "serial_details" and isinstance(value, list):
                        st.write(f"### 📋 {key.replace('_', ' ').title()}")
                        if value:  
                            serial_df = pd.DataFrame(value)
                            st.dataframe(serial_df)
                        else:
                            st.write("No serial details available.")
                    else:
                        st.write(f"**{key}:** {value}")

            os.remove(temp_file_path)

        elif file_extension == 'csv':
            csv_data = pd.read_csv(uploaded_file)
            st.write(f"Processing CSV document: {uploaded_file.name}...")
            st.subheader(f"Extracted Information from CSV: {uploaded_file.name}")
            st.write(csv_data)

    if all_extracted_data:
        file_path = "output.csv"
        data_to_csv(all_extracted_data, file_path)

        with open(file_path, "rb") as f:
            st.download_button(
                label="Download CSV",
                data=f,
                file_name="processed_data.csv",
                mime="text/csv",
                key="download_updated_csv"
            )
        st.success("CSV has been updated with PDF data!")
