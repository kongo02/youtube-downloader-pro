import queue
import threading
import asyncio
from typing import Dict, Any
from .downloader import download

# Thread-safe job queue
download_queue = queue.Queue()

class DownloadJob:
    def __init__(self, url: str, filename: str, folder: str = "downloads"):
        self.url = url
        self.filename = filename
        self.folder = folder
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "filename": self.filename,
            "folder": self.folder
        }

def worker():
    """Background worker that processes download jobs"""
    while True:
        job = download_queue.get()
        if job is None:  # Exit signal
            break
        
        try:
            print(f"Processing job: {job.filename}")
            download(job.url, job.filename, job.folder)
        except Exception as e:
            print(f"Job failed: {e}")
        finally:
            download_queue.task_done()

# Start worker thread
worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()

def enqueue_job(job: DownloadJob):
    """Add a download job to the queue"""
    download_queue.put(job)
    return {
        "status": "queued",
        "position": download_queue.qsize(),
        "filename": job.filename
    }

def get_queue_status():
    """Get current queue status"""
    return {
        "pending": download_queue.qsize(),
        "active": worker_thread.is_alive()
    }