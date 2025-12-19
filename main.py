from fastapi import FastAPI

app = FastAPI(title="Shoplifting Detection API")

@app.get("/")
def root():
    return {"status": "ok", "message": "Shoplifting Detection API"}
