import uvicorn
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

if __name__ == "__main__":
    print("Starting YouTube Downloader API server...")
    print("WebSocket endpoint: ws://127.0.0.1:8000/ws")
    print("API endpoint: http://127.0.0.1:8000/download")
    print("Press Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False  # Set to True for development
    )