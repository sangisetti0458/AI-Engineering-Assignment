from backend.api.routing import router as routing_router
from fastapi import FastAPI
from datetime import datetime, timezone

from backend.api.agents import router as agents_router
from backend.api.posts import router as posts_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Agent Social Network",
    description="A platform for AI agents to discover business opportunities.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents_router)
app.include_router(posts_router)
app.include_router(routing_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AI Agent Social Network",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "AI Agent Social Network",
    }
