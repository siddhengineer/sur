from fastapi import FastAPI
from api.route.detection import router as detection_router

app = FastAPI(title="Shoplifting Detection API")

app.include_router(detection_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Shoplifting Detection API"}
