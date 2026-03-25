import os
import shutil
from pathlib import Path
import re

# ============================================================
# CONFIGURATION - CHANGE THESE PATHS TO MATCH YOUR SYSTEM
# ============================================================
SOURCE_FOLDER = r"C:/Users/kenne/Documents/Soulseek Downloads"
DESTINATION_FOLDER = r"C:\Users\kenne\Music\music_organized"

# Set this to True if you want to clean up your already-organized folder
CLEANUP_MODE = False  # Change to True for second pass cleanup

#Set this to True to see detailed debug info about metadata reading
DEBUG_MODE = True  # Change to False to turn off debugging

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_filename(name):
    """Remove invalid characters from folder/file names for Windows"""
    # Windows doesn't allow these characters in filenames: < > : " / \ | ? *
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    return name.strip()

def try_read_metadata(file_path):
    """
    Try to read artist and album from file metadata using mutagen library.
    Returns: (artist, album) or (None, None) if metadata can't be read
    
    NOTE: This requires the 'mutagen' library. Install it with:
    pip install mutagen
    """
    try:
        from mutagen import File
        audio = File(file_path)
        
        if DEBUG_MODE:
            print(f"\n  [DEBUG] Reading: {os.path.basename(file_path)}")
        
        if audio is None:
            if DEBUG_MODE:
                print(f"  [DEBUG] Mutagen returned None - file format not supported")
            return None, None
        
        if DEBUG_MODE:
            print(f"  [DEBUG] File type: {type(audio)}")
            print(f"  [DEBUG] All tags: {dict(audio)}")
            
        # Different file formats store metadata differently
        artist = None
        album = None
        
        # Try common metadata tags
        if 'artist' in audio:
            artist = str(audio['artist'][0]) if isinstance(audio['artist'], list) else str(audio['artist'])
        elif 'ARTIST' in audio:
            artist = str(audio['ARTIST'][0]) if isinstance(audio['ARTIST'], list) else str(audio['ARTIST'])
        elif '\xa9ART' in audio:  # iTunes format
            artist = str(audio['\xa9ART'][0])
        elif 'TPE1' in audio:  # ID3v2 tag
            artist = str(audio['TPE1'].text[0]) if hasattr(audio['TPE1'], 'text') else str(audio['TPE1'])
            
        if 'album' in audio:
            album = str(audio['album'][0]) if isinstance(audio['album'], list) else str(audio['album'])
        elif 'ALBUM' in audio:
            album = str(audio['ALBUM'][0]) if isinstance(audio['ALBUM'], list) else str(audio['ALBUM'])
        elif '\xa9alb' in audio:  # iTunes format
            album = str(audio['\xa9alb'][0])
        elif 'TALB' in audio:  # ID3v2 tag
            album = str(audio['TALB'].text[0]) if hasattr(audio['TALB'], 'text') else str(audio['TALB'])
        
        if DEBUG_MODE:
            print(f"  [DEBUG] Found artist: {artist}")
            print(f"  [DEBUG] Found album: {album}")
            
        return artist, album
    except ImportError:
        if DEBUG_MODE:
            print(f"  [DEBUG] ERROR: mutagen library not installed!")
        print("WARNING: mutagen library not found. Install with: pip install mutagen")
        return None, None
    except Exception as e:
        if DEBUG_MODE:
            print(f"  [DEBUG] Error reading metadata: {str(e)}")
        return None, None

