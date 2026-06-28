"""Vrika Admin — License Administration Backend."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import close_db, init_db
from app.routers.auth import router as auth_router
from app.routers.license_admin import router as license_admin_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Vrika Admin backend starting...")
    await init_db()
    logger.info("Database connected")
    yield
    await close_db()
    logger.info("Vrika Admin backend shutdown")


app = FastAPI(
    title="Vrika Admin API",
    description="License administration backend for Vrika cybersecurity platform",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(license_admin_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "vrika-admin"}
