"""
Video-to-Audio (v2a) Converter
Reads local video files, extracts audio using yt-dlp and ffmpeg, 
and outputs high-quality MP3 files to a designated target directory.
"""

import os
import json
from yt_dlp import YoutubeDL

CONFIG_FILE = "v2a.config.json"

def load_config():
    """
    Load configuration from the JSON file. 
    Creates a default configuration file if one does not already exist.
    """
    default_config = {
        "SOURCE_DIR": "/Volumes/Self 1Touch/self/userdata/Music_4tb/Christian",
        "TARGET_DIR": "/Volumes/Self 1Touch/self/userdata/Music_4tb/Christian_audio"
    }
    
    # Initialize default config file if missing
    if not os.path.exists(CONFIG_FILE):
        print(f"⚠️ Configuration file '{CONFIG_FILE}' not found. Creating a default one...")
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"✅ Created default config at: {os.path.abspath(CONFIG_FILE)}")
        except Exception as e:
            print(f"❌ Critical Error: Could not create config file: {e}")
            exit(1)
            
    # Parse and validate the configuration file
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            for key in ["SOURCE_DIR", "TARGET_DIR"]:
                if key not in config:
                    raise ValueError(f"Missing required key '{key}' in {CONFIG_FILE}")
            return config
    except Exception as e:
        print(f"❌ Critical Error: Failed to parse '{CONFIG_FILE}': {e}")
        exit(1)

# Load directory paths from configuration
config = load_config()
SOURCE_DIR = config["SOURCE_DIR"]
TARGET_DIR = config["TARGET_DIR"]

# Validate that the source directory exists before proceeding
if not os.path.exists(SOURCE_DIR):
    print(f"❌ Critical Error: Source directory does not exist or is not mounted:\n   {SOURCE_DIR}")
    exit(1)

# Ensure target output directory exists
try:
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
except Exception as e:
    print(f"❌ Critical Error: Could not create target directory {TARGET_DIR}: {e}")
    exit(1)

# Configure yt-dlp extraction options
ydl_opts = {
    'format': 'bestaudio/best',
    'enable_file_urls': True, 
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': os.path.join(TARGET_DIR, '%(title)s.%(ext)s'),
    'quiet': False,
    'no_warnings': True,
}

def convert_videos():
    """Scans the source directory, filters duplicate formats, and converts videos to MP3."""
    try:
        all_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(('.mp4', '.webm', '.mkv'))]
    except Exception as e:
        print(f"❌ Error reading source directory: {e}")
        return

    if not all_files:
        print(f"⚠️ No compatible video files (.mp4, .webm, .mkv) found in {SOURCE_DIR}")
        return
    
    # Filter out duplicate formats of the same media (e.g., matching IDs across .mp4 and .webm)
    processed_ids = set()
    files_to_process = []
    
    for f in all_files:
        try:
            file_id = f.split('[')[-1].split(']')[0] if '[' in f else f
            if file_id not in processed_ids:
                files_to_process.append(f)
                processed_ids.add(file_id)
        except Exception as e:
            print(f"⚠️ Warning: Could not parse filename '{f}': {e}")
            files_to_process.append(f)  # Fallback to process anyway

    print(f"Found {len(all_files)} files. Unique songs to process: {len(files_to_process)}")

    success_count = 0
    failed_files = []

    # Process each unique file through yt-dlp
    with YoutubeDL(ydl_opts) as ydl:
        for filename in files_to_process:
            file_path = "file://" + os.path.join(SOURCE_DIR, filename)
            print(f"\n---> Converting: {filename}")
            try:
                ydl.extract_info(file_path, download=True)
                success_count += 1
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error processing {filename}: {error_msg}")
                failed_files.append((filename, error_msg))

    # --- Summary Report ---
    print("\n" + "="*40)
    print("--- CONVERSION SUMMARY ---")
    print(f"✅ Successfully converted: {success_count}")
    print(f"❌ Failed: {len(failed_files)}")
    print("="*40)

    # Output failure log if any conversion errors occurred
    if failed_files:
        log_path = os.path.join(TARGET_DIR, "failed_conversions.txt")
        try:
            with open(log_path, "w") as log_file:
                log_file.write("Failed Conversions Log:\n\n")
                for fname, err in failed_files:
                    log_file.write(f"File: {fname}\nError: {err}\n{'-'*30}\n")
            print(f"📝 A log of failed conversions has been saved to:\n   {log_path}")
        except Exception as log_err:
            print(f"⚠️ Could not write failure log file: {log_err}")

    print("\n--- Process completed! ---")

if __name__ == "__main__":
    convert_videos()
