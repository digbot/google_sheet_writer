import requests
import datetime
import calendar

def send_day_data(line, hash):
      # Define the URL to send the POST request to
    url = "http://localhost:3007/day"

    json_data = {
        "date": line[0], 
        "value": line[1],
        "comment": line[2],
        "note": line[3],
        "hash": hash
    }
    return send_post_request(url, json_data)

def get_day_data():
      # Define the URL to send the POST request to
    url = "http://localhost:3007/day/byMonth"
    response = do_get_request(url)
    day_data_item = response
    return list(map(lambda x: {"hash": x["hash"]}, day_data_item))


def get_full_day_data():
      # Define the URL to send the POST request to
    url = "http://localhost:3007/day/byMonth"
    response = do_get_request(url)
    output_data = [
        [item['date'], item['value'], item['comment'], item['note'], item['hash']]
        for item in response
    ]
    return output_data

def get_total_day_data():
      # Define the URL to send the POST request to
    url = "http://localhost:3007/day/byMonth"
    response = do_get_request(url)
        
    # Check if the response is valid and not empty
    if not response or not isinstance(response, list) or 'totalValue' not in response[0]:
        return 0
    
    return abs(float(response[0]['totalValue']))

def last_day_of_current_month():
    today = datetime.date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return last_day

def do_get_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        print("GET request sent successfully: ")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending POST request: {e}")

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
    url = "http://localhost:3007/month"

    # Define the JSON data to be sent in the request body
    last_day = last_day_of_current_month()
    today = datetime.datetime.now()
    current_date = str(today.now().strftime("%m.%d.%Y"))
    items = current_date.split('.')
    last_day_month = items[0] + '.'+ str(last_day) + '.' + items[2]

    json_data = {
        "date": last_day_month,
        "in": inData,
        "out": outData,
        "buffer": buffer,
        "invest": invest
    }

    # Send the POST request
    return send_post_request(url, json_data)