def parse_filename(filename):
    """
    Try to extract artist and album from filename using common patterns.
    Returns: (artist, album) or (None, None) if pattern doesn't match
    """
    # Remove file extension
    name_without_ext = os.path.splitext(filename)[0]
    
    # Pattern 1: Remove leading track numbers first
    # Matches: "01-", "01.", "01 ", "1-", etc.
    name_without_track = re.sub(r'^\d+[-.\s]+', '', name_without_ext)
    
    # Pattern 2: "Artist - Album - Song"
    match = re.match(r'^(.+?)\s*-\s*(.+?)\s*-\s*(.+)$', name_without_track)
    if match:
        artist = match.group(1).strip()
        album = match.group(2).strip()
        # Check if "album" part looks like a song title (contains parentheses like "original_mix")
        # If so, it's probably Artist - Song - Version format, no album
        if '(' in album or '_mix' in album.lower() or 'remix' in album.lower():
            return artist, "Unknown Album"
        return artist, album
    
    # Pattern 3: "Artist - Song" (no album)
    match = re.match(r'^(.+?)\s*-\s*(.+)$', name_without_track)
    if match:
        return match.group(1).strip(), "Unknown Album"
    
    # Pattern 4: Just track number and title, no artist
    if name_without_track != name_without_ext:  # We removed a track number
        return None, None
    
    # Couldn't parse filename
    return None, None

def get_artist_and_album(file_path):
    """
    Main function to determine artist and album for a music file.
    Tries metadata first, then filename parsing.
    Returns: (artist, album)
    """
    # Try reading metadata first
    artist, album = try_read_metadata(file_path)
    
    # If metadata didn't work, try parsing filename
    if not artist:
        filename = os.path.basename(file_path)
        artist, album = parse_filename(filename)
    
    # Set defaults if still nothing found
    if not artist:
        artist = "Unknown Artist"
    if not album:
        album = "Unknown Album"
    
    # Clean the names for use as folder names
    artist = clean_filename(artist)
    album = clean_filename(album)
    
    return artist, album

def is_misplaced_folder(folder_name):
    """
    Check if a folder looks like it shouldn't be a top-level artist folder.
    Returns True if it's a number, single letter, or other suspicious pattern.
    """
    # Check if it's just numbers (like "01", "02", "123")
    if folder_name.isdigit():
        return True
    
    # Check if it's just 1-2 characters (like "B2", "A", "CD")
    if len(folder_name) <= 2:
        return True
    
    # Check if it matches disc/CD patterns
    if re.match(r'^(cd|disc|disk)\s*\d*$', folder_name.lower()):
        return True
    
    return False

