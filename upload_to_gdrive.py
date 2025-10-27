import os
import json
import csv
from googleapiclient.discovery import build
from google.oauth2 import service_account

# --- Configuration ---
# Environment variables set in GitHub Actions workflow
SHEET_ID = os.getenv('GDRIVE_SHEET_ID')
SERVICE_ACCOUNT_JSON = os.getenv('GDRIVE_SERVICE_ACCOUNT_JSON')
LOCAL_FILE_PATH = os.getenv('LOCAL_FILE_PATH')

# --- Main Logic ---

def upload_to_sheets():
    """
    Authenticates using the service account and uploads the CSV data
    to the specified Google Sheet using the Sheets API.
    """
    print("🔑 Setting up Google Service Account credentials...")
    try:
        # Load credentials from the environment variable string
        info = json.loads(SERVICE_ACCOUNT_JSON)
        credentials = service_account.Credentials.from_service_account_info(info)
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return

    print("🔧 Building Google Sheets Service...")
    # Sheets API service build
    service = build('sheets', 'v4', credentials=credentials)

    if not SHEET_ID:
        print("❌ FATAL Error: GDRIVE_SHEET_ID environment variable is missing.")
        return

    print(f"📄 Found local file: '{LOCAL_FILE_PATH}'")

    try:
        # 1. Read the CSV data
        with open(LOCAL_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            values = list(reader)

        if not values:
            print("⚠️ CSV file is empty. Skipping upload.")
            return

        # Determine the range for clearing and writing (e.g., A1:Z - assuming up to 26 columns)
        # We clear up to the maximum number of columns in the data to ensure cleanliness
        num_cols = len(values[0]) if values else 1
        # Dynamically determine the last column letter
        last_col = chr(ord('A') + num_cols - 1)
        range_to_clear = f"A1:{last_col}"
        range_to_write = f"A1" # Start writing from cell A1

        # 2. Clear the existing data in the sheet (best practice)
        print(f"🗑️ Clearing existing data in range {range_to_clear}...")
        
        # The range is defined as the whole sheet if no specific rows are given
        # We use batchUpdate for robustness in clearing all data/formatting
        requests = [
            {
                'updateCells': {
                    'range': {
                        'sheetId': 0 # SheetId 0 typically refers to the first sheet (Sheet1)
                    },
                    'fields': '*'
                }
            },
            {
                'updateSpreadsheetProperties': {
                    'properties': {
                        'title': os.getenv('UPLOAD_FILE_NAME').replace(".csv", "")
                    },
                    'fields': 'title'
                }
            }
        ]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={'requests': requests}
        ).execute()

        # 3. Write the new data
        print(f"📝 Writing new data starting at {range_to_write}...")
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=range_to_write,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        print(f"✅ Successfully uploaded data to Google Sheet!")
        print(f"📝 Cells updated: {result.get('updatedCells')}")

    except FileNotFoundError:
        print(f"❌ FATAL Error: File not found: '{LOCAL_FILE_PATH}'")
    except Exception as e:
        print(f"❌ FATAL Error during Sheets API operation: {e}")

if __name__ == '__main__':
    upload_to_sheets()
