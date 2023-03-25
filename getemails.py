import pickle
import os.path
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
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def create_and_write_to_sheet(sheet_name, headers, data):
    # Get credentials
    creds, project = google.auth.default(scopes=['https://www.googleapis.com/auth/spreadsheets'])
    
    # Build the Sheets API client
    service = build('sheets', 'v4', credentials=creds)

    # Create a new spreadsheet
    spreadsheet = service.spreadsheets().create(body={
        'properties': {'title': sheet_name},
        'sheets': [{'properties': {'title': 'Sheet1', 'gridProperties': {'rowCount': len(data), 'columnCount': len(headers)}}}]
    }).execute()

    # Get the ID of the newly created sheet
    sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']

    # Add headers to the sheet
    header_range = f'Sheet1!1:1'
    header_values = [headers]
    request = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet['spreadsheetId'], range=header_range,
        valueInputOption='RAW', body={'values': header_values})
    response = request.execute()

    # Write data to the sheet
    data_range = f'Sheet1!A2:{chr(ord("A") + len(headers) - 1)}{len(data)+1}'
    request = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet['spreadsheetId'], range=data_range,
        valueInputOption='RAW', body={'values': data})
    response = request.execute()

    print(f"Sheet '{sheet_name}' created with {len(data)} rows and {len(headers)} columns.")

    return spreadsheet['spreadsheetUrl']



SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/spreadsheets']

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



def search_messages(service, search_query):
    """Searches for messages using the Gmail API and returns a list of message IDs"""
    try:
        query = "subject:" + search_query
        response = service.users().messages().list(userId='me', q=query).execute()
        messages = [ ]
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
            if 'messages' in response:
                messages.extend(response['messages'])

        return messages

    except HttpError as error:
        print(F'An error occurred: {error}')

if __name__ == '__main__':
    # Get the Gmail API service
    service = get_gmail_service()

    # Print the subject of each email

    sheet_name = 'Test Sheet'
    headers = ['Name', 'Age', 'Gender']
    data = [['Alice', 25, 'Female'], ['Bob', 30, 'Male'], ['Charlie', 35, 'Male']]

    sheet_url = create_and_write_to_sheet(sheet_name, headers, data)

    print(f"Sheet URL: {sheet_url}")


