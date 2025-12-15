from typing import List
from api.schema.detection import DetectionResponse, DetectionBox
from api.service.detection_service import detect_image_bytes
from api.service.telegram_service import send_telegram_alert


def detect_image_and_alert(image_bytes: bytes) -> DetectionResponse:
    shoplifting, dets = detect_image_bytes(image_bytes)
    boxes: List[DetectionBox] = []
    for d in dets:
        x1, y1, x2, y2 = d.xyxy
        boxes.append(DetectionBox(x1=int(x1), y1=int(y1), x2=int(x2), y2=int(y2), conf=float(d.conf), cls=str(d.cls)))
    if shoplifting:
        try:
            send_telegram_alert("Shoplifting detected via API image endpoint.")
        except Exception:
            pass
    return DetectionResponse(count=len(boxes), shoplifting=shoplifting, detections=boxes, message=("alert sent" if shoplifting else None))
