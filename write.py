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


# Define the scopes that the application will need

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/spreadsheets']

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
    service = build('sheets', 'v1', credentials=creds)
    return service


if __name__ == '__main__':
    # Create a new Google Sheet
    sheets_service = get_gmail_service()
    sheet_title = 'My Test Sheet'
    sheet = sheets_service.spreadsheets().create(
        body={
            'properties': {'title': sheet_title},
            'sheets': [{'properties': {'title': 'Sheet 1'}}],
        }
    ).execute()
    sheet_id = sheet['spreadsheetId']
    print(f'Created new sheet with title "{sheet_title}" and ID "{sheet_id}"')

    # Write some test data to the sheet
    data = [
        ['Name', 'Age', 'Gender'],
        ['Alice', 25, 'Female'],
        ['Bob', 30, 'Male'],
        ['Charlie', 35, 'Male'],
    ]
    range_name = 'Sheet 1!A1:C4'
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