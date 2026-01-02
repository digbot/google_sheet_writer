
import json
from datetime import datetime
from constants import STORE_FILE, MODE, MSG_INDEX, SHEET_INDEX, BUFFER, INVEST, INDATA, GID_INDEX, SUBJECT

def store_sheet_and_git_id(sheet_id, sheet_name, git):
    #with open(STORE_FILE, 'w') as f:
    #    json.dump({SHEET_INDEX: sheet_id, GID_INDEX: sheet_name }, f)
    with open(create_gmail_path(git), 'w') as f:
        json.dump({MSG_INDEX: [] }, f)

def get_mode():
    try:
        with open(STORE_FILE) as f:
            data = json.load(f)
            sheet_id = data[MODE]
            return sheet_id
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: mode Could not open " + STORE_FILE + ".json")
        return False

def get_gid():
    try:
        with open(STORE_FILE) as f:
            data = json.load(f)
            if GID_INDEX in data:
                gid = data[GID_INDEX]
                return gid
            else:
                year = datetime.now().strftime('%y')
                month = datetime.now().strftime('%h')
                return str(month)+str(year)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Could not open gid.json")
        return False

def get_sheet_id():
    try:
        with open(STORE_FILE) as f:
            data = json.load(f)
            sheet_id = data[SHEET_INDEX]
            return sheet_id
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: get_sheet_id Could not open " + STORE_FILE + ".json")
        return False

def get_buffer():
    try:
        with open(STORE_FILE) as f:
            data = json.load(f)
            buffer = data[BUFFER]
            return buffer
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: get_sheet_id Could not open " + STORE_FILE +  ".json")
        return False

def get_invest():
    try:
        with open(STORE_FILE) as f:
            data = json.load(f)
            invest = data[INVEST]
            return invest
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: get_sheet_id Could not open " + STORE_FILE +  ".json")
        return False
    
def get_indata():
    try:
        with open(STORE_FILE) as f:
            data = json.load(f)
            inData = data[INDATA]
            return inData
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: get_sheet_id Could not open " + STORE_FILE +  ".json")
        return False

def get_subject_from_config():
    try:
        with open(STORE_FILE) as f:
            data = json.load(f)
            subject = data[SUBJECT]
            return subject
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: get_subject_from_config Could not open " + STORE_FILE + ".json")
        return False
