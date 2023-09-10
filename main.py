import gspread
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from helpers.commonHelper import extract_bgn_numbers_and_dates,DATE_FORMAT
from helpers.storeHelper import get_sheet_id, append_to_json_file, get_processed_ids, get_gid
from service.sheet.sheetService import get_first_empty_row, get_sheet, clear_worksheet
from service.gmail.gmailService import get_gmail_service, get_gmail_cred

# Define the scopes that the application will need
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/spreadsheets']

def fetch_message(service, search_query):
    query = "subject:" + search_query
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
            msg_ids.append(msg_id)
            line = extract_bgn_numbers_and_dates(msg['snippet'], msg_id)

            is_msg_processed = msg_id not in processed_ids
            if line and is_msg_processed:
                data.append(line)
                print('Added: ' + msg['snippet'])
            else:
                print('Bypass: ' + msg['snippet'])                 
          
        append_to_json_file(msg_ids)

        #data.reverse()
        data.sort(key=lambda x: datetime.datetime.strptime(x[0], DATE_FORMAT))
         
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

    sheet_title = get_gid()

    processed_ids = get_processed_ids()
    
    sheet = get_sheet(sheet_id, sheet_title, sheets_service, client)

    clear_worksheet(sheets_service, sheet_id, sheet_title)

    first_empty_row = get_first_empty_row(sheets_service, sheet_id, sheet_title)
    print(f'{first_empty_row} first_empty_row')

    # Search for messages with subject "CC NOTIFICATION"
    data = search_messages("CC NOTIFICATION", processed_ids)

    range_name = sheet_title + '!A1:C900'
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