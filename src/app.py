import streamlit as st
import tempfile
import os
import pandas as pd
import csv
import zipfile
from textract_utils import extract_text_from_pdf
from process_data import process_textract_output, data_to_csv
from custom_queries import process_text_analysis

# Streamlit UI
st.title("🏠 PDF Data Extractor with AWS Textract")
st.write("Upload your PDF documents, and we will extract structured data, format it into a CSV, and prepare it for download.")

uploaded_files = st.file_uploader("Please choose PDF files to process", type=["pdf","zip"], accept_multiple_files=True, key="file_uploader")

# list of json data from pdf's
all_extracted_data = []

def extract_zip(zip_file):
    """Extracts the ZIP file to a temporary directory and returns the list of extracted PDF files."""
    tmpdir = tempfile.mkdtemp()  # Create a temporary directory
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(tmpdir)
        extracted_files = os.listdir(tmpdir)  # List files at the root level
        #st.write(f"Extracted files: {extracted_files}")  # Print files for debugging

    # Walk through all files (including those in subdirectories) and find PDFs
    pdf_files = []
    for root, dirs, files in os.walk(tmpdir):  # Walk through directories
        for f in files:
            # Skip system files (like __MACOSX and '._' files) and check for PDFs
            if not f.startswith('__MACOSX') and not f.startswith('._') and f.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, f))  # Add full path to PDF list

    # Log all PDFs that were found
    #st.write(f"PDF files found: {pdf_files}")  # Display PDFs for debugging
    
    if not pdf_files:
        raise ValueError("No PDF files found in the ZIP archive.")
    
    return pdf_files, tmpdir


    
if uploaded_files:
    st.write("📄 Processing documents...")

    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_file_path = tmp_file.name
            
            # extract text from files and process them
            
            #response = extract_text_from_pdf(temp_file_path)
            #extracted_table_data = process_textract_output(response)
            extracted_data = process_text_analysis(temp_file_path)
            #extracted_data.update(extracted_table_data)
            all_extracted_data.append(extracted_data)

            # display json info in well-formated way
            with st.expander(f"📄 Extracted Data from {temp_file_path}"):
                # Display the rest of the data as plain text first
                serial_details_keys = ['Serial Number', 'HUD Label/Insignia', 'Length', 'Width']

                # Display the rest of the data that is not part of serial details
                for key, value in extracted_data.items():
                    if key not in serial_details_keys:
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")

                # Filter serial details from the extracted data
                serial_details = {key: value for key, value in extracted_data.items() if key in serial_details_keys}

                # Find the maximum length of the lists in serial_details
                max_length = max(len(value) for value in serial_details.values())

                # Pad the shorter lists with empty strings to match the length of the longest list
                for key in serial_details:
                    while len(serial_details[key]) < max_length:
                        # Leave empty strings for the fields without data
                        serial_details[key].append("")

                # Display the serial details as a table at the end
                st.write("### 📋 Serial Details")
                serial_df = pd.DataFrame(serial_details)
                st.dataframe(serial_df)

            # If you have a temp file, remove it
            os.remove(temp_file_path)


        elif file_extension == 'csv':
            csv_data = pd.read_csv(uploaded_file)
            st.write(f"Processing CSV document: {uploaded_file.name}...")
            st.subheader(f"Extracted Information from CSV: {uploaded_file.name}")
            st.write(csv_data)
        
        elif file_extension == 'zip':
            # Process ZIP file
            st.write(f"Processing ZIP document: {uploaded_file.name}...")
            zip_file_paths, tmpdir = extract_zip(uploaded_file)

            for pdf_path in zip_file_paths:
                # st.write(f"Found PDF file: {pdf_path}")
                print(pdf_path)
                
               
                # extract text from files and process them
                response = extract_text_from_pdf(pdf_path)
                #extracted_table_data = process_textract_output(response)
                extracted_data = process_text_analysis(pdf_path)
                #extracted_data.update(extracted_table_data)
                all_extracted_data.append(extracted_data)

                # display json info in well-formated way
                with st.expander(f"📄 Extracted Data from {pdf_path}"):
                    # Display the rest of the data as plain text first
                    serial_details_keys = ['Serial Number', 'HUD Label/Insignia', 'Length', 'Width']

                    # Display the rest of the data that is not part of serial details
                    for key, value in extracted_data.items():
                        if key not in serial_details_keys:
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")

                    # Filter serial details from the extracted data
                    serial_details = {key: value for key, value in extracted_data.items() if key in serial_details_keys}

                    # Find the maximum length of the lists in serial_details
                    max_length = max(len(value) for value in serial_details.values())

                    # Pad the shorter lists with empty strings to match the length of the longest list
                    for key in serial_details:
                        while len(serial_details[key]) < max_length:
                            # Leave empty strings for the fields without data
                            serial_details[key].append("")

                    # Display the serial details as a table at the end
                    st.write("### 📋 Serial Details")
                    serial_df = pd.DataFrame(serial_details)
                    st.dataframe(serial_df)

                # If you have a temp file, remove it
                os.remove(pdf_path)


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
