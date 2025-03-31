from fastapi import FastAPI, APIRouter
from .routes import upload
import uvicorn
import os
app = FastAPI()
app.include_router(upload.router, prefix="/api")
@app.get("/")
async def root():
    return {"message": "Hello World"}

def run_server():
    uvicorn.run("app.server:app", host="0.0.0.0", port=8000, reload=os.getenv("FASTAPI_DEV_MODE", False))