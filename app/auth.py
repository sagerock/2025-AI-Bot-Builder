"""
Simple authentication for the AI Bot Builder
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
import secrets
from typing import Optional

# Simple hardcoded credentials (for single user)
USERNAME = "sagelewis"
PASSWORD = "SageLewis1971"

# Store active sessions (username -> session_token)
sessions = {}

def generate_session_token() -> str:
    """Generate a secure random session token"""
    return secrets.token_urlsafe(32)

def create_session(username: str) -> str:
    """Create a new session for a user"""
    token = generate_session_token()
    sessions[token] = username
    return token

def get_session_username(token: str) -> Optional[str]:
    """Get username from session token"""
    return sessions.get(token)

def delete_session(token: str):
    """Delete a session"""
    if token in sessions:
        del sessions[token]

def verify_credentials(username: str, password: str) -> bool:
    """Verify username and password"""
    return username == USERNAME and password == PASSWORD

def get_session_token(request: Request) -> Optional[str]:
    """Get session token from cookie"""
    return request.cookies.get("session_token")

def require_auth(request: Request) -> str:
    """
    Require authentication for a route.
    Returns username if authenticated, raises HTTPException otherwise.
    """
    token = get_session_token(request)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    username = get_session_username(token)

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )

    return username

def is_authenticated(request: Request) -> bool:
    """Check if request is authenticated (doesn't raise exception)"""
    token = get_session_token(request)
    if not token:
        return False
    return get_session_username(token) is not None
