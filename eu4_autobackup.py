import os
import time
import shutil
import json

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eu4_autobackup.json')

def detect_eu4_save_paths():
    """Auto-detect common EU4 save game locations."""
    possible_paths = []
    
    # Get user's home directory
    user_home = os.path.expanduser("~")
    
    # Common save game locations
    common_locations = [
        os.path.join(user_home, "Documents", "Paradox Interactive", "Europa Universalis IV", "save games"),
        os.path.join("C:", os.sep, "Users", os.getenv("USERNAME", ""), "Documents", "Paradox Interactive", "Europa Universalis IV", "save games"),
        os.path.join("D:", os.sep, "Documents", "Paradox Interactive", "Europa Universalis IV", "save games"),
        os.path.join("C:", os.sep, "Documents", "Paradox Interactive", "Europa Universalis IV", "save games"),
    ]
    
    # Check each possible location
    for path in common_locations:
        if os.path.exists(path):
            possible_paths.append(path)
    
    return possible_paths

def detect_autosave_file():
    """Find the mp_autosave.eu4 file in detected save locations."""
    save_paths = detect_eu4_save_paths()
    
    for save_dir in save_paths:
        autosave_path = os.path.join(save_dir, "mp_autosave.eu4")
        if os.path.exists(autosave_path):
            return autosave_path
    
    return None

def get_detected_paths():
    """Get detected paths for EU4 installation."""
    detected_autosave = detect_autosave_file()
    detected_save_dirs = detect_eu4_save_paths()
    
    if detected_autosave:
        source_file = detected_autosave
        # Always use the directory containing the autosave file + "backups" subfolder
        backup_dir = os.path.join(os.path.dirname(detected_autosave), "backups")
    elif detected_save_dirs:
        # Use first detected save directory
        source_file = os.path.join(detected_save_dirs[0], "mp_autosave.eu4")
        backup_dir = os.path.join(detected_save_dirs[0], "backups")
    else:
        # Fallback to user's Documents folder
        user_home = os.path.expanduser("~")
        eu4_dir = os.path.join(user_home, "Documents", "Paradox Interactive", "Europa Universalis IV", "save games")
        source_file = os.path.join(eu4_dir, "mp_autosave.eu4")
        backup_dir = os.path.join(eu4_dir, "backups")
    
    # Double-check: ensure backup_dir is never the same as source_file
    if backup_dir == source_file or backup_dir.endswith('.eu4'):
        backup_dir = os.path.join(os.path.dirname(source_file), "backups")
    
    return source_file, backup_dir

# Auto-detect paths for default settings
default_source, default_backup = get_detected_paths()

# Default settings with auto-detected paths
DEFAULT_SETTINGS = {
    'SOURCE': default_source,
    'BACKUP_DIR': default_backup,
    'interval': 60.0,
    'keep_years': 'all'
}

def load_settings():
    """Read settings from the JSON file or use defaults."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Validate and fix backup directory if it's pointing to a file
                if settings.get('BACKUP_DIR') and settings.get('SOURCE'):
                    backup_dir = settings['BACKUP_DIR']
                    source_file = settings['SOURCE']
                    
                    # Fix if backup dir is the same as source file or ends with .eu4
                    if backup_dir == source_file or backup_dir.endswith('.eu4'):
                        log("Fixing incorrect backup directory setting...", color='yellow', emoji='🔧')
                        settings['BACKUP_DIR'] = os.path.join(os.path.dirname(source_file), "backups")
                        save_settings(settings)
                        log(f"Updated backup directory to: {settings['BACKUP_DIR']}", color='green', emoji='✅')
                
                return settings
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Write settings to the JSON file."""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)

def update_setting(settings, key, value):
    """Update a setting and save."""
    settings[key] = value
    save_settings(settings)

def delete_setting(settings, key):
    """Delete a setting and save."""
    if key in settings:
        del settings[key]
        save_settings(settings)

