from pydantic import BaseModel
from typing import Optional

class DownloadRequest(BaseModel):
    url: str
    filename: str
    folder: Optional[str] = "downloads"

class ProgressUpdate(BaseModel):
    type: str
    percent: str
    speed: str
    eta: str
    filename: str