from fastapi import FastAPI, Request, Depends, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.config import settings
from app.database import init_db
from app.api import bots, chat, api_keys, qdrant, documents
from app import auth
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
app.include_router(qdrant.router)
app.include_router(documents.router)

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


# Auth models
class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve login page"""
    login_file = os.path.join(static_dir, "login.html")
    if os.path.exists(login_file):
        return FileResponse(login_file)
    return HTMLResponse(content="<h1>Login page not found</h1>")


@app.post("/auth/login")
async def login(request: LoginRequest, response: Response):
    """Handle login"""
    if auth.verify_credentials(request.username, request.password):
        # Create session
        token = auth.create_session(request.username)

        # Set session cookie
        response = JSONResponse(content={"success": True, "username": request.username})
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            max_age=7 * 24 * 60 * 60,  # 7 days
            samesite="lax"
        )
        return response
    else:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid username or password"}
        )


@app.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Handle logout"""
    token = auth.get_session_token(request)
    if token:
        auth.delete_session(token)

    response = JSONResponse(content={"success": True})
    response.delete_cookie("session_token")
    return response


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Serve admin dashboard (requires authentication)"""
    # Check if authenticated
    if not auth.is_authenticated(request):
        return RedirectResponse(url="/login?redirect=/admin", status_code=302)

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
