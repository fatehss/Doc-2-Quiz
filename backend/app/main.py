from fastapi import FastAPI
from app.routes import upload # Assuming your structure

app = FastAPI()

# Include the router from the upload module
app.include_router(upload.router)

# ... other setup, maybe other routers ...

@app.get("/")
async def root():
    return {"message": "Hello World"} 