import subprocess
import sys

def update_ytdlp():
    subprocess.run([
        sys.executable, "-m", "yt_dlp", "-U"
    ], capture_output=True)
