from flask import Flask, jsonify, request
import json
import os
import codecs
from helpers.storeHelper import get_gid, create_cache_path
from constants import MSG_INDEX

app = Flask(__name__)

DATA_FILE = create_cache_path(get_gid())

# Load initial data
@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        with codecs.open(DATA_FILE, "r", "utf-8") as f:
            data = json.load(f)
            if MSG_INDEX in data:
              return jsonify(data)
            else: 
                return []
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: fetch_manule_data can't open file:" + path)
        return False


# Save data
@app.route('/api/data', methods=['POST'])
def save_data():
    new_data = request.json
    with open(DATA_FILE, 'w') as file:
        json.dump(new_data, file, ensure_ascii=False, indent=2)
    return jsonify({"message": "Data saved successfully"}), 200

# Run the app
if __name__ == '__main__':
    print("Run the app")
    app.run(debug=True)
