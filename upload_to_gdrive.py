import os
import json
import io
import httplib2
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
    print("❌ Error: Missing one or more required environment variables.")
    # Exits the script with an error code
    exit(1) 

def upload_file_to_drive():
    """Authenticates and uploads a file to the specified Google Drive folder."""
    
    # 1. Setup Credentials
    print("🔑 Setting up Google Service Account credentials...")
    try:
        # Load credentials from JSON string
        creds_info = json.loads(SERVICE_ACCOUNT_JSON)
        
        # Define the scope for Google Drive access
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        # Create credentials object
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, SCOPES)
        
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return

    # 2. Build the Drive Service
    print("🔧 Building Google Drive Service...")
    # httplib2.Http() is required for this version of the library
    service = build('drive', 'v3', http=creds.authorize(httplib2.Http()))

    # 3. Check for Existing File (for overwrite logic)
    # Search for the file by name within the specific folder
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
            fields='files(id, name)'
        ).execute()
        
        items = results.get('files', [])
        
    except Exception as e:
        print(f"❌ Error searching for existing file: {e}")
        return

    file_metadata = {
        'name': UPLOAD_FILE_NAME,
        'parents': [FOLDER_ID]
    }
    
    # 4. Upload or Update the File
    try:
        media = MediaIoBaseUpload(io.FileIO(LOCAL_FILE_PATH, 'rb'),
                                  mimetype='text/csv',
                                  resumable=True)
                                  
        if items:
            # File exists, update it (overwrite)
            file_id = items[0]['id']
            print(f"🔄 File found (ID: {file_id}). Updating/Overwriting...")
            service.files().update(fileId=file_id, 
                                   body=file_metadata,
                                   media_body=media).execute()
            print(f"✅ Successfully updated file: {UPLOAD_FILE_NAME}")
        else:
            # File does not exist, upload new one
            print("⬆️ File not found. Uploading new file...")
            service.files().create(body=file_metadata,
                                   media_body=media,
                                   fields='id').execute()
            print(f"✅ Successfully uploaded new file: {UPLOAD_FILE_NAME}")

    except Exception as e:
        print(f"❌ Error during file upload/update: {e}")
        
if __name__ == '__main__':
    upload_file_to_drive()
