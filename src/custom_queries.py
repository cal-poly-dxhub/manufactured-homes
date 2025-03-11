import boto3
from configparser import ConfigParser

# Function to read adapter configuration
def read_adapter_config(name, key, config_file="adapter.config"):
    config = ConfigParser()
    config.read(config_file)
    return config[name][key]

# Displays information about a block returned by text detection and text analysis
def DisplayBlockInformation(block):
    print('Id: {}'.format(block['Id']))
    if 'Text' in block:
        print('    Detected: ' + block['Text'])
    print('    Type: ' + block['BlockType'])
   
    if 'Confidence' in block:
        print('    Confidence: ' + "{:.2f}".format(block['Confidence']) + "%")
    
    # Skip Geometry-related information since it's not necessary for query results
    if 'Relationships' in block:
        print('    Relationships: {}'.format(block['Relationships']))

    if 'Page' in block:
        print('Page: ' + block['Page'])
    print()

# Function to process text analysis with custom queries
def process_text_analysis(path):
    session = boto3.Session(profile_name='default')
    client = session.client('textract', region_name='us-west-2')

    # Custom Queries Configuration
    queriesConfig = { 
        "Queries": [ 
            {"Text": "Decal #"},
            {"Text": "Manufacturer"},
            {"Text": "Model"},
            {"Text": "Manufactured Date"},
            {"Text": "First Sold Date"},
            {"Text": "Record Conditions"},
            {"Text": "Last Reported Registered Owner"},
            {"Text": "Sale/Transfer Info"},
            {"Text": "Situs Address"}
        ]
    }

    # Open the image file
    with open(path, 'rb') as img_file:
        img_bytes = img_file.read()

        # Call Textract analyze_document API with custom queries
        response = client.analyze_document(
            Document={'Bytes': img_bytes}, 
            FeatureTypes=["FORMS", "SIGNATURES", "QUERIES"],
            AdaptersConfig={
                "Adapters":[
                    {
                        "AdapterId": "b33530ccb8d5",
                        "Version":"1",
                    }
                ]
            },
            QueriesConfig=queriesConfig
        )

    # Parse the Textract response
    blocks = response['Blocks']
    print('Detected Document Text')

    kvPairs = {}
    for block in blocks:
        if block['BlockType'] == 'QUERY':
            print('-' * 50)
            print(f"Query: {block['Query']['Text']}")
            if 'Relationships' in block:
                for relationship in block['Relationships']:
                    if relationship['Type'] == 'ANSWER':
                        for answer_id in relationship['Ids']:
                            # Find the answer block associated with the query
                            answer_block = next((b for b in blocks if b['Id'] == answer_id), None)
                            if answer_block and 'Text' in answer_block:
                                print(f"    Answer: {answer_block['Text']}")
                                # Store the answer in a key-value pair
                                kvPairs[block['Query']['Text']] = answer_block['Text']

    return kvPairs

# Example execution
def main():
     kvPairs = process_text_analysis("../RT_ESCROW_AND_TITLE_SEARCHES_8823460.pdf")
     print(kvPairs)
     

if __name__ == "__main__":
     main()

