#!/usr/bin/env python3
"""
Backup Script for RPG DM Agent
Creates timestamped backups before making changes to critical files.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def create_backup(file_path, backup_dir="backups"):
    """
    Create a timestamped backup of a file.
    
    Args:
        file_path (str): Path to the file to backup
        backup_dir (str): Directory to store backups (default: "backups")
    
    Returns:
        str: Path to the created backup file
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist!")
        return None
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get filename and extension
    file_name = os.path.basename(file_path)
    name, ext = os.path.splitext(file_name)
    
    # Create backup filename
    backup_filename = f"{name}_backup_{timestamp}{ext}"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Copy file to backup location
    try:
        shutil.copy2(file_path, backup_path)
        print(f"SUCCESS: Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"ERROR: Error creating backup: {e}")
        return None

def backup_critical_files():
    """Backup all critical files in the project."""
    critical_files = [
        "streamlit_ui.py",
        "dm_agent.py", 
        "character_manager.py",
        "dice_roller.py",
        "journal_manager.py",
        "rule_engine.py",
        "main.py"
    ]
    
    print("Creating backups of critical files...")
    backups_created = []
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            backup_path = create_backup(file_path)
            if backup_path:
                backups_created.append(backup_path)
        else:
            print(f"WARNING: File {file_path} not found, skipping...")
    
    print(f"\nTotal backups created: {len(backups_created)}")
    return backups_created

if __name__ == "__main__":
    backup_critical_files()
