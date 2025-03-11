import streamlit as st
import tempfile
import os
import json
from textract_utils import extract_text_from_pdf
from process_data import process_textract_output, data_to_csv
from custom_queries import process_text_analysis

# Streamlit UI
st.title("🏠 PDF Data Extractor with AWS Textract")
st.write(f"Upload your PDF document and an exisiting CSV you'd like to add to, and we'll extract the structured data and append to your CSV.")

# Upload file section
uploaded_files = st.file_uploader("Choose PDF or CSV files", type=["pdf", "csv"], accept_multiple_files=True)

if uploaded_files:
    st.write("📄 Processing documents...")
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # the docs
        if file_extension == 'pdf':
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_file_path = tmp_file.name
            response = extract_text_from_pdf(temp_file_path)
            extracted_table_data = process_textract_output(response)
            extracted_data = process_text_analysis(temp_file_path)

            extracted_data.update(extracted_table_data)

            st.subheader(f"Extracted Information from PDF: {uploaded_file.name}")
            st.json(extracted_data)

            updated_csv_data = data_to_csv(extracted_data)  

            # Cleanup temp file
            os.remove(temp_file_path)
            st.success("Extraction completed!")

        elif file_extension == 'csv':
            csv_data = pd.read_csv(uploaded_file)
            st.write(f"Processing CSV document: {uploaded_file.name}...")
            st.subheader(f"Extracted Information from CSV: {uploaded_file.name}")
            st.write(csv_data)

    # user can download csv at the end
    file_path = "processed_data.csv"  
    data_to_csv(extracted_data, file_path)
    with open(file_path, "rb") as f:
        st.download_button(
            label="Download CSV",
            data=f,
            file_name="processed_data.csv",
            mime="text/csv",
            key="download_updated_csv"
        )
    
    st.success("CSV has been updated with PDF data!")
    
    #TODO: take in user's csv and append to their csv

