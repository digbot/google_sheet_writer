import requests
from datetime import datetime

def send_post_request(url, data):
    try:
        print("Send data: ..")
        print(data) 
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        print("POST request sent successfully: ")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error sending POST request: {e}")

def send_month_data(inData, outData, buffer, invest):
    # Define the URL to send the POST request to
    url = "http://localhost:3000/month"

    # Define the JSON data to be sent in the request body
    current_date = str(datetime.now().strftime("%m.%d.%Y"))

    json_data = {
        "date": current_date,
        "in": inData,
        "out": outData,
        "buffer": buffer,
        "invest": invest
    }

    # Send the POST request
    return send_post_request(url, json_data)