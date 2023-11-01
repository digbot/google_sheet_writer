
import json
from datetime import datetime
import codecs

STORE_FILE = 'config.json'
MANUAL_ITEMS = 'items'
MSG_INDEX = 'msg_ids'
SHEET_INDEX = 'sheet_id'
GID_INDEX = 'gid'
DATA_FOLDER = 'data/'
SUBJECT = 'subject'

def store_sheet_and_git_id(sheet_id, sheet_name, git):
    #with open(STORE_FILE, 'w') as f:
    #    json.dump({SHEET_INDEX: sheet_id, GID_INDEX: sheet_name }, f)
    with open(create_gmail_path(git), 'w') as f:
        json.dump({MSG_INDEX: [] }, f)

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
        print("Error: get_sheet_id Could not open " + STORE_FILE+ ".json")
        return False

def get_subject_from_config():
    try:
        with open(STORE_FILE) as f:
            data = json.load(f)
            subject = data[SUBJECT]
            return subject
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: get_subject_from_config Could not open " + STORE_FILE+ ".json")
        return False

def fetch_cache_data(git):
    path = create_cache_path(git)
    print("with open "+ path)
    try:
        with codecs.open(path, "r", "utf-8") as f:
            data = json.load(f)
            if MSG_INDEX in data:
                item_list = data[MSG_INDEX]
                print("The Array is: ", item_list) #printing the array
                return item_list
            else: 
                return []
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: fetch_manule_data can't open file:" + path)
        return False
    
def create_cache_path(git):
    path = DATA_FOLDER + git + '_cache.json'
    return path

def create_gmail_path(git):
    path = DATA_FOLDER + git + '_cc_card.json'
    return path

def get_processed_ids(git):
    try:
        with open(create_gmail_path(git)) as f:
            data = json.load(f)
            if MSG_INDEX in data:
                msg_id_list = data[MSG_INDEX]
                return msg_id_list
            else: 
                return []
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Could not open " + create_gmail_path(git) + ".json")
        return False

def append_to_json_file(data, git):
    try:
        # Load existing data from file
        with open(create_gmail_path(git), 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        # Create new file if it doesn't exist
        json_data = []

    # Append new data to existing data
    json_data[MSG_INDEX] = data

    # Write updated data to file
    with open(create_gmail_path(git), 'w') as f:
        json.dump(json_data, f)
