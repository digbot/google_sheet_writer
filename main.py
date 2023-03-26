import pickle
import os.path
import os
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, time, timedelta
import google.auth
from google.oauth2.credentials import Credentials
import gspread
from helpers.commonHelper import extract_bgn_numbers_and_dates
from helpers.storeHelper import get_sheet_id, append_to_json_file, get_processed_ids
from service.sheet.sheetService import get_first_empty_row, get_sheet

# Define the scopes that the application will need
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/spreadsheets']

def get_gmail_cred():
    """Gets the Gmail API service"""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_gmail_service():
    """Gets the Gmail API service"""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service

def search_messages(search_query, processed_ids):
    service = get_gmail_service()
    """Searches for messages using the Gmail API and returns a list of message IDs"""
    try:
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
        
        data = [
            ['Data', 'Sum']
        ]

        # Print the subject of each email
        msg_ids = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            #headers = msg['payload']['headers']
            msg_id = msg['id']
            msg_ids.append(msg_id)
            line = extract_bgn_numbers_and_dates(msg['snippet'])
            is_msg_processed = msg_id not in processed_ids
            if line and is_msg_processed:
                data.append(line)
                print(msg['snippet'])
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

    processed_ids = get_processed_ids()
    
    sheet = get_sheet(sheet_id, sheets_service, client)

    first_empty_row = get_first_empty_row(sheets_service, sheet_id, "Sheet 1")
    print(f'{first_empty_row} first_empty_row')

    # select a worksheet within the spreadsheet
    worksheet_list = sheet.worksheets()
    for worksheet in worksheet_list:
        worksheet.clear()

    # Search for messages with subject "CC NOTIFICATION"
    data = search_messages("CC NOTIFICATION", processed_ids)
                
    range_name = 'Sheet 1!A1:C400'
    value_input_option = 'USER_ENTERED'
    body = {
        'range': range_name,
        'values': data,
        'majorDimension': 'ROWS',
    }
    result = sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_name, valueInputOption=value_input_option, body=body
    ).execute()
    print(f'{result["updatedCells"]} cells updated')