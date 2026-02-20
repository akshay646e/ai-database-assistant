from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import load_environment

from api.routes_chat import router as chat_router
from api.routes_upload import router as upload_router
from api.routes_visualize import router as visualize_router

# Load environment variables
load_environment()

app = FastAPI(title="BAAP AI - Database Analytics", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "BAAP AI Backend (v2) is running ✓"}

# Register modular routers
app.include_router(chat_router, prefix="/api", tags=["Chat & Query"])
app.include_router(upload_router, prefix="/api", tags=["Upload & Connect"])
app.include_router(visualize_router, prefix="/api", tags=["Schema & Config"])