def cleanup_organized_folder():
    """
    Second pass: Find music files in weird folders (like "01", "B2") 
    inside the organized folder and reorganize them properly.
    """
    print("CLEANUP MODE: Reorganizing nested files in organized folder...")
    print(f"Scanning: {DESTINATION_FOLDER}")
    print("-" * 60)
    
    total_files = 0
    moved_files = 0
    music_extensions = {'.mp3', '.flac', '.m4a', '.wav', '.ogg', '.wma', '.aac'}
    folders_to_remove = set()  # Track empty folders to clean up
    
    # Look through all top-level folders
    for item in os.listdir(DESTINATION_FOLDER):
        item_path = os.path.join(DESTINATION_FOLDER, item)
        
        # Skip if not a directory
        if not os.path.isdir(item_path):
            continue
        
        # Check if this looks like a misplaced folder
        if is_misplaced_folder(item):
            print(f"Found suspicious folder: {item}")
            
            # Walk through everything inside this folder
            for root, dirs, files in os.walk(item_path):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext not in music_extensions:
                        continue
                    
                    total_files += 1
                    source_path = os.path.join(root, file)
                    
                    try:
                        # Get proper artist and album
                        artist, album = get_artist_and_album(source_path)
                        
                        # Create proper destination
                        artist_folder = os.path.join(DESTINATION_FOLDER, artist)
                        album_folder = os.path.join(artist_folder, album)
                        os.makedirs(album_folder, exist_ok=True)
                        
                        dest_path = os.path.join(album_folder, file)
                        
                        # Move the file to correct location
                        shutil.move(source_path, dest_path)
                        moved_files += 1
                        
                        print(f"  ✓ Moved: {file} → {artist}/{album}/")
                        
                    except Exception as e:
                        print(f"  ✗ Error with {file}: {str(e)}")
            
            # Mark this folder for removal
            folders_to_remove.add(item_path)
    
    # Remove empty folders
    print("\nCleaning up empty folders...")
    for folder in folders_to_remove:
        try:
            # Remove the folder and all empty subdirectories
            for root, dirs, files in os.walk(folder, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if not os.listdir(dir_path):  # If empty
                        os.rmdir(dir_path)
                        print(f"  Removed empty: {dir_path}")
            
            # Remove the main folder if empty
            if not os.listdir(folder):
                os.rmdir(folder)
                print(f"  Removed: {folder}")
        except Exception as e:
            print(f"  Couldn't remove {folder}: {str(e)}")
    
    print("-" * 60)
    print(f"Cleanup complete!")
    print(f"Files found in misplaced folders: {total_files}")
    print(f"Successfully moved: {moved_files}")

def organize_music():
    """
    Main function that organizes all music files.
    Structure: Destination/Artist/Album/song.mp3
    """
    # Create destination folder if it doesn't exist
    os.makedirs(DESTINATION_FOLDER, exist_ok=True)
    
    # Statistics
    total_files = 0
    organized_files = 0
    skipped_files = 0
    
    # Music file extensions to look for
    music_extensions = {'.mp3', '.flac', '.m4a', '.wav', '.ogg', '.wma', '.aac'}
    
    print("Starting music organization...")
    print(f"Source: {SOURCE_FOLDER}")
    print(f"Destination: {DESTINATION_FOLDER}")
    print("-" * 60)
    
    # Walk through all files in source folder and subfolders
    for root, dirs, files in os.walk(SOURCE_FOLDER):
        for file in files:
            # Check if it's a music file
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext not in music_extensions:
                continue
            
            total_files += 1
            source_path = os.path.join(root, file)
            
            try:
                # Get artist and album info
                artist, album = get_artist_and_album(source_path)
                
                # Create destination folder structure: Artist/Album/
                artist_folder = os.path.join(DESTINATION_FOLDER, artist)
                album_folder = os.path.join(artist_folder, album)
                os.makedirs(album_folder, exist_ok=True)
                
                # Destination file path
                dest_path = os.path.join(album_folder, file)
                
                # Copy the file (not move, to keep originals safe)
                shutil.copy2(source_path, dest_path)
                organized_files += 1
                
                print(f"✓ Organized: {artist} / {album} / {file}")
                
            except Exception as e:
                skipped_files += 1
                print(f"✗ Error with {file}: {str(e)}")
    
    # Print summary
    print("-" * 60)
    print(f"Organization complete!")
    print(f"Total music files found: {total_files}")
    print(f"Successfully organized: {organized_files}")
    print(f"Skipped (errors): {skipped_files}")
    print(f"\nYour organized music is in: {DESTINATION_FOLDER}")
    print("\nIMPORTANT: This script COPIED your files (originals are safe).")
    print("After verifying everything looks good, you can delete the old folders.")

# ============================================================
# RUN THE SCRIPT
# ============================================================
if __name__ == "__main__":
    # Safety check - make sure paths are configured
    if "YourUsername" in SOURCE_FOLDER or "YourUsername" in DESTINATION_FOLDER:
        print("ERROR: Please edit the SOURCE_FOLDER and DESTINATION_FOLDER paths at the top of this script!")
        print("Replace 'YourUsername' with your actual Windows username.")
    else:
        if CLEANUP_MODE:
            # Run cleanup mode - reorganize misplaced files in organized folder
            print("=" * 60)
            print("CLEANUP MODE ENABLED")
            print("=" * 60)
            cleanup_organized_folder()
            
        else:
            # Run normal organization mode
            print(f"This will organize music from:")
            print(f"  {SOURCE_FOLDER}")
            print(f"Into:")
            print(f"  {DESTINATION_FOLDER}")
            print("\nFiles will be COPIED (not moved) - your originals will be safe.")
            organize_music()