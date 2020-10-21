import httplib2
import os, json
from base64 import b64decode

from googleapiclient import discovery
from google.oauth2 import service_account

scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
service_info = json.loads(b64decode(os.environ['GOOGLE_SERVICE_AUTH']))
credentials = service_account.Credentials.from_service_account_info(service_info, scopes=scopes)
service = discovery.build('sheets', 'v4', credentials=credentials)
gsheets = service.spreadsheets()

PRODUCTION_SPREADSHEET_ID = os.environ['PRODUCTION_SPREADSHEET_ID']
MAIN_SHEET_NAME = os.environ['MAIN_SHEET_NAME'] 

def get_sheet_values(spreadsheet_id=PRODUCTION_SPREADSHEET_ID, sheet_name=MAIN_SHEET_NAME, limit=''):
    get_range = "%s!A1:M%s" % (sheet_name, limit)
    request = gsheets.values().get(spreadsheetId=spreadsheet_id, range=get_range)
    response = request.execute()
    if 'values' not in response:
        return []

    keys = response['values'][0]

    rows = []
    for row in response['values'][1:]:
        batch = {}
        for idx, value in enumerate(row):
            batch[keys[idx]] = value
        rows.append(batch)
    return rows
