"""
FastAPI application entry point.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.models import Base, engine, SessionLocal
from .routers import auth, schemas, validate, audit, admin, demo, dashboard, experiments, contracts, dependencies, validation
from .api import partners as api_partners, data_sources as api_data_sources
from .services.seed_service import seed_database
from .core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Schema Change Sentinel",
    description="Detect breaking upstream schema changes and block unsafe data publication.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow React dev server and any localhost port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(schemas.router)
app.include_router(validate.router)
app.include_router(audit.router)
app.include_router(admin.router)
app.include_router(demo.router)
app.include_router(dashboard.router)
app.include_router(experiments.router)
app.include_router(contracts.router)
app.include_router(dependencies.router)
app.include_router(validation.router)
app.include_router(api_partners.router)
app.include_router(api_data_sources.router)

@app.on_event("startup")
def startup():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    if settings.DEMO_MODE:
        logger.info("DEMO_MODE enabled — seeding database...")
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
    logger.info("Schema Change Sentinel started.")

@app.get("/health")
def health():
    return {"status": "ok", "service": "schema-change-sentinel", "version": "1.0.0"}

@app.get("/")
def root():
    return {"message": "Schema Change Sentinel API", "docs": "/docs", "status": "ONLINE"}
