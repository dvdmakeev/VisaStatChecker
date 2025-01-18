import os
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


TOKEN_FILENAME = "token.json"


CREDENTIALS_FILENAME = "credentials.json"


SAMPLE_SPREADSHEET_ID = "18jFotI0lwie-8p-eU9rjtcVrtsO5GldMbVoyo-Y5EYY"


def authenticate_google_sheets():
    creds = None

    if os.path.exists(TOKEN_FILENAME):
        creds = Credentials.from_authorized_user_file(TOKEN_FILENAME, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILENAME,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_FILENAME, "w") as token:
            token.write(creds.to_json())
    
    service = build("sheets", "v4", credentials=creds)
    return service

def fetch_data_from_sheets(sheet_id, range_name):
    try:
        # Authenticate and fetch data
        service = authenticate_google_sheets()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get("values", [])
        
        if not values:
            print("No data found.")
            return pd.DataFrame()  # Return an empty DataFrame if no data
        
        # Convert data to a Pandas DataFrame
        headers = values[0]  # First row is considered headers
        data = values[1:]    # Remaining rows are data
        return pd.DataFrame(data, columns=headers)
    
    except HttpError as err:
        print(f"An error occurred: {err}")
        return pd.DataFrame()

def main():
    SAMPLE_RANGE_NAME = "Form Responses 1!A2:K"
    
    # Fetch data from the sheet
    df = fetch_data_from_sheets(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)
    print("Data fetched from Google Sheets:")
    print(df)

if __name__ == "__main__":
    main()