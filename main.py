import gspread
import datetime
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from helpers.commonHelper import create_line_object, is_subject_ignored, DATE_FORMAT
from helpers.storeHelper import get_sheet_id, get_gid, get_subject_from_config, get_buffer, get_invest, get_indata
from service.sheet.sheetService import get_first_empty_row, get_sheet, clear_worksheet
from service.gmail.gmailService import get_gmail_service, get_gmail_cred
from collections import deque
from service.httpClient import send_month_data, send_day_data, get_day_data, get_full_day_data, get_total_day_data
import re
from time import strptime
import calendar

# Define the scopes that the application will need
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/spreadsheets']

def get_first_day_of_a_month(): 
    input_dt = datetime.today()
    first_day_of_a_month = input_dt.replace(day=1)
    return first_day_of_a_month

def get_first_day_of_a_month_by_gid(gid): 
    year = re.findall(r'\d+', gid)
    year = str(year[0])
    month = gid.replace(year,'')
    month = strptime(month,'%b').tm_mon
    input_dt = datetime.today()
    first_day_of_a_month = input_dt.replace(year = int('20' + year), month = int(month), day=1, hour=0, minute=0, second=0)
    return first_day_of_a_month
 
def get_last_day_of_a_month_by_gid(gid):
    year = re.findall(r'\d+', gid)
    year = str(year[0])
    month = gid.replace(year,'')
    month = strptime(month,'%b').tm_mon
    year = int('20' + year)
    month = int(month)
    _, last_day = calendar.monthrange(year, month)
    input_dt = datetime.today()
    lastt_day_of_a_month = input_dt.replace(year = year, month = month, day=last_day, hour=23, minute=59, second=59)
    return lastt_day_of_a_month

def fetch_message(service, search_query, gid):
    first_day_of_a_month = get_first_day_of_a_month_by_gid(gid)
    last_day_of_a_month = get_last_day_of_a_month_by_gid(gid)
    print('from: ' + str(first_day_of_a_month) +' to: ' + str(last_day_of_a_month))
    date_after = str(int(first_day_of_a_month.timestamp()))
    date_before = str(int(last_day_of_a_month.timestamp()))
    query = "after:" + date_after + ";before:" + date_before +  ";subject:" + search_query
    #query = "subject:" + search_query
    print('fetch_message_Query: ' + query)
    response = service.users().messages().list(userId='me', q=query).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in response:
            messages.extend(response['messages'])
    return messages

def process_main_data(data):
    
    data.sort(key=lambda x: datetime.strptime(x[0], DATE_FORMAT))

    return data

def search_messages(search_query, processed_ids, git):
    service = get_gmail_service()
    """Searches for messages using the Gmail API and returns a list of message IDs"""
    try:

        messages = fetch_message(service, search_query, git)

        data = []
        # Print the subject of each email
        msg_ids = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            #headers = msg['payload']['headers']
            msg_id = msg['id']
            subject = msg['snippet']

            if is_subject_ignored(subject):
                continue

            line = create_line_object(subject, msg_id)
            is_msg_processed = msg_id not in processed_ids
            if line and is_msg_processed:
                data.append(line)
                send_day_data(line, deque(line).pop())
                print('Added: ' + subject)
            else:
                print('Bypass: ' + subject)
            if line:
                last_elem = deque(line).pop()
                msg_ids.append(last_elem)
          
#        append_to_json_file(msg_ids, git)
         #   for hash in msg_ids:
         #       (hash)
        return data

    except HttpError as error:
        print(F'An error occurred: {error}')

def add_item(data, cache_data):
    if not data:
        return cache_data

    if len(cache_data):
        for cache_item in cache_data:
            key = cache_item[0]
            cache_item_str = '_'.join(cache_item)
            cache_item.append(str(key) + '_' + str(hash(cache_item_str)))
            data.append(cache_item)
    return data

def write_data_into_sheet(sheet_id, git, data):
    print("The msgs_data is: ", data) #printing the array

    data = process_main_data(data)

    range_name = git + '!A1:E900'
    value_input_option = 'USER_ENTERED'
    body = {
        'range': range_name,
        'values': data,
        'majorDimension': 'ROWS',
    }
    result = sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_name, valueInputOption=value_input_option, body=body
    ).execute()

    if "updatedCells" in result:
        print(f'{result["updatedCells"]} cells updated')

def accumulate_total(array):
    total = 0

    for sublist in array:
        try:
            total += int(sublist[1])
        except ValueError:
            pass

    return total

def spread_data(sheet_id, git, data, total_data):
    write_data_into_sheet(sheet_id, git, data)
    buffer = get_buffer()
    invest = get_invest()
    inData = get_indata()
    send_month_data(inData, total_data, buffer, invest)

if __name__ == '__main__':

    # Create a new Google Sheet
    creds = get_gmail_cred()

    # Build the Gmail API service
    sheets_service = build('sheets', 'v4', credentials=creds)
    client = gspread.authorize(creds)

    sheet_id = get_sheet_id()

    git = get_gid()

    processed_ids = get_day_data()
    
    sheet = get_sheet(sheet_id, git, sheets_service, client)

    clear_worksheet(sheets_service, sheet_id, git)

    first_empty_row = get_first_empty_row(sheets_service, sheet_id, git)
    print(f'{first_empty_row} first_empty_row')

    subject = get_subject_from_config()

    msgs_data = search_messages(subject, processed_ids, git)
    
    data = get_full_day_data()

    total_data = get_total_day_data()

    print("The data dunmp is: ", data) #printing the array

    spread_data(sheet_id, git, data, total_data)