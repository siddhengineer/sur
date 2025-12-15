import os
import cv2
import numpy as np
from typing import Tuple, List
from src.yolo_detector import YOLODetector
from src.config import get_settings

settings = get_settings()
_detector = YOLODetector(model_name=settings.yolo_model, conf_thresh=settings.detection_confidence)


def is_shoplifting_detection(d) -> bool:
    try:
        conf = float(getattr(d, 'conf', 0.0))
    except Exception:
        conf = 0.0
    thresh = float(getattr(settings, 'alert_confidence', float(os.getenv('SD_ALERT_CONFIDENCE', '0.85'))))
    return conf >= thresh


def detect_image_bytes(image_bytes: bytes) -> Tuple[bool, List]:
    arr = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    img = cv2.imdecode(arr, 1)
    if img is None:
        raise ValueError("Invalid image data")
    dets = _detector.detect(img)
    shoplifting = any(is_shoplifting_detection(d) for d in dets)
    return shoplifting, dets
