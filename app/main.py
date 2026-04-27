from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, hotels, bookings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pet-Friendly Travel SaaS API",
    description="Multi-tenant travel booking platform for pet owners - CMPE 131 Scenario #9",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(hotels.router)
app.include_router(bookings.router)

@app.get("/")
def root():
    return {"message": "Pet-Friendly Travel SaaS API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}