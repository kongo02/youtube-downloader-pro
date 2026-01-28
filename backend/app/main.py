from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import concurrent.futures
from .downloader import download
from .sockets import connect, manager

app = FastAPI(
    title="YouTube Downloader API",
    description="Download YouTube videos with real-time progress",
    version="1.0.0"
)

# Add CORS for all origins (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for downloads
executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connect(websocket)
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to download server"
        })
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except:
                break
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

@app.post("/download")
async def start_download(
    url: str, 
    filename: str, 
    folder: str = "downloads",
    background_tasks: BackgroundTasks = None
):
    """Start a download with real-time progress"""
    # Validate inputs
    if not url or not url.strip():
        return {"status": "error", "message": "URL is required"}
    
    if not filename or not filename.strip():
        return {"status": "error", "message": "Filename is required"}
    
    # Clean filename (remove special characters)
    import re
    clean_filename = re.sub(r'[^\w\s-]', '', filename)
    clean_filename = re.sub(r'[-\s]+', '_', clean_filename)
    
    # Run download in background
    try:
        # Use asyncio.to_thread for cleaner async/await
        result = await asyncio.to_thread(
            download,
            url,
            clean_filename,
            folder
        )
        
        return {
            "status": "success" if result else "error",
            "message": f"Download {'completed' if result else 'failed'} for '{clean_filename}'",
            "filename": clean_filename
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Download failed: {str(e)}"
        }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "youtube-downloader",
        "active_connections": len(manager.active_connections)
    }

@app.get("/test-progress")
async def test_progress():
    """Test WebSocket progress updates"""
    import asyncio
    
    # Send test progress updates
    for i in range(1, 101):
        await manager.send_progress({
            "type": "progress",
            "percent": f"{i}%",
            "speed": f"{i * 100} KB/s",
            "eta": f"{100 - i} seconds",
            "filename": "test_video.mp4"
        })
        await asyncio.sleep(0.1)
    
    await manager.send_progress({
        "type": "completed",
        "filename": "test_video.mp4",
        "message": "Test download completed!"
    })
    
    return {"status": "test_completed"}

@app.get("/")
async def root():
    return {
        "app": "YouTube Downloader API",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "ws://127.0.0.1:8000/ws (for real-time progress)",
            "download": "POST /download?url=URL&filename=NAME",
            "health": "GET /health",
            "test": "GET /test-progress"
        },
        "instructions": [
            "1. Connect WebSocket to ws://127.0.0.1:8000/ws for progress",
            "2. POST to /download with url and filename parameters",
            "3. Watch real-time progress in WebSocket"
        ]
    }