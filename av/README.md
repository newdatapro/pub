# Video-to-Audio (v2a) Converter

A lightweight Python utility built on top of `yt-dlp` and `ffmpeg` that scans a directory for local video files (`.mp4`, `.webm`, `.mkv`), removes format duplicates, and converts them into high-quality MP3 audio files.

---

## Key Features

* **Configurable Environment:** External JSON configuration for input and output paths.
* **Smart Deduplication:** Automatically groups video files sharing the same YouTube ID to prevent duplicate processing.
* **Robust Error Handling:** Checks directory paths, logs conversion failures without interrupting the overall batch process, and outputs a detailed failure summary.
* **Automated Log Generation:** Saves error traces to `failed_conversions.txt` inside the target directory if any errors occur.

---

## Prerequisites

* **Python 3.8+**
* **FFmpeg** installed and accessible in your system's `PATH`.

### Installing Dependencies

```bash
pip install yt-dlp
```

---

## Quick Start

1. **Clone or Download** the repository files into your working directory.
2. **Configure Settings:** Run `v2a.py` once to generate a default configuration file (`v2a.config.json`), or manually create `v2a.config.json` in the project root:

```json
{
    "SOURCE_DIR": "/path/to/your/video/files",
    "TARGET_DIR": "/path/to/your/audio/output"
}
```

3. **Run the Script:**

```bash
python v2a.py
```

---

## Output & Logs

* **Audio Quality:** Converted files are output in MP3 format at **192 kbps**.
* **Log Files:** If any files fail during conversion, a log detailing the filename and error message is written to `<TARGET_DIR>/failed_conversions.txt`.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
