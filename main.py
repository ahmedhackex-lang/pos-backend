from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import engine, Base
from api.auth import router as auth_router
from api.products import router as products_router
from api.sales import router as sales_router
from api.dashboard import router as dashboard_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grocery POS API")

# Explicitly list all possible frontend origins
origins = [
    "https://owner-dashboard-chi.vercel.app",
    "https://owner-dashboard-olirm04sy-ahmadgffx-8492s-projects.vercel.app", # Branch URL
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(products_router, prefix="/api/products", tags=["Products"])
app.include_router(sales_router, prefix="/api/sales", tags=["Sales"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"status": "online"}
