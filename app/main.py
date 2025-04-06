# api-gateway/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.api.auth import router as auth_router 

app = FastAPI(title="Authentication Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the auth router with the correct prefix
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

def create_tables():
    Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    create_tables()

@app.get("/health")
def health_check():
    return {"status": "ok"}