"""
FastAPI application entry point.

Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.api.routes import qa, search, ingest

app = FastAPI(
    title="AI Research Paper Explorer",
    description="Semantic search, recommendation, and RAG-based QA over arXiv papers.",
    version="0.1.0",
)

app.include_router(search.router)
app.include_router(qa.router)
app.include_router(ingest.router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}