"""
Auto-archive old reports (>30 days)
"""

import os
import shutil
from datetime import datetime, timedelta

def archive_old_reports(days_threshold=30):
    """
    Archive reports older than threshold
    
    Args:
        days_threshold: Days after which reports are archived (default: 30)
    
    Returns:
        Number of reports archived
    """
    
    cutoff = datetime.now() - timedelta(days=days_threshold)
    archived_count = 0
    
    for folder in ['daily', 'weekly', 'monthly']:
        folder_path = os.path.join('reports', folder)
        if not os.path.exists(folder_path):
            continue
        
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            
            if not os.path.isfile(filepath):
                continue
            
            # Check file age
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if mtime < cutoff:
                # Move to archives
                archive_path = os.path.join('reports', 'archives', filename)
                shutil.move(filepath, archive_path)
                archived_count += 1
                print(f"[ARCHIVE] Moved {filename} to archives")
    
    print(f"[ARCHIVE] Archived {archived_count} old reports")
    return archived_count


if __name__ == '__main__':
    # Test archiving
    count = archive_old_reports(30)
    print(f"Archived {count} reports")
