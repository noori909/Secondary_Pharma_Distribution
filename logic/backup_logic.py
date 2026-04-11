import os
import glob
import shutil
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APP_DATA_DIR

def perform_automated_backup():
    """
    Safely copies pharma.db into a timestamped zip archive in the APP_DATA_DIR/backups directory,
    and cleans up old backups exceeding 30 days.
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
    shutil.make_archive(archive_name, 'zip', temp_dir)
    
    # Clean up temp isolation folder
    shutil.rmtree(temp_dir)
    
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
