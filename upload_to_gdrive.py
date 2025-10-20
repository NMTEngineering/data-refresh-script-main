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
UPLOAD_FILE_NAME = os.environ.get('UPLOAD_FILE_NAME')

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

    # 4. Check for Existing File (for overwrite logic)
    # The query filters by name, parent folder, and excludes trash/folders
    query = (
        f"name = '{UPLOAD_FILE_NAME}' and "
        f"'{FOLDER_ID}' in parents and "
        "mimeType != 'application/vnd.google-apps.folder' and "
        "trashed = false"
    )
    
    try:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType)',
            supportsAllDrives=True 
        ).execute()
        
        items = results.get('files', [])
        
    except Exception as e:
        print(f"❌ Error searching for existing file on Drive: {e}", file=sys.stderr)
        sys.exit(1)

    # Metadata for a NEW file creation - Note the mimeType change!
    new_file_metadata = {
        'name': UPLOAD_FILE_NAME,
        'parents': [FOLDER_ID],
        # CRITICAL FIX: Tell Drive to create a Google Sheet (application/vnd.google-apps.spreadsheet)
        # This converts the CSV and bypasses the quota error.
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    
    # 5. Upload or Update the File
    try:
        # Create Media Object for upload (CSV data)
        media = MediaIoBaseUpload(io.FileIO(LOCAL_FILE_PATH, 'rb'),
                                  mimetype='text/csv', # The data being uploaded is CSV
                                  resumable=True)
                                  
        if items:
            # File exists, update it (overwrite)
            file_id = items[0]['id']
            # If the existing file is a CSV, we update it as a CSV. If it's a Sheet, we update it as a Sheet.
            # We rely on the existing file's mimeType to maintain its format.
            is_google_sheet = items[0].get('mimeType') == 'application/vnd.google-apps.spreadsheet'

            print(f"🔄 File found on Drive (ID: {file_id}). Updating/Overwriting...")
            
            # When updating an existing file, we must use the correct target mimeType in the metadata
            # to trigger the conversion if it's a Sheet, or just update if it's a raw CSV.
            update_metadata = {}
            if is_google_sheet:
                # If overwriting a sheet, we must tell it to import the CSV data
                update_metadata['mimeType'] = 'application/vnd.google-apps.spreadsheet'
            
            # Update only media body and use supportsAllDrives
            service.files().update(fileId=file_id, 
                                   body=update_metadata, # Pass the metadata body if converting
                                   media_body=media,
                                   supportsAllDrives=True).execute()
                                   
            print(f"✅ Successfully updated file: {UPLOAD_FILE_NAME}")
        else:
            # File does not exist, upload new one
            print("⬆️ File not found on Drive. Uploading new file...")
            
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
