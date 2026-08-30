from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.api.papers import router as paper_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.include_router(paper_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to PaperMind API",
        "version": settings.APP_VERSION
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }