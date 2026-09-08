"""
Schema Change Sentinel for Fintech Data Pipelines
===================================================
Backend API server built with FastAPI.

Detects breaking schema changes in financial data pipelines,
analyzes downstream SQL dependencies, and enforces data contracts
with ALLOW / WARN / BLOCK publication decisions.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Schema Change Sentinel",
    description=(
        "Detects breaking schema changes in fintech data pipelines, "
        "analyzes downstream SQL impact, and enforces data contracts."
    ),
    version="0.1.0",
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint – confirms the backend is running."""
    return {"message": "Schema Change Sentinel Backend is running"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Health-check endpoint for monitoring and load balancers."""
    return {"status": "healthy"}
