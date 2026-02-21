import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import load_environment

from api.routes_chat import router as chat_router
from api.routes_upload import router as upload_router
from api.routes_visualize import router as visualize_router

# Load environment variables first
load_environment()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")


# ── Lifespan: startup & shutdown ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — warm up RAG engine on startup."""
    logger.info("BAAP AI v2 starting up…")
    try:
        import rag.rag_engine as rag_engine
        rag_engine.startup()
        logger.info("RAG engine initialised.")
    except Exception as e:
        logger.warning("RAG engine startup skipped (will retry on first use): %s", e)
    yield
    logger.info("BAAP AI v2 shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="BAAP AI – Database & Document Analytics",
    version="2.0.0",
    description="Hybrid Conversational + RAG-powered Business Intelligence Assistant",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "BAAP AI Backend (v2) is running ✓"}


@app.get("/health")
def health():
    """Health check + RAG store stats."""
    try:
        from rag.vector_store import get_store_stats
        rag_stats = get_store_stats()
    except Exception:
        rag_stats = {"status": "unavailable"}
    return {"status": "ok", "version": "2.0.0", "rag": rag_stats}


# Register modular routers
app.include_router(chat_router, prefix="/api", tags=["Chat & Query"])
app.include_router(upload_router, prefix="/api", tags=["Upload & Connect"])
app.include_router(visualize_router, prefix="/api", tags=["Schema & Config"])
