
import json

def store_sheet_id(sheet_id):
    with open('sheet_id.json', 'w') as f:
        json.dump({'sheet_id': sheet_id }, f)

def get_sheet_id():
    try:
        with open('sheet_id.json') as f:
            data = json.load(f)
            sheet_id = data['sheet_id']
            return sheet_id
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Could not open sheet_id.json")
        return False
