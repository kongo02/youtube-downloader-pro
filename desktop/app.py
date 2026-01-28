import tkinter as tk
from tkinter import messagebox
import requests
import subprocess
import sys
import os

class YouTubeDownloader:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_ui()
        self.start_backend()
    
    def setup_ui(self):
        self.root.title("YouTube Downloader")
        self.root.geometry("500x300")
        
        # Title
        tk.Label(self.root, text="YouTube Downloader", 
                font=("Arial", 20)).pack(pady=20)
        
        # URL
        tk.Label(self.root, text="YouTube URL:").pack()
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)
        
        # Filename
        tk.Label(self.root, text="Filename:").pack()
        self.name_entry = tk.Entry(self.root, width=30)
        self.name_entry.pack(pady=5)
        
        # Download button
        self.download_btn = tk.Button(self.root, text="Download", 
                                     command=self.download, bg="green", fg="white")
        self.download_btn.pack(pady=20)
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready")
        self.status_label.pack()
    
    def start_backend(self):
        """Start backend if not running"""
        try:
            requests.get("http://127.0.0.1:8000/health", timeout=2)
            print("Backend is already running")
        except:
            print("Starting backend...")
            # In development, run the backend script
            backend_path = os.path.join(os.path.dirname(__file__), "..", "backend", "run.py")
            subprocess.Popen([sys.executable, backend_path], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
    
    def download(self):
        url = self.url_entry.get()
        filename = self.name_entry.get()
        
        if not url or not filename:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/download",
                params={"url": url, "filename": filename}
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Download started!")
                self.status_label.config(text="Downloading...")
            else:
                messagebox.showerror("Error", f"Server error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Backend server not running")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()