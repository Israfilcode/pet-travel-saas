from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, bookings, hotels, flights
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Pet-Friendly Travel SaaS API",
    description="Multi-tenant travel booking platform for pet owners - CMPE 131 Scenario #9",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(bookings.router)
app.include_router(hotels.router)
app.include_router(flights.router)
@app.get("/")
def root():
    return {"message": "Pet-Friendly Travel SaaS API is running"}
@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/app", response_class=FileResponse)
def serve_frontend():
    return os.path.join(static_dir, "index.html")
