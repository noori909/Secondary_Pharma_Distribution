import os
import glob
import shutil
import sys
import socket
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APP_DATA_DIR


def _has_internet():
    """Quick connectivity check — tries to reach Google DNS."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def perform_automated_backup():
    """
    Safely copies pharma.db into a timestamped zip archive in the APP_DATA_DIR/backups directory.
    If internet is available, also uploads to Google Drive and sends daily email report.
    Cleans up local backups exceeding 30 entries.
    """
    db_path = str(APP_DATA_DIR / "pharma.db")
    if not os.path.exists(db_path):
        return  # Nothing to backup

    backup_dir = str(APP_DATA_DIR / "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    temp_dir = os.path.join(backup_dir, f"temp_{timestamp}")
    os.makedirs(temp_dir, exist_ok=True)

    # Copy db into isolation folder for zip
    shutil.copy2(db_path, temp_dir)

    # Create zip archive
    archive_name = os.path.join(backup_dir, f"pharma_backup_{timestamp}")
    zip_path = shutil.make_archive(archive_name, 'zip', temp_dir)

    # Clean up temp isolation folder
    shutil.rmtree(temp_dir)

    # --- Cloud sync (only if internet available) ---
    if _has_internet():
        try:
            from services.gdrive_service import upload_backup_to_drive
            upload_backup_to_drive(zip_path)
        except Exception as e:
            print(f"Google Drive upload failed (non-critical): {e}")

        try:
            from services.email_service import send_daily_report
            send_daily_report()
        except Exception as e:
            print(f"Daily email failed (non-critical): {e}")
    else:
        print("No internet detected — skipping cloud sync and email.")

    # Manage rotation (keep last 30 backups)
    existing_backups = glob.glob(os.path.join(backup_dir, "pharma_backup_*.zip"))
    existing_backups.sort(key=os.path.getctime)

    # Delete oldest if exceeds 30
    if len(existing_backups) > 30:
        for old_backup in existing_backups[:-30]:
            try:
                os.remove(old_backup)
            except OSError:
                pass
