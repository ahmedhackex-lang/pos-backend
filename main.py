"""
FastAPI Cloud Backend - Production-ready CORS
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import engine, Base
from config.settings import settings
from api.auth import router as auth_router
from api.products import router as products_router
from api.sales import router as sales_router
from api.dashboard import router as dashboard_router

# Initialize database
Base.metadata.create_all(bind=engine)

# Create app
app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS Configuration
# Parse comma-separated ALLOWED_ORIGINS env var into a list
allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

# If wildcard, disable credentials (CORS spec requires this)
use_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=use_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Routes
app.include_router(auth_router, prefix="/api/auth")
app.include_router(products_router, prefix="/api/products")
app.include_router(sales_router, prefix="/api/sales")
app.include_router(dashboard_router, prefix="/api/dashboard")


@app.get("/")
def root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "cors_origins": allowed_origins,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