def log(msg, color=None, emoji=None):
    # Print a timestamped, colored, emoji-enhanced log message
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'red': '\033[91m',  # Add red color
        'reset': '\033[0m',
    }
    prefix = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
    emoji_str = f"{emoji} " if emoji else ""
    color_code = colors.get(color, '')
    reset_code = colors['reset'] if color else ''
    print(f"{color_code}{prefix}{emoji_str}{msg}{reset_code}")

# Print all current settings to the console
def show_settings(settings):
    """Print current settings with descriptions."""
    print("\n" + "="*50)
    print("  📋 CURRENT SETTINGS")
    print("="*50)
    
    # Format settings with descriptions
    setting_descriptions = {
        'SOURCE': 'EU4 autosave file location',
        'BACKUP_DIR': 'Backup directory location',
        'interval': 'Check interval (seconds)',
        'keep_years': 'Backup retention (years or "all")'
    }
    
    for key, value in settings.items():
        desc = setting_descriptions.get(key, 'Custom setting')
        print(f"  {key.ljust(12)}: {str(value).ljust(40)} # {desc}")
    
    # Show file existence status
    print("\n📁 FILE STATUS:")
    source_exists = "✅ EXISTS" if os.path.exists(settings.get('SOURCE', '')) else "❌ NOT FOUND"
    backup_exists = "✅ EXISTS" if os.path.exists(settings.get('BACKUP_DIR', '')) else "❌ NOT FOUND"
    print(f"  Source file   : {source_exists}")
    print(f"  Backup dir    : {backup_exists}")
    print("="*50)


def validate_path_input(prompt, current_value, is_file=True):
    """Get and validate file/directory path input with smart suggestions."""
    while True:
        print(f"\nCurrent: {current_value}")
        
        # Show suggestions for EU4 paths
        if 'autosave' in prompt.lower() or 'source' in prompt.lower():
            detected_paths = detect_eu4_save_paths()
            if detected_paths:
                print("💡 Detected EU4 save directories:")
                for i, path in enumerate(detected_paths[:3], 1):  # Show up to 3
                    autosave_path = os.path.join(path, "mp_autosave.eu4")
                    status = "✅" if os.path.exists(autosave_path) else "📁"
                    print(f"    {i}. {status} {autosave_path}")
        
        value = input(f"{prompt} (Enter to keep current, number to select above, 'search' to find files): ").strip()
        
        if value == '':
            return current_value
        elif value.isdigit() and 'autosave' in prompt.lower():
            # User selected a numbered option
            try:
                detected_paths = detect_eu4_save_paths()
                selected_idx = int(value) - 1
                if 0 <= selected_idx < len(detected_paths):
                    selected_path = os.path.join(detected_paths[selected_idx], "mp_autosave.eu4")
                    return selected_path
                else:
                    log("Invalid selection number", color='red', emoji='❌')
                    continue
            except:
                pass
        elif value.lower() == 'search':
            log("Searching for EU4 files...", color='blue', emoji='🔍')
            detected_autosave = detect_autosave_file()
            if detected_autosave:
                log(f"Found: {detected_autosave}", color='green', emoji='✅')
                use_found = input("Use this file? (y/n): ").strip().lower()
                if use_found == 'y':
                    return detected_autosave
            else:
                log("No autosave file found in common locations", color='yellow', emoji='⚠️')
            continue
        
        # Expand user directory shortcuts
        value = os.path.expanduser(value)
        
        if is_file:
            if os.path.exists(value) and os.path.isfile(value):
                return value
            elif os.path.exists(os.path.dirname(value)):
                confirm = input(f"File doesn't exist yet. Use this path anyway? (y/n): ").strip().lower()
                if confirm == 'y':
                    return value
            else:
                log("Invalid file path or directory doesn't exist.", color='red', emoji='❌')
                # Show common EU4 locations as hints
                if 'eu4' in prompt.lower() or 'europa' in prompt.lower():
                    log("💡 Try checking these common locations:", color='blue', emoji='💡')
                    user_home = os.path.expanduser("~")
                    hints = [
                        os.path.join(user_home, "Documents", "Paradox Interactive", "Europa Universalis IV", "save games"),
                        "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Europa Universalis IV"
                    ]
                    for hint in hints:
                        print(f"     📂 {hint}")
        else:
            if os.path.exists(value) and os.path.isdir(value):
                return value
            else:
                create = input(f"Directory doesn't exist. Create it? (y/n): ").strip().lower()
                if create == 'y':
                    try:
                        os.makedirs(value, exist_ok=True)
                        return value
                    except Exception as e:
                        log(f"Failed to create directory: {e}", color='red', emoji='❌')
                else:
                    log("Invalid directory path.", color='red', emoji='❌')

