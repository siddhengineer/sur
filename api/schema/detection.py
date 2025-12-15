from typing import List, Optional
from pydantic import BaseModel

class DetectionBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int
    conf: float
    cls: str

class DetectionResponse(BaseModel):
    count: int
    shoplifting: bool
    detections: List[DetectionBox]
    message: Optional[str] = None
