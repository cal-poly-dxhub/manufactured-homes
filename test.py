import boto3
import time

# Initialize AWS clients
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')

def extract_text_from_s3(bucket_name, file_key):
    # Call Textract API to process the document from S3
    response = textract_client.start_document_text_detection(
        DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': file_key}}
    )

    return response

def parse_textract_data_with_position(response):
    extracted_data = {
        "Decal #": None,
        "Manufacturer": None,
        "Model": None,
        "Manufactured Date": None,
        "First Sold Date": None,
        "Serial Number": None,
        "HUD Label/Insignia": None,
        "Length": None,
        "Width": None,
        "Record Conditions": None,
        "Last Reported Registered Owner": None,
        "Sale/Transfer Info": None,
        "Situs Address": None
    }

    blocks = response['Blocks']
    
    # Define a threshold for "right side" text (you can adjust this value as needed)
    right_threshold = 0.5  # For example, anything with an 'X' coordinate > 0.5 is considered 'right'

    # To store the last block that is on the right side of the page
    last_right_side_block = None

    for block in blocks:
        if block['BlockType'] == 'LINE':
            text = block['Text']
            left = block['Geometry']['BoundingBox']['Left']
            top = block['Geometry']['BoundingBox']['Top']
            width = block['Geometry']['BoundingBox']['Width']
            height = block['Geometry']['BoundingBox']['Height']

            # Check if the block is on the right side of the page
            if left + width > right_threshold:
                # Check if the block is for one of the fields we care about
                if 'decal' in text.lower() and "number" in text.lower():
                    extracted_data['Decal #'] = text
                elif 'manufacturer' in text.lower():
                    extracted_data['Manufacturer'] = text
                elif 'model' in text.lower():
                    extracted_data['Model'] = text
                elif 'manufactured' in text.lower() and 'date' in text.lower():
                    extracted_data['Manufactured Date'] = text
                elif 'first sold' in text.lower():
                    extracted_data['First Sold Date'] = text
                elif 'serial' in text.lower():
                    extracted_data['Serial Number'] = text
                elif 'hud' in text.lower() and 'label' in text.lower():
                    extracted_data['HUD Label/Insignia'] = text
                elif 'length' in text.lower():
                    extracted_data['Length'] = text
                elif 'width' in text.lower():
                    extracted_data['Width'] = text
                elif 'record conditions' in text.lower():
                    extracted_data['Record Conditions'] = text
                else:
                    # Store the last block on the right side (for "Record Conditions")
                    last_right_side_block = text

    # Special case: If "Record Conditions" is slightly below, it might be in the last block we found on the right
    if last_right_side_block:
        extracted_data['Record Conditions'] = last_right_side_block

    return extracted_data


# S3 bucket and file information
bucket_name = "manufactured-homes-file-upload"
file_key = "sampledocs/RT_ESCROW_AND_TITLE_SEARCHES_8741771.pdf"

# Extract text from the document in S3
response = extract_text_from_s3(bucket_name, file_key)

# Wait for the Textract job to complete (you can poll this with a delay or use a notification if needed)
job_id = response['JobId']

# Poll the Textract job status
def get_job_status(job_id):
    while True:
        result = textract_client.get_document_text_detection(JobId=job_id)
        status = result['JobStatus']
        if status in ['SUCCEEDED', 'FAILED']:
            return result
        print("Waiting for Textract job to complete...")
        time.sleep(5)

# Get the final result after the job completes
final_response = get_job_status(job_id)

# Parse and print the extracted information
extracted_info = parse_textract_data_with_position(final_response)
for key, value in extracted_info.items():
    print(f"{key}: {value}")
