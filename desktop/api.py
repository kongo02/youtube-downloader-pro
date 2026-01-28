import requests
import json
from typing import Optional, Dict, Any

API_BASE = "http://127.0.0.1:8000"

def start_download(url: str, filename: str, folder: str = "downloads") -> Dict[str, Any]:
    """Start a YouTube download via the API"""
    payload = {
        "url": url,
        "filename": filename,
        "folder": folder
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/download",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise Exception("Backend server is not running. Please start the backend first.")
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. The server might be busy.")
    except Exception as e:
        raise Exception(f"API Error: {str(e)}")

def check_health() -> bool:
    """Check if the backend server is healthy"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_server_info() -> Optional[Dict[str, Any]]:
    """Get server information"""
    try:
        response = requests.get(API_BASE, timeout=5)
        return response.json()
    except:
        return None