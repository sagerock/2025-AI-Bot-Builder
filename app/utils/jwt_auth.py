"""
JWT Token Authentication Utilities
Supports both Firebase token validation and Bot Builder JWT tokens
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Header
from app.config import settings

# Initialize Firebase Admin SDK (lazy load)
_firebase_app = None


def get_firebase_app():
    """Initialize Firebase Admin SDK if configured"""
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    if not settings.firebase_project_id:
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        # Check if already initialized
        try:
            _firebase_app = firebase_admin.get_app()
            return _firebase_app
        except ValueError:
            pass

        # Initialize with credentials if provided
        if settings.firebase_credentials_path:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            _firebase_app = firebase_admin.initialize_app(cred)
        else:
            # Initialize without credentials (for testing)
            _firebase_app = firebase_admin.initialize_app(options={
                'projectId': settings.firebase_project_id
            })

        return _firebase_app
    except Exception as e:
        print(f"Warning: Could not initialize Firebase Admin SDK: {e}")
        return None


def create_bot_builder_token(user_id: str, user_email: str, additional_data: Dict = None) -> str:
    """
    Create a Bot Builder JWT token

    Args:
        user_id: User ID from external system (e.g., Firebase UID)
        user_email: User's email address
        additional_data: Optional additional data to include in token

    Returns:
        JWT token string
    """
    payload = {
        "sub": user_id,
        "email": user_email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours),
        "iss": "bot-builder"
    }

    if additional_data:
        payload.update(additional_data)

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


def verify_bot_builder_token(token: str) -> Dict:
    """
    Verify a Bot Builder JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": True, "verify_iat": True}
        )

        # Verify issuer
        if payload.get("iss") != "bot-builder":
            raise HTTPException(status_code=401, detail="Invalid token issuer")

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def verify_firebase_token(firebase_token: str) -> Dict:
    """
    Verify a Firebase ID token from AI Engagement Hub

    Args:
        firebase_token: Firebase ID token string

    Returns:
        Decoded token payload with user info

    Raises:
        HTTPException: If token is invalid or Firebase is not configured
    """
    firebase_app = get_firebase_app()

    if not firebase_app:
        raise HTTPException(
            status_code=503,
            detail="Firebase authentication not configured"
        )

    try:
        from firebase_admin import auth

        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(firebase_token)

        return {
            "user_id": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False),
            "name": decoded_token.get("name"),
            "firebase_token": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Firebase token: {str(e)}"
        )


async def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> Optional[Dict]:
    """
    Extract and verify JWT token from Authorization header
    Supports both "Bearer <token>" and plain token formats

    Args:
        authorization: Authorization header value

    Returns:
        User info from token or None if no token provided

    Raises:
        HTTPException: If token is provided but invalid
    """
    if not authorization:
        return None

    # Handle "Bearer <token>" format
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    # Try to verify as Bot Builder token first
    try:
        return verify_bot_builder_token(token)
    except HTTPException:
        pass

    # Try to verify as Firebase token
    try:
        firebase_data = verify_firebase_token(token)
        # Create a Bot Builder token for future requests
        return firebase_data
    except HTTPException:
        pass

    # If both fail, raise error
    raise HTTPException(
        status_code=401,
        detail="Invalid or expired token"
    )


def require_token_auth(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Dependency that requires valid token authentication

    Args:
        authorization: Authorization header value

    Returns:
        User info from token

    Raises:
        HTTPException: If no token or invalid token
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid token."
        )

    user = get_current_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    return user
