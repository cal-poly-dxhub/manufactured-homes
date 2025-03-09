import re

def get_kv_pairs(response):
    kv_pairs = {}
    blocks = response["Blocks"]
    key_map = {}
    value_map = {}

    for block in blocks:
        if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block["EntityTypes"]:
            key_map[block["Id"]] = block
        elif block["BlockType"] == "KEY_VALUE_SET" and "VALUE" in block["EntityTypes"]:
            value_map[block["Id"]] = block

    for key_id, key_block in key_map.items():
        key_text = get_text(key_block, blocks)
        if key_text:
            value_text = get_value_text(value_map, key_block, blocks)
            kv_pairs[key_text] = value_text

    return kv_pairs

# Function to get text from block
def get_text(block, blocks):
    text = ""
    if "Relationships" in block:
        for rel in block["Relationships"]:
            if rel["Type"] == "CHILD":
                for child_id in rel["Ids"]:
                    text += next((b["Text"] for b in blocks if b["Id"] == child_id), "") + " "
    return text.strip()

# Function to get value from key-value pair
def get_value_text(value_map, key_block, blocks):
    if "Relationships" in key_block:
        for rel in key_block["Relationships"]:
            if rel["Type"] == "VALUE":
                value_block = value_map.get(rel["Ids"][0])
                return get_text(value_block, blocks)
    return ""

# Function to extract table data
def get_table_data(response):
    tables = []
    for block in response["Blocks"]:
        if block["BlockType"] == "TABLE":
            table_data = []
            rows = {}
            for relationship in block.get("Relationships", []):
                if relationship["Type"] == "CHILD":
                    for id_ in relationship["Ids"]:
                        cell = next(b for b in response["Blocks"] if b["Id"] == id_)
                        if cell["BlockType"] == "CELL":
                            row_index = cell["RowIndex"]
                            col_index = cell["ColumnIndex"]
                            text = get_text(cell, response["Blocks"])

                            if row_index not in rows:
                                rows[row_index] = {}
                            rows[row_index][col_index] = text

            for row_index in sorted(rows.keys()):
                row_data = [rows[row_index].get(i, "") for i in sorted(rows[row_index].keys())]
                table_data.append(row_data)

            tables.append(table_data)
    return tables

# Function to extract Sale/Transfer Info
def extract_sale_info(text):
    price_match = re.search(r"Price\s+\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", text)
    transfer_date_match = re.search(r"Transferred on\s+(\d{2}/\d{2}/\d{4})", text)
    
    return {
        "Price": f"${price_match.group(1)}" if price_match else None,
        "Transferred On": transfer_date_match.group(1) if transfer_date_match else None
    }

# Process Textract response
def process_textract_output(response):
    kv_pairs = get_kv_pairs(response)
    tables = get_table_data(response)

    print(kv_pairs)
    
    # Extract key details
    data = {
        "Decal #": kv_pairs.get("Decal #:", ""),
        "Manufacturer": kv_pairs.get("Manufacturer:", ""),
        "Model": kv_pairs.get("Model:", ""),
        "Manufactured Date": kv_pairs.get("Manufactured Date:", ""),
        "First Sold Date": kv_pairs.get("First Sold On:", ""),
        "Record Conditions": kv_pairs.get("Record Conditions:", ""),
        "Last Reported Registered Owner": kv_pairs.get("Last Reported Registered Owner:", ""),
        "Situs Address": kv_pairs.get("Situs Address:", "")
    }

    record_conditions = kv_pairs.get("Record Conditions:", "")
    if "Permanent Foundation -" in kv_pairs:
        data["Record Conditions"] = "Permanent Foundation - " + kv_pairs.get("Record Conditions:")

    

    # Extract serial number table
    serial_info = []
    if tables:
        for row in tables:  
            if row[0] == ['Serial Number', 'HUD Label / Insignia', 'Length', 'Width']:
                for i in range(1,len(row)):
                    serial_info.append({
                        "Serial Number": row[i][0],
                        "HUD Label/Insignia": row[i][1],
                        "Length": row[i][2],
                        "Width": row[i][3]
                    })

    data["serial_details"] = serial_info

    # Extract sale/transfer info
    full_text = " ".join([block.get("Text", "") for block in response["Blocks"] if block["BlockType"] == "LINE"])
    data["Sale/Transfer Info"] = extract_sale_info(full_text)

    return data