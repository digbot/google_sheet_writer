from flask import Flask, jsonify, request
import json
import os
import codecs
from helpers.storeHelper import get_gid, create_cache_path
from constants import MSG_INDEX, DATA_FOLDER
import subprocess
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

debug_mode = os.getenv('DEBUG')

app = Flask(__name__)

DATA_FILE = create_cache_path(get_gid())

print(DATA_FILE)

def get_item_list(current_data, MSG_INDEX):
    if isinstance(current_data, dict) and MSG_INDEX in current_data:
        return current_data[MSG_INDEX]
    elif isinstance(current_data, list) and isinstance(MSG_INDEX, int):
        return current_data[MSG_INDEX]
    else:
        raise TypeError("Invalid data structure or index type")

def set_item_list(current_data, index, new_value):
    """
    Updates the `current_data` with `new_value` at the given `index` or key.

    Parameters:
    - current_data (dict or list): The data structure to update.
    - index (str or int): The key (if `current_data` is a dict) or index (if `current_data` is a list).
    - new_value: The new value to set at the specified `index` or key.

    Returns:
    - Updated `current_data`.
    """
    if isinstance(current_data, dict):
        if not isinstance(index, str):
            raise TypeError("Index must be a string for a dictionary.")
        if index not in current_data:
            raise KeyError(f"Key '{index}' not found in dictionary.")
        current_data[index] = new_value
    elif isinstance(current_data, list):
        if not isinstance(index, int):
            raise TypeError("Index must be an integer for a list.")
        if index < 0 or index >= len(current_data):
            raise IndexError("Index is out of range.")
        current_data[index] = new_value
    else:
        raise TypeError("`current_data` must be either a dictionary or a list.")

    return current_data

# Load initial data
# Define a route for DELETE requests
@app.route('/api/data/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
    # item_id is extracted from the URL path
        current_data = get_data()
        item_list = get_item_list(current_data, MSG_INDEX)
        print(item_id)
        print(len(item_list))
        item_list.pop(item_id-1)
        output_list_data = set_item_list(current_data, MSG_INDEX, item_list)
        with open(DATA_FILE, 'w', encoding='utf-8') as file:
            json.dump(output_list_data, file, ensure_ascii=False, indent=2)
        return jsonify({
            'message': f'Item with ID {item_id} has been deleted'
        }), 200
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: delete_item can't open file:" + DATA_FILE)
        return False

# Load initial data
@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        with codecs.open(DATA_FILE, "r", "utf-8") as f:
            data = json.load(f)
            if MSG_INDEX in data:
              return data
            else: 
                return []
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: fetch_manule_data can't open file:" + DATA_FILE)
        return False

# Save data
@app.route('/api/data', methods=['POST'])
def save_data():
    new_data = request.json
    current_data = get_data()
    item_list = get_item_list(current_data, MSG_INDEX)
    item_list.append(list(new_data.values()))
    output_list_data = set_item_list(current_data, MSG_INDEX, item_list)
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(output_list_data, file, ensure_ascii=False, indent=2)
    return jsonify({"message": "Data saved successfully"}), 200


# Save data
@app.route('/api/run', methods=['POST'])
def run():
    try:
       subprocess.run(["python", "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
    return jsonify({"message": "Ran with ok code"}), 200


# Run the app
if __name__ == '__main__':
    print("Run the app")
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
