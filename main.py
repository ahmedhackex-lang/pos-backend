"""
FastAPI Cloud Backend - Secure CORS Configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import engine, Base
from api.auth import router as auth_router
from api.products import router as products_router
from api.sales import router as sales_router
from api.dashboard import router as dashboard_router
from config.settings import settings

# Initialize database
Base.metadata.create_all(bind=engine)

# Create app
app = FastAPI(title="Grocery POS API")

# DEFINE ALLOWED ORIGINS CLEARLY
# Added both production and local development origins
origins = [
    "https://owner-dashboard-chi.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        "version": settings.APP_VERSION,
        "allowed_origins": origins
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
