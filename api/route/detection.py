from fastapi import APIRouter, UploadFile, File, HTTPException
from api.controller.detection_controller import detect_image_and_alert

router = APIRouter(prefix="/detect", tags=["detect"])

@router.post("/image")
async def detect_image(file: UploadFile = File(...)):
    try:
        data = await file.read()
        resp = detect_image_and_alert(data)
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
