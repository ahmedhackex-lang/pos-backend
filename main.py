"""
FastAPI Cloud Backend - Production-ready
- Auto-runs SQL migrations on startup
- Valid CORS config
- No trailing-slash redirects
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config.database import engine, Base, SessionLocal
from config.settings import settings
from api.auth import router as auth_router
from api.products import router as products_router
from api.sales import router as sales_router
from api.dashboard import router as dashboard_router

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """Execute all .sql files in migrations/ on startup (idempotent)."""
    migrations_dir = Path(__file__).parent / "migrations"
    if not migrations_dir.exists():
        logger.warning(f"Migrations directory not found: {migrations_dir}")
        return

    sql_files = sorted(migrations_dir.glob("*.sql"))
    if not sql_files:
        logger.info("No migration files found")
        return

    db = SessionLocal()
    try:
        for sql_file in sql_files:
            logger.info(f"Running migration: {sql_file.name}")
            sql_content = sql_file.read_text(encoding="utf-8")
            # Split on semicolons but skip empty statements
            statements = [s.strip() for s in sql_content.split(";") if s.strip()]
            for stmt in statements:
                # Skip pure comments
                if stmt.lstrip().startswith("--") and "\n" not in stmt:
                    continue
                try:
                    db.execute(text(stmt))
                except Exception as e:
                    logger.error(f"Statement failed (continuing): {e}")
                    logger.error(f"Statement was: {stmt[:200]}")
                    db.rollback()
                    continue
            db.commit()
            logger.info(f"Migration {sql_file.name} completed")
    except Exception as e:
        logger.error(f"Migration runner failed: {e}")
        db.rollback()
    finally:
        db.close()


# Initialize database tables (only creates missing ones)
Base.metadata.create_all(bind=engine)

# Run migrations to align schema
run_migrations()

# CORS configuration
allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
use_credentials = "*" not in allowed_origins

# Create app (no trailing-slash redirects)
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    redirect_slashes=False,  # <-- eliminates 307 redirects
)

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
