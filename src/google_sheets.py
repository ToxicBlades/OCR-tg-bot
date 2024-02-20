# -*- coding: utf-8 -*-
from google.oauth2.service_account import Credentials
import gspread
import traceback
import json

def get_google_sheets_client():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file('/opt/perspektiva-bot-py/data/credentials.json', scopes=scope)
    client = gspread.authorize(creds)
    return client


def write_to_google_sheets(json_data):
    try:
        # Open the Google Sheet by title
        gc = get_google_sheets_client()
        worksheet = gc.open('SES leads data').sheet1

        # Define the order of columns in Google Sheets

        data = json.loads(json_data)

        # Set default value for 'link' if not present in JSON data
        link_value = data.get('link', None)

        # Create a list of data to add to Google Sheets in the specified order
        row_data = [
            link_value,
            data.get('name', ''),
            data.get('email', ''),
            data.get('phone_number', '')
        ]

        # Add data to Google Sheets
        worksheet.append_row(row_data)

    except Exception as e:
        # Handle any exceptions
        print(f"An error occurred: {e}")
        traceback.print_exc()  # Prints detailed traceback of the exception

        # You might want to return False or some error message to indicate failure
        return False

