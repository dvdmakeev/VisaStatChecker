import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


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
