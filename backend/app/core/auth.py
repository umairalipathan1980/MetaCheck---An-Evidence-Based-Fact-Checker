"""
Authentication utilities for admin access control.

Provides session-based authentication with HTTP-only cookies for admin users.
"""

from fastapi import Cookie, HTTPException, status
from typing import Optional
import secrets

SESSION_COOKIE_NAME = "metacheck_admin_session"
SESSION_EXPIRY_HOURS = 24

# In-memory session store (token -> {"username": str, "role": str})
# Note: Sessions reset on server restart
active_sessions = {}


def create_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)


async def require_admin(
    session: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
) -> None:
    """
    FastAPI dependency that verifies admin session.

    Raises HTTPException with 403 status if session is invalid or missing.
    """
    session_data = active_sessions.get(session) if session else None
    if not session_data or session_data.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def verify_admin_credentials(username: str, password: str) -> bool:
    """
    Verify admin credentials against environment variables.

    Args:
        username: Username to verify
        password: Password to verify

    Returns:
        True if credentials match environment settings, False otherwise
    """
    from app.core.settings import get_settings

    settings = get_settings()
    return username == settings.admin_username and password == settings.admin_password


def verify_user_credentials(username: str, password: str) -> bool:
    """Verify main user credentials from environment variables."""
    from app.core.settings import get_settings

    settings = get_settings()
    return username == settings.user_username and password == settings.user_password


def verify_credentials(username: str, password: str) -> bool:
    """
    Backward-compatible credential check.
    Returns True for either admin or user credentials.
    """
    return verify_admin_credentials(username, password) or verify_user_credentials(username, password)