def first_run_setup():
    """Guide users through initial setup with auto-detection."""
    print("\n" + "="*60)
    print("  🎮 WELCOME TO EU4 AUTOBACKUP - FIRST TIME SETUP")
    print("="*60)
    print("  Let's configure your EU4 backup settings!")
    print("  We'll try to auto-detect your EU4 installation...\n")
    
    # Auto-detect and show results
    detected_save_dirs = detect_eu4_save_paths()
    detected_autosave = detect_autosave_file()
    
    if detected_autosave:
        log(f"✅ Found EU4 autosave file: {detected_autosave}", color='green', emoji='🎯')
        source_file = detected_autosave
    elif detected_save_dirs:
        log(f"✅ Found EU4 save directory: {detected_save_dirs[0]}", color='green', emoji='📁')
        source_file = os.path.join(detected_save_dirs[0], "mp_autosave.eu4")
        log(f"⚠️  Autosave file not found, will use: {source_file}", color='yellow', emoji='⚠️')
    else:
        log("❌ Could not auto-detect EU4 installation", color='red', emoji='❌')
        log("💡 Common locations to check:", color='blue', emoji='💡')
        user_home = os.path.expanduser("~")
        suggestions = [
            os.path.join(user_home, "Documents", "Paradox Interactive", "Europa Universalis IV", "save games"),
            "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Europa Universalis IV",
            "C:\\Program Files\\Epic Games\\Europa Universalis IV"
        ]
        for suggestion in suggestions:
            print(f"     📂 {suggestion}")
        
        source_file = DEFAULT_SETTINGS['SOURCE']
    
    # Setup source file
    print(f"\n🔧 STEP 1: EU4 Autosave File Location")
    print("-" * 40)
    final_source = validate_path_input(
        "Enter path to your mp_autosave.eu4 file",
        source_file,
        is_file=True
    )
    
    # Setup backup directory
    print(f"\n🔧 STEP 2: Backup Directory")
    print("-" * 40)
    suggested_backup = os.path.join(os.path.dirname(final_source), "backups")
    print(f"Suggested: {suggested_backup}")
    final_backup = validate_path_input(
        "Enter backup directory path",
        suggested_backup,
        is_file=False
    )
    
    # Setup monitoring interval
    print(f"\n🔧 STEP 3: Monitoring Settings")
    print("-" * 40)
    print("How often should we check for save file changes?")
    print("  • 30 seconds (frequent)")
    print("  • 60 seconds (recommended)")
    print("  • 300 seconds (5 minutes)")
    while True:
        interval_input = input("Enter interval in seconds [60]: ").strip()
        if interval_input == '':
            interval = 60.0
            break
        try:
            interval = float(interval_input)
            if interval < 5:
                log("Minimum 5 seconds recommended", color='yellow', emoji='⚠️')
                continue
            break
        except ValueError:
            log("Please enter a valid number", color='red', emoji='❌')
    
    # Create settings
    settings = {
        'SOURCE': final_source,
        'BACKUP_DIR': final_backup,
        'interval': interval,
        'keep_years': 'all'
    }
    
    # Save settings
    save_settings(settings)
    
    print(f"\n✅ Setup complete! Settings saved to:")
    print(f"    {SETTINGS_FILE}")
    print(f"\n📋 Your configuration:")
    show_settings(settings)
    
    input("\nPress Enter to continue to the main menu...")
    return settings

