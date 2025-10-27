import os
import json
import io
import httplib2
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials

# --- Configuration from Environment Variables ---
# The Service Account JSON is passed as an environment variable (secret)
SERVICE_ACCOUNT_JSON = os.environ.get('GDRIVE_SERVICE_ACCOUNT_JSON')
FOLDER_ID = os.environ.get('GDRIVE_FOLDER_ID')
LOCAL_FILE_PATH = os.environ.get('LOCAL_FILE_PATH')
UPLOAD_FILE_NAME = os.environ.get('UPLOAD_FILE_NAME') # This MUST now be unique per run

if not all([SERVICE_ACCOUNT_JSON, FOLDER_ID, LOCAL_FILE_PATH, UPLOAD_FILE_NAME]):
    print("❌ Error: Missing one or more required environment variables (GDRIVE_SERVICE_ACCOUNT_JSON, GDRIVE_FOLDER_ID, LOCAL_FILE_PATH, or UPLOAD_FILE_NAME).", file=sys.stderr)
    sys.exit(1)

def upload_file_to_drive():
    """Authenticates and uploads a file to the specified Google Drive folder."""
    
    # 1. CRITICAL: Check if the file exists before attempting to open it
    if not os.path.exists(LOCAL_FILE_PATH):
        print(f"❌ FATAL: Local file not found at path: '{LOCAL_FILE_PATH}'", file=sys.stderr)
        print("This means the scraping script failed to create the file or saved it in the wrong location.", file=sys.stderr)
        sys.exit(1)
        
    print(f"📄 Found local file: '{LOCAL_FILE_PATH}' (Size: {os.path.getsize(LOCAL_FILE_PATH)} bytes)")

    # 2. Setup Credentials
    print("🔑 Setting up Google Service Account credentials...")
    try:
        # Load credentials from JSON string
        creds_info = json.loads(SERVICE_ACCOUNT_JSON)
        
        # Define the scope for Google Drive access
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        # Create credentials object
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, SCOPES)
        
    except Exception as e:
        print(f"❌ Error loading credentials. Check your GDRIVE_SERVICE_ACCOUNT_CREDENTIALS secret formatting. Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Build the Drive Service
    print("🔧 Building Google Drive Service...")
    # httplib2.Http() is required for this version of the library
    service = build('drive', 'v3', http=creds.authorize(httplib2.Http()))

    # Metadata for a NEW file creation - Note the mimeType change!
    new_file_metadata = {
        'name': UPLOAD_FILE_NAME,
        'parents': [FOLDER_ID],
        # CRITICAL FIX: Tell Drive to create a Google Sheet (application/vnd.google-apps.spreadsheet)
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    
    # 4. Upload New File (Always)
    print(f"⬆️ Uploading new file with unique name: {UPLOAD_FILE_NAME}...")
    try:
        # Create Media Object for upload (CSV data)
        media = MediaIoBaseUpload(io.FileIO(LOCAL_FILE_PATH, 'rb'),
                                  mimetype='text/csv', # The data being uploaded is CSV
                                  resumable=True)
                                  
        # This creation step uses the new_file_metadata (Google Sheet MIME-type)
        service.files().create(body=new_file_metadata,
                               media_body=media,
                               fields='id',
                               supportsAllDrives=True).execute()
                               
        print(f"✅ Successfully uploaded new file (as Google Sheet): {UPLOAD_FILE_NAME}")

    except Exception as e:
        print(f"❌ FATAL Error during file upload/update (Permissions/Folder ID issue likely): {e}", file=sys.stderr)
        # Re-raise error to show detailed message
        sys.exit(1)
        
if __name__ == '__main__':
    upload_file_to_drive()



-
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
        range_to_clear = f"A1:{chr(ord('A') + num_cols - 1)}"
        range_to_write = f"A1" # Start writing from cell A1

        # 2. Clear the existing data in the sheet (best practice)
        print(f"🗑️ Clearing existing data in range {range_to_clear}...")
        clear_values_request = {'range': range_to_clear}
        service.spreadsheets().values().clear(
            spreadsheetId=SHEET_ID,
            range=range_to_clear,
            body=clear_values_request
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
