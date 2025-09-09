from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys

# Add the parent directory to the path to import from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.routers import advisors, scanner, dashboard

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="InvestShield API",
    description="AI-powered Investor Fraud Detection Tool",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3002", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(advisors.router, prefix="/api/advisors", tags=["advisors"])
app.include_router(scanner.router, prefix="/api/scanner", tags=["scanner"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to InvestShield API",
        "version": "1.0.0",
        "description": "AI-powered Investor Fraud Detection Tool",
        "endpoints": {
            "advisors": "/api/advisors",
            "scanner": "/api/scanner",
            "dashboard": "/api/dashboard",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "InvestShield API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
