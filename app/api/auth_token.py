"""
Token Authentication API
Handles JWT token exchange and validation for external integrations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.utils.jwt_auth import verify_firebase_token, create_bot_builder_token

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class TokenExchangeRequest(BaseModel):
    """Request to exchange Firebase token for Bot Builder token"""
    firebase_token: str = Field(..., description="Firebase ID token from AI Engagement Hub")
    course_id: Optional[str] = Field(None, description="Course ID for context")


class TokenExchangeResponse(BaseModel):
    """Response containing Bot Builder access token"""
    access_token: str = Field(..., description="Bot Builder JWT token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")


class TokenValidationResponse(BaseModel):
    """Response for token validation"""
    valid: bool = Field(..., description="Whether token is valid")
    user_id: Optional[str] = Field(None, description="User ID if token is valid")
    email: Optional[str] = Field(None, description="User email if token is valid")


@router.post("/token/exchange", response_model=TokenExchangeResponse)
async def exchange_firebase_token(request: TokenExchangeRequest):
    """
    Exchange a Firebase ID token for a Bot Builder JWT token

    This endpoint allows AI Engagement Hub to authenticate users with their
    Firebase credentials and receive a Bot Builder token for API access.

    Args:
        request: Token exchange request with Firebase token

    Returns:
        Bot Builder JWT token and user info

    Raises:
        HTTPException: If Firebase token is invalid
    """
    try:
        # Verify the Firebase token
        firebase_user = verify_firebase_token(request.firebase_token)

        # Extract user info
        user_id = firebase_user["user_id"]
        email = firebase_user["email"]

        # Create Bot Builder token
        additional_data = {}
        if request.course_id:
            additional_data["course_id"] = request.course_id

        bot_builder_token = create_bot_builder_token(
            user_id=user_id,
            user_email=email,
            additional_data=additional_data
        )

        # Calculate expiration (from config)
        from app.config import settings
        expires_in = settings.jwt_expiration_hours * 3600  # Convert to seconds

        return TokenExchangeResponse(
            access_token=bot_builder_token,
            token_type="Bearer",
            expires_in=expires_in,
            user_id=user_id,
            email=email
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token exchange failed: {str(e)}"
        )


@router.post("/token/validate", response_model=TokenValidationResponse)
async def validate_token(token: str):
    """
    Validate a Bot Builder JWT token

    Args:
        token: Bot Builder JWT token to validate

    Returns:
        Validation result with user info if valid
    """
    from app.utils.jwt_auth import verify_bot_builder_token

    try:
        payload = verify_bot_builder_token(token)

        return TokenValidationResponse(
            valid=True,
            user_id=payload.get("sub"),
            email=payload.get("email")
        )
    except HTTPException:
        return TokenValidationResponse(
            valid=False,
            user_id=None,
            email=None
        )


@router.get("/token/info")
async def get_token_info():
    """
    Get information about token authentication configuration

    Returns:
        Configuration and capabilities info
    """
    from app.config import settings

    return {
        "firebase_configured": bool(settings.firebase_project_id),
        "firebase_project_id": settings.firebase_project_id,
        "jwt_algorithm": settings.jwt_algorithm,
        "jwt_expiration_hours": settings.jwt_expiration_hours,
        "endpoints": {
            "exchange": "/api/auth/token/exchange",
            "validate": "/api/auth/token/validate",
            "info": "/api/auth/token/info"
        }
    }
