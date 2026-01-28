import os
import json
import asyncio
from yt_dlp import YoutubeDL
from .sockets import broadcast_progress

class DownloadProgress:
    """Manages download progress and WebSocket updates"""
    def __init__(self, filename):
        self.filename = filename
        self.percent = "0%"
        self.speed = "N/A"
        self.eta = "N/A"
        self.loop = None
    
    def get_event_loop(self):
        """Get or create event loop"""
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            try:
                return asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return loop

    def update(self, d):
        """Update progress from yt-dlp hook"""
        if d['status'] == 'downloading':
            self.percent = d.get('_percent_str', '0%').strip()
            self.speed = d.get('_speed_str', 'N/A').strip()
            self.eta = d.get('_eta_str', 'N/A').strip()
            
            # Print to console for debugging
            print(f"Progress: {self.percent} | Speed: {self.speed} | ETA: {self.eta}")
            
            # Send WebSocket update
            try:
                loop = self.get_event_loop()
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        broadcast_progress({
                            "type": "progress",
                            "percent": self.percent,
                            "speed": self.speed,
                            "eta": self.eta,
                            "filename": self.filename
                        }),
                        loop
                    )
            except Exception as e:
                print(f"WebSocket error: {e}")
        
        elif d['status'] == 'finished':
            print(f"Download finished: {self.filename}")
            try:
                loop = self.get_event_loop()
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        broadcast_progress({
                            "type": "completed",
                            "filename": self.filename,
                            "message": "Download completed!"
                        }),
                        loop
                    )
            except Exception as e:
                print(f"WebSocket error: {e}")
                


def download(url: str, filename: str, folder: str = "downloads"):
    """Download YouTube video with progress tracking"""
    os.makedirs(folder, exist_ok=True)
    
    # Create progress tracker
    progress = DownloadProgress(filename)
    
    # Notify start
    try:
        loop = progress.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(
                broadcast_progress({
                    "type": "started",
                    "filename": filename,
                    "url": url
                }),
                loop
            )
    except:
        pass
    
    ydl_opts = {
        'format': 'best[height<=720]',  # Best quality up to 720p
        'outtmpl': os.path.join(folder, f'{filename}.%(ext)s'),
        'progress_hooks': [progress.update],
        'quiet': False,  # Show yt-dlp output
        'no_warnings': False,
        'retries': 10,
        'fragment_retries': 10,
        'socket_timeout': 30,
        'noprogress': False,  # Show progress in console
    }
    
    try:
        print(f"Starting download: {filename}")
        print(f"URL: {url}")
        
        with YoutubeDL(ydl_opts) as ydl:
            # Optional: Get video info first
            info = ydl.extract_info(url, download=False)
            print(f"Video title: {info.get('title', 'Unknown')}")
            print(f"Duration: {info.get('duration', 0)} seconds")
            
            # Start download
            ydl.download([url])
        
        print(f"Download completed successfully: {filename}")
        return True
        
    except Exception as e:
        print(f"Download failed: {str(e)}")
        
        # Notify error
        try:
            loop = progress.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    broadcast_progress({
                        "type": "error",
                        "message": f"Download failed: {str(e)}",
                        "filename": filename
                    }),
                    loop
                )
        except:
            pass
        
        return False 
    
    
