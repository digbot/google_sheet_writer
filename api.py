from flask import Flask, jsonify, request
import json
import os
import codecs
import subprocess
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from functools import wraps
#from flask_cors import CORS

from helpers.storeHelper import get_gid, create_cache_path
from constants import MSG_INDEX, DATA_FOLDER

# Load the .env file
load_dotenv()

# Secret key for JWT
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_secret_key')

debug_mode = os.getenv('DEBUG')

app = Flask(__name__)
#CORS(app)  # This will allow all origins; you can configure it further if needed

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

# JWT token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check for token in the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

# Route to generate token (for testing purposes)
@app.route('/api/token', methods=['GET'])
def generate_token():
    token = jwt.encode({
        'sub': 'user123',
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, SECRET_KEY, algorithm="HS256")
    return jsonify({'token': token})

# Define a route for DELETE requests
@app.route('/api/data/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
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
        return jsonify({'message': 'Internal Server Error'}), 500
    except IndexError:
        return jsonify({'message': 'Item not found'}), 404

# Load initial data
@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        with codecs.open(DATA_FILE, "r", "utf-8") as f:
            data = json.load(f)
            if MSG_INDEX in data:
                return data
            else:
                return jsonify([]), 200
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: fetch_manule_data can't open file:" + DATA_FILE)
        return jsonify({'message': 'Internal Server Error'}), 500

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

# Run script
@app.route('/api/run', methods=['POST'])
def run():
    try:
        subprocess.run(["python", "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        return jsonify({"message": "Script execution failed"}), 500
    return jsonify({"message": "Ran with ok code"}), 200

# Run the app
if __name__ == '__main__':
    print("Run the app")
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
