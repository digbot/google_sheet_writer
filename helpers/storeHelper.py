
import json

STORE_FILE = 'sheet_id.json'
MSG_INDEX = 'msg_ids'
SHEET_INDEX = 'sheet_id'

def store_sheet_id(sheet_id):
    with open(STORE_FILE, 'w') as f:
        json.dump({SHEET_INDEX: sheet_id }, f)

def get_sheet_id():
    try:
        with open(STORE_FILE) as f:
            data = json.load(f)
            sheet_id = data[SHEET_INDEX]
            return sheet_id
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Could not open sheet_id.json")
        return False
    
def get_processed_ids():
    try:
        with open(STORE_FILE) as f:
            data = json.load(f)
            msg_id_list = data[MSG_INDEX]
            return msg_id_list
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Could not open sheet_id.json")
        return False

def append_to_json_file(data):
    try:
        # Load existing data from file
        with open(STORE_FILE, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        # Create new file if it doesn't exist
        json_data = []

    # Append new data to existing data
    json_data[MSG_INDEX] = data

    # Write updated data to file
    with open(STORE_FILE, 'w') as f:
        json.dump(json_data, f)
