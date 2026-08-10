"""ProjectForge AI — FastAPI Application Entry Point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core import settings
from backend.app.core.database import init_db
from backend.app.api.auth import router as auth_router
from backend.app.api.projects import router as projects_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info("ProjectForge AI Backend starting up...")

    # Initialize database tables
    init_db()
    logger.info("Database initialized.")

    # Check configuration
    if not settings.has_any_llm_key():
        logger.warning(
            "⚠️  No LLM API key configured. "
            "Set GEMINI_API_KEY, GROQ_API_KEY, or OPENROUTER_API_KEY in .env"
        )
    if not settings.TAVILY_API_KEY:
        logger.info(
            "ℹ️  Tavily API key not set. Web search will be unavailable."
        )

    yield

    logger.info("ProjectForge AI Backend shutting down.")


# Create FastAPI app
app = FastAPI(
    title="ProjectForge AI",
    description="Multi-Agent Project Architecture & Planning Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware — allow local and deployed frontend origins
allowed_origins = [
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
import os
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))
if os.getenv("VITE_BACKEND_URL"):
    allowed_origins.append(os.getenv("VITE_BACKEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(projects_router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "name": "ProjectForge AI",
        "version": "1.0.0",
        "status": "running",
        "llm_configured": settings.has_any_llm_key(),
        "tavily_configured": bool(settings.TAVILY_API_KEY),
    }


@app.get("/api/health")
def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "llm_providers": {
            "gemini": bool(settings.GEMINI_API_KEY),
            "groq": bool(settings.GROQ_API_KEY),
            "openrouter": bool(settings.OPENROUTER_API_KEY),
        },
        "tavily": bool(settings.TAVILY_API_KEY),
        "database": settings.DATABASE_URL.split("://")[0] if "://" in settings.DATABASE_URL else "unknown",
    }
