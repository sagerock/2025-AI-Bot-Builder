from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api import bots, chat, api_keys
import os

# Initialize FastAPI app
app = FastAPI(
    title="AI Bot Builder Platform",
    description="Create and deploy AI chatbots with ease",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bots.router)
app.include_router(chat.router)
app.include_router(api_keys.router)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")
    print(f"🚀 Server running at {settings.api_base_url}")
    print(f"📚 API Docs: {settings.api_base_url}/docs")
    print(f"🎨 Admin Dashboard: {settings.api_base_url}/admin")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Bot Builder Platform API",
        "docs": "/docs",
        "admin": "/admin"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    favicon_path = os.path.join(static_dir, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return {"status": "not found"}


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Serve admin dashboard"""
    admin_file = os.path.join(static_dir, "admin.html")
    if os.path.exists(admin_file):
        return FileResponse(admin_file)
    return HTMLResponse(content="<h1>Admin dashboard not found. Please create static/admin.html</h1>")


@app.get("/chat/{bot_id}", response_class=HTMLResponse)
async def chat_interface(bot_id: str):
    """Serve standalone chat interface"""
    chat_file = os.path.join(static_dir, "chat.html")
    if os.path.exists(chat_file):
        return FileResponse(chat_file)
    return HTMLResponse(content="<h1>Chat interface not found. Please create static/chat.html</h1>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
