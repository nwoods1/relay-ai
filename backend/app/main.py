from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine
from fastapi.middleware.cors import CORSMiddleware
from app.api.customers import router as customers_router
from app.api.products import router as products_router
from app.api.inventory import router as inventory_router
from app.api.pricing import router as pricing_router
from app.api.quotes import router as quotes_router
from app.api.ai_quotes import router as ai_quotes_router

app = FastAPI(
    title="Relay AI API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    customers_router,
    prefix="/api"
)

app.include_router(
    products_router,
    prefix="/api"
)

app.include_router(
    inventory_router,
    prefix="/api"
)

app.include_router(
    pricing_router,
    prefix="/api"
)

app.include_router(
    quotes_router,
    prefix="/api"
)

app.include_router(
    ai_quotes_router,
    prefix="/api",
)

@app.get("/")
def root():
    return {
        "message": "Relay AI API"
    }


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected"
    }