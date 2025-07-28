# EU4 Autobackup

![alt text](image.png)

A robust, user-friendly Python script to automatically back up your Europa Universalis IV (EU4) multiplayer autosave files. Designed for flexibility across different setups, with onboarding, auto-detection, and an interactive CLI menu.

## Features
- **Automatic backup** of `mp_autosave.eu4` at user-defined intervals
- **Auto-detects** common EU4 save locations and suggests paths
- **First-run setup wizard** for easy onboarding
- **Interactive settings menu** for configuration
- **Non-blocking controls**: 
  - `Ctrl+Q` to return to menu
  - `Ctrl+C` to exit
- **Backup retention**: keep all or only recent years
- **Colored, emoji-enhanced logs** for clarity

## Requirements
- Python 3.6+
- Windows (tested), should work on Linux/Mac with minor adjustments

## Installation
1. Download `eu4_autobackup.py` to any folder.
2. Open a terminal (PowerShell or CMD on Windows).
3. Run:
   ```sh
   python eu4_autobackup.py
   ```

## First Run
- The script will auto-detect your EU4 save locations and guide you through setup.
- Settings are saved in `eu4_autobackup.json` in the script's folder.

## Usage
- **Start the script**: `python eu4_autobackup.py`
- **Menu options**:
  - Show/update settings
  - Run setup wizard
  - Start/stop monitoring
  - Reset to defaults
- **During monitoring**:
  - `Ctrl+Q`: Return to menu
  - `Ctrl+C`: Exit script

## Settings
- **SOURCE**: Path to your `mp_autosave.eu4` file
- **BACKUP_DIR**: Where backups are stored (default: `backups` folder next to your save)
- **interval**: How often to check for changes (seconds)
- **keep_years**: How many in-game years of backups to keep (`all` = keep everything)

## Troubleshooting
- If the script can't find your save file, use the menu to set the correct path.
- Make sure you have permission to read/write in the backup directory.

## Notes
- Backups are named with the player tag and timestamp for easy identification.
- You'll see more information when selecting the save file ingame.
- The script is safe to run alongside EU4 multiplayer sessions.

## License
MIT License. See file for details.# 🎮 EU4 Autosave Backup Tool