from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base

# Import all models so they register with Base
from app.models import *  # noqa: F403, F401

# Import routers
from app.api import (
    auth,
    organizations,
    partners,
    data_sources,
    schemas,
    contracts,
    pipeline_runs,
    dependencies,
    publication,
    changes,
    audit,
    metrics,
)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Schema-Change Sentinel API - Detects breaking upstream schema changes and blocks unsafe publication in fintech data pipelines.",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (for SQLite/dev)
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(partners.router)
app.include_router(data_sources.router)
app.include_router(schemas.router)
app.include_router(contracts.router)
app.include_router(pipeline_runs.router)
app.include_router(dependencies.router)
app.include_router(publication.router)
app.include_router(changes.router)
app.include_router(audit.router)
app.include_router(metrics.router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
