import requests
import datetime
import calendar


def last_day_of_current_month():
    today = datetime.date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return last_day

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