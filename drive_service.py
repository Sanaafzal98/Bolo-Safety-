"""
Google Drive service using a Service Account.
Set GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_DRIVE_FOLDER_ID in .env.

If not configured, upload_audio() safely returns (None, None) so the rest
of the app keeps working (audio just stays saved locally in /uploads).
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

_drive = None


def _get_drive_client():
    global _drive
    if _drive is not None:
        return _drive

    cred_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not cred_file or not os.path.exists(cred_file):
        return None

    creds = service_account.Credentials.from_service_account_file(cred_file, scopes=SCOPES)
    _drive = build("drive", "v3", credentials=creds)
    return _drive


def upload_audio(local_path: str, filename: str):
    """
    Uploads a local audio file to the configured Drive folder.
    Returns (drive_file_id, drive_view_link) or (None, None) if Drive isn't configured.
    """
    drive = _get_drive_client()
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

    if drive is None or not folder_id:
        return None, None

    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(local_path, resumable=True)

    uploaded = drive.files().create(
        body=file_metadata, media_body=media, fields="id, webViewLink"
    ).execute()

    # make it viewable by anyone with the link (optional - remove if you want it private)
    try:
        drive.permissions().create(
            fileId=uploaded["id"], body={"type": "anyone", "role": "reader"}
        ).execute()
    except Exception:
        pass

    return uploaded.get("id"), uploaded.get("webViewLink")


def delete_audio(drive_file_id: str):
    drive = _get_drive_client()
    if drive is None or not drive_file_id:
        return False
    try:
        drive.files().delete(fileId=drive_file_id).execute()
        return True
    except Exception:
        return False
