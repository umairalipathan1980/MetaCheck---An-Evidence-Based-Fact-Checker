"""
Authentication API routes for admin login/logout.
"""

from fastapi import APIRouter, HTTPException, Response, Cookie, status
from pydantic import BaseModel
from typing import Optional

from app.core.auth import (
    verify_admin_credentials,
    verify_user_credentials,
    create_session_token,
    SESSION_COOKIE_NAME,
    SESSION_EXPIRY_HOURS,
    active_sessions,
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Request model for login endpoint."""
    username: str
    password: str


class AuthStatusResponse(BaseModel):
    """Response model for auth status endpoint."""
    authenticated: bool
    username: Optional[str] = None
    role: Optional[str] = None


@router.post("/login")
async def login(request: LoginRequest, response: Response):
    """
    Authenticate admin and set session cookie.

    Args:
        request: Login credentials
        response: FastAPI response object for setting cookies

    Returns:
        Success message with username

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    role = None
    if verify_admin_credentials(request.username, request.password):
        role = "admin"
    elif verify_user_credentials(request.username, request.password):
        role = "user"
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create session
    token = create_session_token()
    active_sessions[token] = {"username": request.username, "role": role}

    # Set HTTP-only cookie (24h expiry)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=SESSION_EXPIRY_HOURS * 3600,
        samesite="lax"
    )

    return {"message": "Login successful", "username": request.username, "role": role}


@router.post("/admin/login")
async def admin_login(request: LoginRequest, response: Response):
    """Authenticate admin only and set session cookie."""
    if not verify_admin_credentials(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )

    token = create_session_token()
    active_sessions[token] = {"username": request.username, "role": "admin"}

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=SESSION_EXPIRY_HOURS * 3600,
        samesite="lax"
    )

    return {"message": "Admin login successful", "username": request.username, "role": "admin"}


@router.post("/logout")
async def logout(
    response: Response,
    session: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """
    Clear session cookie and invalidate session.

    Args:
        response: FastAPI response object for clearing cookies
        session: Current session token from cookie

    Returns:
        Success message
    """
    if session and session in active_sessions:
        del active_sessions[session]

    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return {"message": "Logout successful"}


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status(
    session: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """
    Check current authentication status.

    Args:
        session: Current session token from cookie

    Returns:
        Authentication status with username if authenticated
    """
    if session and session in active_sessions:
        session_data = active_sessions[session]
        return {
            "authenticated": True,
            "username": session_data.get("username"),
            "role": session_data.get("role"),
        }
    return {"authenticated": False, "username": None, "role": None}
