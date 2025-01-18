import os
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth import SAMPLE_SPREADSHEET_ID, authenticate_google_sheets


def fetch_data_from_sheets(sheet_id, range_name):
    try:
        service = authenticate_google_sheets()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get("values", [])
        
        if not values:
            print("No data found.")
            return pd.DataFrame()
        
        headers = values[0]
        data = values[1:]
        return pd.DataFrame(data, columns=headers)
    
    except HttpError as err:
        print(f"An error occurred: {err}")
        return pd.DataFrame()

def main():
    SAMPLE_RANGE_NAME = "Form Responses 1!A2:K"
    
    df = fetch_data_from_sheets(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)
    
    print("Data fetched from Google Sheets:")
    print(df)

if __name__ == "__main__":
    main()
