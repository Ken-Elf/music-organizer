# 🎵 Music Library Organizer

A Python script that automatically organizes your messy music collection into a clean, structured library organized by Artist and Album.

## 📋 What It Does

This script takes a disorganized music folder like this:
```
Music/
├── RandomFolder1/
│   ├── 01-artist-song.mp3
│   ├── track2.mp3
├── SomeDownload/
│   ├── album/
│   │   ├── song1.mp3
```

And organizes it into:
```
Music_Organized/
├── Artist Name/
│   ├── Album Name/
│   │   ├── song1.mp3
│   │   ├── song2.mp3
├── Another Artist/
│   ├── Their Album/
│   │   ├── track.mp3
```

### Key Features
- ✅ Reads metadata (artist, album) from music files
- ✅ Falls back to intelligent filename parsing if no metadata exists
- ✅ Handles mixed filename formats (track numbers, dashes, underscores)
- ✅ Copies files (keeps originals safe!)
- ✅ Cleanup mode to fix already-organized folders
- ✅ Debug mode to troubleshoot metadata issues
- ✅ Supports: MP3, FLAC, M4A, WAV, OGG, WMA, AAC

---

## 🚀 Installation

### Step 1: Install Required Library
Open Command Prompt (search "cmd" in Windows) and type:
```bash
pip install mutagen
```

### Step 2: Download the Script
Save the script as `organize_music.py` in a folder like `C:\Music Scripts\`

---

## ⚙️ Configuration

Edit these lines at the top:

```python
SOURCE_FOLDER = r"C:\Users\YourUsername\Music"  # Where your messy music is
DESTINATION_FOLDER = r"C:\Users\YourUsername\Music_Organized"  # Where organized music goes

CLEANUP_MODE = False  # Set to True for cleanup mode (see below)
DEBUG_MODE = False    # Set to True to see detailed metadata info
```

### Important Notes:
- Replace `YourUsername` with your actual Windows username
- Use `r"..."` format (the `r` is important!)
- You can use forward slashes `/` or backslashes `\`

---

## 🎯 Usage

### Normal Mode: Organize New Music

This is for organizing music from a messy source folder.

**Settings:**
```python
CLEANUP_MODE = False
DEBUG_MODE = False
```

**Run:**
1. Open Command Prompt
2. Navigate to the script folder: `cd C:\Music Scripts`
3. Run: `python organize_music.py`
4. Type `yes` when prompted

**What happens:**
- Scans all music files in `SOURCE_FOLDER`
- Reads metadata or parses filenames
- **Copies** files to `DESTINATION_FOLDER/Artist/Album/`
- Shows progress for each file

---

### Cleanup Mode: Fix Already-Organized Music

Use this when you have weird folders like "01", "B2", or "CD1" in your organized library.

**Settings:**
```python
CLEANUP_MODE = True
DEBUG_MODE = False
```

**Run:**
Same as above - the script will automatically detect and reorganize misplaced files.

**What it fixes:**
- Folders named with just numbers ("01", "123")
- Single/double character folders ("A", "B2", "CD")
- Disc folders ("Disc 1", "CD2")

These get reorganized into proper Artist/Album structure.

---

### Debug Mode: Troubleshoot Metadata Issues

Use this when files aren't being organized correctly.

**Settings:**
```python
DEBUG_MODE = True
```

**Output example:**
```
[DEBUG] Reading: 01 One More Time.mp3
[DEBUG] File type: <class 'mutagen.mp3.MP3'>
[DEBUG] All tags: {'TPE1': 'Daft Punk', 'TALB': 'Discovery', ...}
[DEBUG] Found artist: Daft Punk
[DEBUG] Found album: Discovery
```

This shows:
- What metadata tags are in the file
- Which tags the script found
- Why files end up as "Unknown Artist"

---

## 🛠️ Troubleshooting

### Problem: "File is being used by another process"
**Solution:**
1. Close File Explorer windows showing the music folder
2. Close all music players (Windows Media Player, iTunes, VLC, etc.)
3. Restart your computer
4. Try again

### Problem: Everything goes to "Unknown Artist"
**Solutions:**
1. Turn on `DEBUG_MODE = True` to see what tags exist
2. Check if mutagen is installed: `pip install mutagen`
3. Your files might not have metadata - that's okay! The script will still organize by filename

### Problem: Script won't start
**Solutions:**
1. Make sure Python is installed: Type `python --version` in Command Prompt
2. Make sure paths are correct (no "YourUsername" in the paths)
3. Check that the script file ends with `.py`

### Problem: Some artists have weird names
This happens when:
- Files have no metadata AND
- Filenames don't match expected patterns

**Fix:** Manually add metadata using a tool like:
- [Mp3tag](https://www.mp3tag.de/en/) (free)
- [MusicBrainz Picard](https://picard.musicbrainz.org/) (free)

---

## ⚠️ Important Notes

### Files Are Copied, Not Moved
- Original files stay in `SOURCE_FOLDER`
- After verifying everything looks good, you can delete the originals
- This keeps you safe from accidents!

### Supported File Types
- MP3 (`.mp3`)
- FLAC (`.flac`)
- M4A/AAC (`.m4a`, `.aac`)
- WAV (`.wav`)
- OGG (`.ogg`)
- WMA (`.wma`)

### Windows Path Restrictions
The script automatically removes these invalid characters from folder names:
`< > : " / \ | ? *`

---

## 📄 License

Free to use and modify for your personal music organization needs!

---

**Happy Organizing! 🎵**

