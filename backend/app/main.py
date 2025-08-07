from fastapi import FastAPI
from .routes.park_info_routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Parking Slots API",
    description="API for managing and optimizing parking slots",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # lub ["*"] w dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get('/')
async def root():
    return {"message": "API is working"}

    