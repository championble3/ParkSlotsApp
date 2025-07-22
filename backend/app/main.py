from fastapi import FastAPI
from .routes.park_info_routes import router

app = FastAPI(
    title="Parking Slots API",
    description="API for managing and optimizing parking slots",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(router)

@app.get('/')
async def root():
    return {"message": "API is working"}

    