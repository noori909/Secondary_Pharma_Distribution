import os
import sys
from pathlib import Path

from config import APP_DATA_DIR

SCOPES     = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID  = '1nhTrn6ft6Np-kJhBUWK4NFgnGdC1rPjU'
TOKEN_FILE  = 'gdrive_token.json'   # Saved after first authorisation — lives in AppData


def _client_file_path() -> Path:
    """
    Locate PharmaDesktopClient.json whether we're running from:
      - The raw source directory (development / python main.py)
      - An unpacked PyInstaller EXE (_MEIPASS is the temp bundle directory)
    """
    # PyInstaller bundles data files into sys._MEIPASS at runtime
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
    return base / 'PharmaDesktopClient.json'


def _get_credentials():
    """
    Return valid OAuth credentials.
    - First run  : opens a browser for one-time approval, saves token to AppData.
    - Later runs : loads saved token silently; auto-refreshes if expired.
    """
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    token_path  = APP_DATA_DIR / TOKEN_FILE
    client_path = _client_file_path()

    creds = None

    # Load existing token if present
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # Refresh expired token, or run first-time browser flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not client_path.exists():
                print(f"[GDrive] OAuth client file not found at: {client_path}")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(str(client_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Persist token for all future runs
        token_path.write_text(creds.to_json())
        print(f"[GDrive] Token saved to {token_path}")

    return creds


def upload_backup_to_drive(zip_path: str) -> bool:
    """Upload a zip file to the designated Google Drive backup folder."""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        creds = _get_credentials()
        if creds is None:
            return False

        service  = build('drive', 'v3', credentials=creds)
        metadata = {'name': os.path.basename(zip_path), 'parents': [FOLDER_ID]}
        media    = MediaFileUpload(zip_path, mimetype='application/zip', resumable=True)

        uploaded = service.files().create(
            body=metadata, media_body=media, fields='id,name'
        ).execute()

        print(f"[GDrive] Uploaded: {uploaded.get('name')} (id={uploaded.get('id')})")
        return True

    except Exception as e:
        print(f"[GDrive] Upload failed: {e}")
        return False