def validate_interval_input(current_value):
    """Get and validate interval input."""
    while True:
        print(f"\nCurrent interval: {current_value} seconds")
        print("Suggestions: 30 (30s), 60 (1min), 300 (5min), 600 (10min)")
        value = input("Enter new interval in seconds (Enter to keep current): ").strip()
        
        if value == '':
            return current_value
        
        try:
            interval = float(value)
            if interval < 5:
                log("Interval too short. Minimum 5 seconds recommended.", color='yellow', emoji='⚠️')
                continue
            elif interval > 3600:
                confirm = input("Interval over 1 hour. Continue? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            return interval
        except ValueError:
            log("Please enter a valid number.", color='red', emoji='❌')

def validate_keep_years_input(current_value):
    """Get and validate keep_years input."""
    while True:
        print(f"\nCurrent setting: {current_value}")
        print("Options:")
        print("  'all'  - Keep all backups (no cleanup)")
        print("  Number - Years of backups to keep (e.g., 50 keeps last 50 in-game years)")
        value = input("Enter new value (Enter to keep current): ").strip()
        
        if value == '':
            return current_value
        elif value.lower() == 'all':
            return 'all'
        else:
            try:
                years = int(value)
                if years < 1:
                    log("Years must be positive.", color='red', emoji='❌')
                    continue
                elif years < 10:
                    confirm = input(f"Only keeping {years} years of backups. Continue? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                return years
            except ValueError:
                log("Please enter 'all' or a number.", color='red', emoji='❌')


def settings_menu(settings):
    """Enhanced interactive CLI for settings management."""
    while True:
        print("\n" + "="*50)
        print("  🎮 EU4 AUTOBACKUP - SETTINGS")
        print("="*50)
        print("  1. 📋 Show current settings")
        print("  2. 📁 Update source file path")
        print("  3. 🗂️ Update backup directory")
        print("  4. ⏱️ Update check interval")
        print("  5. 🗑️ Update backup retention")
        print("  6. 🔧 Run setup wizard (auto-detect & configure)")
        print("  7. 🔄 Reset to defaults")
        print("  8. 🚀 Start backup monitoring")
        print("  0. 👋 Exit")
        print("-"*50)
        
        choice = input("Select option (0-8): ").strip()
        
        if choice == '1':
            show_settings(settings)
            
        elif choice == '2':
            new_value = validate_path_input(
                "Enter EU4 autosave file path",
                settings.get('SOURCE', DEFAULT_SETTINGS['SOURCE']),
                is_file=True
            )
            update_setting(settings, 'SOURCE', new_value)
            
            # Auto-suggest backup directory based on new source file
            current_backup = settings.get('BACKUP_DIR', '')
            suggested_backup = os.path.join(os.path.dirname(new_value), "backups")
            
            if current_backup != suggested_backup:
                print(f"\n💡 Suggested backup directory: {suggested_backup}")
                update_backup = input("Update backup directory to match? (y/n): ").strip().lower()
                if update_backup == 'y':
                    update_setting(settings, 'BACKUP_DIR', suggested_backup)
                    log("Backup directory updated automatically!", color='green', emoji='✅')
            
            log("Source file path updated!", color='green', emoji='✅')
            
        elif choice == '3':
            new_value = validate_path_input(
                "Enter backup directory path",
                settings.get('BACKUP_DIR', DEFAULT_SETTINGS['BACKUP_DIR']),
                is_file=False
            )
            update_setting(settings, 'BACKUP_DIR', new_value)
            log("Backup directory updated!", color='green', emoji='✅')
            
        elif choice == '4':
            new_value = validate_interval_input(settings.get('interval', DEFAULT_SETTINGS['interval']))
            update_setting(settings, 'interval', new_value)
            log("Check interval updated!", color='green', emoji='✅')
            
        elif choice == '5':
            new_value = validate_keep_years_input(settings.get('keep_years', DEFAULT_SETTINGS['keep_years']))
            update_setting(settings, 'keep_years', new_value)
            log("Backup retention updated!", color='green', emoji='✅')
            
        elif choice == '6':
            print("\n🔧 Running setup wizard with auto-detection...")
            
            # First try quick auto-detection
            detected_autosave = detect_autosave_file()
            detected_dirs = detect_eu4_save_paths()
            
            if detected_autosave:
                log(f"✅ Found autosave: {detected_autosave}", color='green', emoji='🎯')
                print("\nQuick setup options:")
                print("  1. 🚀 Use detected paths automatically")
                print("  2. 🔧 Run full setup wizard")
                print("  3. ↩️  Cancel and return to menu")
                
                quick_choice = input("Choose option (1-3): ").strip()
                if quick_choice == '1':
                    update_setting(settings, 'SOURCE', detected_autosave)
                    backup_dir = os.path.join(os.path.dirname(detected_autosave), "backups")
                    update_setting(settings, 'BACKUP_DIR', backup_dir)
                    log("Paths updated automatically!", color='green', emoji='✅')
                elif quick_choice == '2':
                    new_settings = first_run_setup()
                    settings.clear()
                    settings.update(new_settings)
                # Option 3 or invalid input just continues to menu
            elif detected_dirs:
                log(f"✅ Found save directories, running full setup wizard...", color='green', emoji='📁')
                new_settings = first_run_setup()
                settings.clear()
                settings.update(new_settings)
            else:
                log("❌ No EU4 installation detected, running manual setup wizard...", color='yellow', emoji='⚠️')
                new_settings = first_run_setup()
                settings.clear()
                settings.update(new_settings)
                
        elif choice == '7':
            print("\n⚠️  This will reset ALL settings to defaults!")
            confirm = input("Are you sure? Type 'yes' to confirm: ").strip().lower()
            if confirm == 'yes':
                settings.clear()
                settings.update(DEFAULT_SETTINGS)
                save_settings(settings)
                log("Settings reset to defaults!", color='blue', emoji='🔄')
            else:
                log("Reset cancelled.", color='yellow', emoji='↩️')
                
        elif choice == '8':
            # Quick validation before starting
            source = settings.get('SOURCE')
            backup_dir = settings.get('BACKUP_DIR')
            
            if not source or not os.path.exists(source):
                log("❌ Source file not found! Please update the source file path.", color='red', emoji='❌')
                continue
                
            if not backup_dir:
                log("❌ Backup directory not set! Please update the backup directory.", color='red', emoji='❌')
                continue
                
            # Try to create backup directory if it doesn't exist
            if not os.path.exists(backup_dir):
                try:
                    os.makedirs(backup_dir, exist_ok=True)
                    log(f"Created backup directory: {backup_dir}", color='green', emoji='✅')
                except Exception as e:
                    log(f"❌ Cannot create backup directory: {e}", color='red', emoji='❌')
                    continue
            
            log("Starting backup monitoring...", color='blue', emoji='🚀')
            break
                
        elif choice == '0':
            log("Goodbye!", color='blue', emoji='👋')
            exit(0)
            
        else:
            log("Invalid choice. Please select 0-8.", color='yellow', emoji='⚠️')

def get_mtime(path):
    """Return the last modification time of a file, or None if not found."""
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return None

def get_player_tag(save_path):
    """Extract the player country tag from the EU4 save file."""
    try:
        # Try reading as binary first, then decode what we can
        with open(save_path, 'rb') as f:
            content = f.read()
            # Convert to string, ignoring errors
            text_content = content.decode('utf-8', errors='ignore')
            
            # Look for player= line
            for line in text_content.split('\n'):
                if line.strip().startswith('player='):
                    tag = line.split('=')[1].strip().strip('"')
                    if tag and tag != '---':  # EU4 sometimes uses --- for no player
                        return tag
                    
        # If binary approach didn't work, try UTF-8 with error handling
        with open(save_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('player='):
                    tag = line.split('=')[1].strip().strip('"')
                    if tag and tag != '---':
                        return tag
                        
    except Exception as e:
        log(f"Warning: Could not extract player tag: {e}", color='yellow', emoji='⚠️')
        pass
    return 'UNKNOWN'

def get_save_year(save_path):
    """Extract the in-game year from the EU4 save file (date=YYYY.M.D)."""
    try:
        # Try reading as binary first, then decode what we can
        with open(save_path, 'rb') as f:
            content = f.read()
            text_content = content.decode('utf-8', errors='ignore')
            
            for line in text_content.split('\n'):
                if line.strip().startswith('date='):
                    date_str = line.split('=')[1].strip().strip('"')
                    year = int(date_str.split('.')[0])
                    return year
                    
        # Fallback to UTF-8 with error handling
        with open(save_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('date='):
                    date_str = line.split('=')[1].strip().strip('"')
                    year = int(date_str.split('.')[0])
                    return year
    except Exception:
        pass
    return None

def get_backup_year(filename):
    """Extract the in-game year from a backup filename (if present)."""
    try:
        # Try reading as binary first, then decode what we can
        with open(filename, 'rb') as f:
            content = f.read()
            text_content = content.decode('utf-8', errors='ignore')
            
            for line in text_content.split('\n'):
                if line.strip().startswith('date='):
                    date_str = line.split('=')[1].strip().strip('"')
                    year = int(date_str.split('.')[0])
                    return year
                    
        # Fallback to UTF-8 with error handling
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('date='):
                    date_str = line.split('=')[1].strip().strip('"')
                    year = int(date_str.split('.')[0])
                    return year
    except Exception:
        pass
    return None

def cleanup_old_backups(backup_dir, current_year, keep_years):
    """Delete backups older than current_year - keep_years. If keep_years is 'all', keep all backups."""
    if keep_years == 'all':
        return
    try:
        keep_years = int(keep_years)
    except (TypeError, ValueError):
        return
    for fname in os.listdir(backup_dir):
        if fname.endswith('.eu4'):
            fpath = os.path.join(backup_dir, fname)
            backup_year = get_backup_year(fpath)
            if backup_year is not None and backup_year < current_year - keep_years:
                try:
                    os.remove(fpath)
                    log(f"🗑️  Cleaned up old backup: {fname} (Year {backup_year})", color='red', emoji='🧹')
                except Exception:
                    pass

# Load settings and initialize
settings = load_settings()

# Check if this is a first run or if paths are invalid
is_first_run = not os.path.exists(SETTINGS_FILE)
source_invalid = not os.path.exists(settings.get('SOURCE', ''))
backup_invalid = not settings.get('BACKUP_DIR')

if is_first_run:
    log("First time running EU4 Autobackup!", color='blue', emoji='🎉')
    settings = first_run_setup()
elif source_invalid or backup_invalid:
    log("Configuration issues detected!", color='yellow', emoji='⚠️')
    if source_invalid:
        log(f"❌ Source file not found: {settings.get('SOURCE', 'Not set')}", color='red')
    if backup_invalid:
        log(f"❌ Backup directory not set", color='red')
    
    print("\nWould you like to:")
    print("  1. 🔧 Run setup wizard to reconfigure")
    print("  2. 📋 Go to settings menu to fix manually")
    print("  3. 🚀 Continue anyway (not recommended)")
    
    choice = input("Choose option (1-3): ").strip()
    if choice == '1':
        settings = first_run_setup()
    elif choice == '3':
        log("Continuing with potentially invalid settings...", color='yellow', emoji='⚠️')

# Show menu before starting backup loop
settings_menu(settings)
SOURCE = settings.get('SOURCE', DEFAULT_SETTINGS['SOURCE'])
BACKUP_DIR = settings.get('BACKUP_DIR', DEFAULT_SETTINGS['BACKUP_DIR'])
interval = settings.get('interval', DEFAULT_SETTINGS['interval'])
log(f"Monitoring EU4 autosave file for changes every {interval}s", color='blue', emoji='🔍')
log(f"📂 Source: {SOURCE}", color='blue')
log(f"💾 Backups: {BACKUP_DIR}", color='blue')
log("Press Ctrl+Q to stop monitoring and return to menu", color='yellow', emoji='ℹ️')
log("Or press Ctrl+C to exit completely", color='yellow', emoji='ℹ️')
heartbeat = 0

# Get the initial modification time of the save file
last_mtime = get_mtime(SOURCE)

# Import for non-blocking input
import select
import sys

def check_for_quit():
    """Check if user wants to quit monitoring (Ctrl+Q detection)."""
    if sys.platform == "win32":
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # Check for Ctrl+Q (ASCII 17 or ord('q') with Ctrl modifier)
            if key == b'\x11':  # Ctrl+Q
                return True
    else:
        # Unix/Linux/Mac - use select
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            key = sys.stdin.read(1)
            if ord(key) == 17:  # Ctrl+Q
                return True
    return False

# Main monitoring loop
try:
    while True:
        time.sleep(1)  # Check every second for responsiveness
        heartbeat += 1
        
        # Check if user wants to quit
        if check_for_quit():
            log("Returning to settings menu...", color='blue', emoji='↩️')
            settings_menu(settings)
            # Reset variables after returning from menu
            SOURCE = settings.get('SOURCE', DEFAULT_SETTINGS['SOURCE'])
            BACKUP_DIR = settings.get('BACKUP_DIR', DEFAULT_SETTINGS['BACKUP_DIR'])
            interval = settings.get('interval', DEFAULT_SETTINGS['interval'])
            log(f"Resumed monitoring every {interval}s", color='blue', emoji='🔍')
            log(f"📂 Source: {SOURCE}", color='blue')
            log(f"💾 Backups: {BACKUP_DIR}", color='blue')
            log("Press Ctrl+Q to stop monitoring and return to menu", color='yellow', emoji='ℹ️')
            log("Or press Ctrl+C to exit completely", color='yellow', emoji='ℹ️')
            heartbeat = 0
            last_mtime = get_mtime(SOURCE)
            continue
        
        # Only check file changes at the specified interval
        if heartbeat % interval == 0:
            current_mtime = get_mtime(SOURCE)  # Check if the save file has changed
            
            # Print status every 10 seconds
            if heartbeat % 10 == 0:
                log("Watching for file changes...", color='yellow', emoji='👀')
            
            # If the file has changed, create a backup
            if current_mtime and current_mtime != last_mtime:
                tag = get_player_tag(SOURCE)  # Get the country tag
                timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')  # Format the timestamp
                backup_name = f'mp_autosave_{tag}_{timestamp}.eu4'  # Build backup filename
                backup_path = os.path.join(BACKUP_DIR, backup_name)  # Build backup path
                shutil.copy2(SOURCE, backup_path)  # Copy the save file
                log(f'💾 Backup created: {backup_name}', color='green', emoji='✅')
                # Cleanup old backups based on in-game year
                current_year = get_save_year(SOURCE)
                keep_years = settings.get('keep_years', DEFAULT_SETTINGS.get('keep_years', 'all'))
                if current_year is not None:
                    cleanup_old_backups(BACKUP_DIR, current_year, keep_years)
                last_mtime = current_mtime  # Update last_mtime
                
except KeyboardInterrupt:
    log("Goodbye!", color='blue', emoji='👋')
    exit(0)
