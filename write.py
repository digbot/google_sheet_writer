import pickle
import os.path
import os
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, time, timedelta
import re
from datetime import datetime
import google.auth
from google.oauth2.credentials import Credentials
import json
import gspread
 
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

def store_sheet_id(sheet_id):
    with open('sheet_id.json', 'w') as f:
        json.dump({'sheet_id': sheet_id}, f)

def get_sheet_id():
    try:
        with open('sheet_id.json') as f:
            data = json.load(f)
            sheet_id = data['sheet_id']
            return sheet_id
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Could not open sheet_id.json")
        return False

def get_sheet(sheet_id, sheets_service, client):
    if sheet_id:
        sheet = client.open_by_key(sheet_id)
    else:
        sheet_title = 'Email content'
        sheet = sheets_service.spreadsheets().create(
            body={
                'properties': {'title': sheet_title},
                'sheets': [{'properties': {'title': 'Sheet 1'}}],
            }
        ).execute()
        sheet_id = sheet['spreadsheetId']
        print(f'Created new sheet with title "{sheet_title}" and ID "{sheet_id}"')
        store_sheet_id(sheet_id)
    return sheet

def extract_bgn_numbers_and_dates(text):
    # Regular expression to match BGN numbers
    bgn_pattern = r"\b\d+(?:\.\d{1,2})?\s*BGN\b"
    
    # Regular expression to match dates
    date_pattern = r"\b\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}\b"

    # Find all BGN numbers in the text
    bgn_matches = re.findall(bgn_pattern, text)
    
    # Find all dates in the text
    date_matches = re.findall(date_pattern, text)

    # Convert date strings to datetime objects
    dates = []
    for date_str in date_matches:
        date = datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
        dates.append(date)

    # Return a tuple of the BGN numbers and dates
    return bgn_matches, dates


def extract_bgn_numbers_and_dates(text):
    result = []
    # Regular expression to match BGN numbers
    bgn_pattern = r"\b\d+(?:\.\d{1,2})?\s*BGN\b"
    
    # Regular expression to match dates
    date_pattern = r"\b\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}\b"

    # Find all BGN numbers in the text
    bgn_matches = re.findall(bgn_pattern, text)
    
    # Find all dates in the text
    date_matches = re.findall(date_pattern, text)

    # Convert date strings to datetime objects
    #dates = []
    #for date_str in date_matches:
        #  date = datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
        # my_datetime_str = date.strftime("%Y-%m-%d %H:%M:%S")
        #bgn_matches.append(date_str)

    # Return a tuple of the BGN numbers and dates
    if  (len(date_matches) and len(bgn_matches)):
        return [date_matches[0], bgn_matches[0]]
    else:
        return ['','']

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

def search_messages(search_query):
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
            ['Name', 'Age', 'TIme']
        ]

        # Print the subject of each email
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload']['headers']
            data.append(extract_bgn_numbers_and_dates(msg['snippet']))
            print(msg['snippet'])
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

    sheet = get_sheet(sheet_id, sheets_service, client)
    
    # select a worksheet within the spreadsheet
    worksheet_list = sheet.worksheets()
    for worksheet in worksheet_list:
        worksheet.clear()

    # Search for messages with subject "CC NOTIFICATION"
    data = search_messages("CC NOTIFICATION")
                
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