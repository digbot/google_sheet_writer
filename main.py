import gspread
import datetime
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from helpers.commonHelper import create_line_object, DATE_FORMAT
from helpers.storeHelper import get_sheet_id, append_to_json_file, get_processed_ids, get_gid, fetch_manule_data
from service.sheet.sheetService import get_first_empty_row, get_sheet, clear_worksheet
from service.gmail.gmailService import get_gmail_service, get_gmail_cred
from collections import deque

# Define the scopes that the application will need
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/spreadsheets']

def fetch_message(service, search_query):
    input_dt = datetime.today()
    first_day_of_a_month = input_dt.replace(day=1)
    date_after = str(int(first_day_of_a_month.timestamp()))
    query = "after:" + date_after + ";subject:" + search_query
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
    
    #data.reverse()
    data.sort(key=lambda x: datetime.strptime(x[0], DATE_FORMAT))

    return data

def search_messages(search_query, processed_ids):
    service = get_gmail_service()
    """Searches for messages using the Gmail API and returns a list of message IDs"""
    try:

        messages = fetch_message(service, search_query)

        data = []
        # Print the subject of each email
        msg_ids = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            #headers = msg['payload']['headers']
            msg_id = msg['id']
            line = create_line_object(msg['snippet'], msg_id)
            
            is_msg_processed = msg_id not in processed_ids
            if line and is_msg_processed:
                data.append(line)
                print('Added: ' + msg['snippet'])
            else:
                print('Bypass: ' + msg['snippet'])
            if line:
                last_elem = deque(line).pop()
                msg_ids.append(last_elem)
          
        append_to_json_file(msg_ids)

        return data

    except HttpError as error:
        print(F'An error occurred: {error}')

if __name__ == '__main__':

    # Create a new Google Sheet
    creds = get_gmail_cred()

    # Build the Gmail API service
    sheets_service = build('sheets', 'v4', credentials=creds)
    client = gspread.authorize(creds)

    sheet_id = get_sheet_id()

    git = get_gid()

    processed_ids = get_processed_ids(git)
    
    sheet = get_sheet(sheet_id, git, sheets_service, client)

    clear_worksheet(sheets_service, sheet_id, git)

    first_empty_row = get_first_empty_row(sheets_service, sheet_id, git)
    print(f'{first_empty_row} first_empty_row')

    # Search for messages with subject "CC NOTIFICATION"
    msgs_data = search_messages("CC NOTIFICATION", processed_ids)

    manuel_data = fetch_manule_data()

    msgs_data.append(manuel_data)

    print("The msgs_data is: ", msgs_data) #printing the array

    data = process_main_data(msgs_data)

    range_name = git + '!A1:C900'
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