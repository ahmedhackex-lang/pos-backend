"""
FastAPI Cloud Backend - Production-ready
"""
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    migrations_dir = Path(__file__).parent / "migrations"
    if not migrations_dir.exists():
        return
    sql_files = sorted(migrations_dir.glob("*.sql"))
    if not sql_files:
        return
    db = SessionLocal()
    try:
        for sql_file in sql_files:
            logger.info(f"Running migration: {sql_file.name}")
            sql_content = sql_file.read_text(encoding="utf-8")
            statements = [s.strip() for s in sql_content.split(";") if s.strip()]
            for stmt in statements:
                if stmt.lstrip().startswith("--") and "\n" not in stmt:
                    continue
                try:
                    db.execute(text(stmt))
                except Exception as e:
                    logger.warning(f"Statement skipped: {e}")
                    db.rollback()
                    continue
            db.commit()
            logger.info(f"Migration {sql_file.name} done")
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
run_migrations()

allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
use_credentials = "*" not in allowed_origins

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    redirect_slashes=False,
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
