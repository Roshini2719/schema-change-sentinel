from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.connection import init_db
from .routers import auth, schemas, contracts, dependencies, validation, dashboard, experiments, demo

app = FastAPI(
    title="🛡️ Schema Sentinel API",
    description="Detecting Breaking Schema Changes Before Unsafe Data Publication",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth.router)
app.include_router(schemas.router)
app.include_router(contracts.router)
app.include_router(dependencies.router)
app.include_router(validation.router)
app.include_router(dashboard.router)
app.include_router(experiments.router)
app.include_router(demo.router)

@app.get("/")
def read_root():
    return {
        "status": "ONLINE",
        "system": "Schema Sentinel Engine",
        "docs_url": "/docs"
    }
